from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = ['stock.production.lot', 'meili.document.mixin']

    @api.model
    def _get_index_uid(self):
        return 'lots'

    @api.multi
    def _prepare_index_document(self):
        """Prepare lot data for MeiliSearch indexing."""
        import re
        
        docs = []
        for rec in self:
            # Get product SKU (default_code)
            sku = rec.product_id.default_code or ''
            lot_name = rec.name or ''
            
            # Extract just the numbers from lot name for better number search
            lot_numbers = re.sub(r'[^0-9]', ' ', lot_name).strip()
            
            docs.append({
                'id': str(rec.id),
                'lot_id': str(rec.id),
                'lot_name': lot_name,
                'lot_numbers': lot_numbers,  # Just the numbers for number-only search
                'product_id': str(rec.product_id.id) if rec.product_id else '',
                'product_name': rec.product_id.name if rec.product_id else '',
                'sku': sku
            })
        return docs

    @api.model
    def create(self, vals):
        rec = super(StockProductionLot, self).create(vals)
        try:
            rec.meili_index()
        except Exception as e:
            _logger.error("Failed to index new lot in MeiliSearch: %s", str(e))
        return rec

    @api.multi
    def write(self, vals):
        res = super(StockProductionLot, self).write(vals)
        try:
            self.meili_index()
        except Exception as e:
            _logger.error("Failed to update lot in MeiliSearch: %s", str(e))
        return res

    @api.multi
    def unlink(self):
        try:
            self.meili_delete()
        except Exception as e:
            _logger.error("Failed to delete lot from MeiliSearch: %s", str(e))
        return super(StockProductionLot, self).unlink()

    @api.model
    def _configure_meili_index(self):
        """Configure MeiliSearch index settings for optimal lot searching.
        
        Sets searchable attributes priority and ranking rules.
        """
        import requests
        import json
        
        try:
            host = self.env['ir.config_parameter'].sudo().get_param('meili.host')
            key = self.env['ir.config_parameter'].sudo().get_param('meili.admin_key')
            
            if not host or not key:
                return False
            
            headers = {
                'Authorization': 'Bearer ' + key,
                'Content-Type': 'application/json'
            }
            
            # Configure index settings
            settings_url = host + '/indexes/lots/settings'
            settings = {
                'searchableAttributes': [
                    'lot_name',       # Highest priority - full lot name
                    'lot_numbers',    # Second priority - just numbers from lot name
                    'sku',            # Third priority
                    'product_name'    # Fourth priority
                ],
                'rankingRules': [
                    'words',
                    'typo',
                    'proximity',
                    'attribute',  # This makes the searchableAttributes order matter
                    'sort',
                    'exactness'
                ],
                'displayedAttributes': ['*'],
                'filterableAttributes': ['product_id', 'lot_id'],
                'separatorTokens': ['-', '_', '/', '\\', '.', ' '],  # Split on these characters
                'nonSeparatorTokens': [],  # Keep numbers together
                'disableTypo': False,  # Allow typo tolerance
                'minWordSizeForTypos': {
                    'oneTypo': 4,
                    'twoTypos': 8
                }
            }
            
            response = requests.patch(settings_url, headers=headers, 
                                     json=settings, timeout=10)
            
            if response.status_code in [200, 202]:
                _logger.info("MeiliSearch index settings configured successfully")
                return True
            else:
                _logger.warning("Failed to configure MeiliSearch settings: %s", response.text)
                return False
                
        except Exception as e:
            _logger.error("Error configuring MeiliSearch index: %s", str(e))
            return False

    @api.model
    def action_bulk_index_all_lots(self):
        """Bulk index all existing lots to MeiliSearch.
        
        This method can be called from a button or server action to index
        all existing lots in the database.
        """
        import time
        
        _logger.info("Starting bulk indexing of all lots to MeiliSearch...")
        
        # Configure index settings first
        self._configure_meili_index()
        
        # Get all lots
        all_lots = self.search([])
        total = len(all_lots)
        
        if total == 0:
            _logger.info("No lots found to index.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'MeiliSearch Bulk Index',
                    'message': 'No lots found to index.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        _logger.info("Found %d lots to index", total)
        
        # Index in batches with delay to avoid rate limiting
        batch_size = 500  # Larger batch size since we're batching on MeiliSearch side
        indexed = 0
        failed = 0
        delay = 0.5  # 500ms delay between batches to avoid overwhelming MeiliSearch
        
        for i in range(0, total, batch_size):
            batch = all_lots[i:i+batch_size]
            try:
                batch.meili_index()
                indexed += len(batch)
                _logger.info("Indexed batch %d-%d of %d lots (%.1f%% complete)", 
                           i+1, min(i+batch_size, total), total, 
                           (min(i+batch_size, total) / float(total)) * 100)
                
                # Add delay between batches to avoid rate limiting
                if i + batch_size < total:  # Don't delay after last batch
                    time.sleep(delay)
                    
            except Exception as e:
                failed += len(batch)
                _logger.error("Failed to index batch %d-%d: %s", i+1, min(i+batch_size, total), str(e))
                # Continue with next batch even if this one failed
        
        message = "Successfully indexed %d lots to MeiliSearch." % indexed
        if failed > 0:
            message += " Failed to index %d lots (check logs for details)." % failed
        
        _logger.info("Bulk indexing completed: %d indexed, %d failed out of %d total", indexed, failed, total)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'MeiliSearch Bulk Index Complete',
                'message': message,
                'type': 'success' if failed == 0 else 'warning',
                'sticky': True,
            }
        }
