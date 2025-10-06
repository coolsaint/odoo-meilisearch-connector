from odoo import models, _
import logging

_logger = logging.getLogger(__name__)

class MeiliClient(models.AbstractModel):
    _name = 'meili.client'
    _description = "MeiliSearch Client Wrapper"

    def get_client(self):
        """Get MeiliSearch client instance.
        
        Uses late import to avoid conflicts with Odoo's calendar module.
        
        Returns:
            meilisearch.Client: Configured MeiliSearch client
            
        Raises:
            ValueError: If host or key not configured or meilisearch not installed
        """
        # Late import to avoid Python path conflicts
        try:
            import meilisearch
        except ImportError as e:
            _logger.error("MeiliSearch Python package not installed: %s", str(e))
            raise ValueError(_("MeiliSearch Python package is not installed. Please install it with: pip install meilisearch==0.11.2"))
        except Exception as e:
            _logger.error("Failed to import meilisearch: %s", str(e))
            raise ValueError(_("Failed to import meilisearch module: %s") % str(e))
            
        host = self.env['ir.config_parameter'].sudo().get_param('meili.host')
        key = self.env['ir.config_parameter'].sudo().get_param('meili.admin_key')
        if not host or not key:
            raise ValueError(_("Meili host or admin key not configured in System Settings"))
            
        try:
            # For meilisearch 0.11.2, try using requests directly to work around cloud API issues
            import requests
            
            # Test connection first with direct request
            headers = {'Authorization': 'Bearer ' + key}
            test_response = requests.get(host + '/indexes', headers=headers, timeout=10)
            
            if test_response.status_code == 401:
                # Try with X-Meili-API-Key header instead
                headers = {'X-Meili-API-Key': key}
                test_response = requests.get(host + '/indexes', headers=headers, timeout=10)
                
                if test_response.status_code != 200:
                    raise ValueError(_("Authentication failed. Please check your API key. Status: %s") % test_response.status_code)
            
            # Create client - meilisearch 0.11.2 uses the key as api_key parameter
            client = meilisearch.Client(host, key)
            
            # Override the headers if needed for cloud compatibility
            if hasattr(client, 'config') and hasattr(client.config, 'headers'):
                client.config.headers = {'X-Meili-API-Key': key}
            
            return client
            
        except Exception as e:
            import traceback
            _logger.error("Failed to connect to MeiliSearch at %s: %s\n%s", host, str(e), traceback.format_exc())
            raise ValueError(_("Could not connect to MeiliSearch server at %s. Error: %s. Please check your configuration and ensure the server is running.") % (host, str(e)))
