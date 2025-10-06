from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

class MeiliDocumentMixin(models.AbstractModel):
    _name = 'meili.document.mixin'
    _description = "Mixin to enable Meili indexing"

    @api.model
    def _get_index_uid(self):
        """Override to define index UID for this model, e.g. 'submissions' or 'scan_lines'."""
        return self._name

    @api.multi
    def _prepare_index_document(self):
        """Override to return list of dicts for indexing."""
        docs = []
        for rec in self:
            docs.append({
                'id': str(rec.id),  # MeiliSearch 0.11.2 requires string IDs
            })
        return docs

    @api.multi
    def meili_index(self):
        """Index documents in MeiliSearch.
        
        Uses direct HTTP requests for better cloud compatibility.
        """
        import requests
        import json
        
        try:
            host = self.env['ir.config_parameter'].sudo().get_param('meili.host')
            key = self.env['ir.config_parameter'].sudo().get_param('meili.admin_key')
            
            if not host or not key:
                _logger.warning("MeiliSearch not configured, skipping indexing")
                return False
            
            index_uid = self._get_index_uid()
            docs = self._prepare_index_document()
            
            if not docs:
                return True
            
            # Use requests directly for better compatibility
            headers = {
                'Authorization': 'Bearer ' + key,
                'Content-Type': 'application/json'
            }
            
            # Try to create index if it doesn't exist (will fail silently if exists)
            try:
                create_url = host + '/indexes'
                requests.post(create_url, headers=headers, 
                            json={'uid': index_uid, 'primaryKey': 'id'}, 
                            timeout=5)
            except:
                pass  # Index might already exist
            
            # Add documents
            add_url = host + '/indexes/' + index_uid + '/documents'
            response = requests.post(add_url, headers=headers, 
                                    json=docs, timeout=30)
            
            if response.status_code in [200, 201, 202]:
                _logger.info("MeiliSearch: Indexed %d documents to '%s'", len(docs), index_uid)
                return True
            else:
                _logger.error("MeiliSearch indexing failed: Status %s - %s", 
                            response.status_code, response.text)
                return False
                
        except Exception as e:
            _logger.error("Failed to index documents in MeiliSearch: %s", str(e))
            # Don't raise error to avoid breaking main operations
            return False

    @api.multi
    def meili_delete(self):
        """Delete documents from MeiliSearch.
        
        Uses direct HTTP requests for better cloud compatibility.
        """
        import requests
        import json
        
        try:
            host = self.env['ir.config_parameter'].sudo().get_param('meili.host')
            key = self.env['ir.config_parameter'].sudo().get_param('meili.admin_key')
            
            if not host or not key:
                return False
            
            index_uid = self._get_index_uid()
            ids = [str(r.id) for r in self]
            
            if not ids:
                return True
            
            # Use requests directly
            headers = {
                'Authorization': 'Bearer ' + key,
                'Content-Type': 'application/json'
            }
            
            delete_url = host + '/indexes/' + index_uid + '/documents/delete-batch'
            response = requests.post(delete_url, headers=headers, 
                                    json=ids, timeout=10)
            
            if response.status_code in [200, 201, 202]:
                _logger.info("MeiliSearch: Deleted %d documents from '%s'", len(ids), index_uid)
                return True
            else:
                _logger.warning("MeiliSearch deletion warning: Status %s", response.status_code)
                return False
                
        except Exception as e:
            _logger.error("Failed to delete documents from MeiliSearch: %s", str(e))
            return False
