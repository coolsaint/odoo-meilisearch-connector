from odoo import models, _
import logging

_logger = logging.getLogger(__name__)

class MeiliClient(models.AbstractModel):
    _name = 'meili.client'
    _description = "MeiliSearch Client Wrapper"

    def test_connection(self):
        """Test MeiliSearch connection.
        
        Uses direct HTTP requests for compatibility.
        
        Returns:
            bool: True if connection successful
            
        Raises:
            ValueError: If host or key not configured or connection fails
        """
        import requests
        
        host = self.env['ir.config_parameter'].sudo().get_param('meili.host')
        key = self.env['ir.config_parameter'].sudo().get_param('meili.admin_key')
        
        if not host or not key:
            raise ValueError(_("MeiliSearch host or admin key not configured in System Settings"))
            
        try:
            # Test connection with direct request
            headers = {'Authorization': 'Bearer ' + key}
            test_response = requests.get(host + '/health', headers=headers, timeout=10)
            
            if test_response.status_code == 200:
                _logger.info("MeiliSearch connection successful: %s", host)
                return True
            else:
                raise ValueError(_("MeiliSearch connection failed. Status: %s") % test_response.status_code)
            
        except Exception as e:
            import traceback
            _logger.error("Failed to connect to MeiliSearch at %s: %s\n%s", host, str(e), traceback.format_exc())
            raise ValueError(_("Could not connect to MeiliSearch server at %s. Error: %s") % (host, str(e)))
