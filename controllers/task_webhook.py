from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class MeiliTaskWebhookController(http.Controller):
    @http.route('/meili/task-webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook(self, **kw):
        _logger.info("Meili task webhook called: %s", kw)
        # Optionally, you can parse kw["taskUid"], kw["indexUid"], kw["status"], etc.
        return {'ok': True}
