from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    meili_host = fields.Char(
        string='MeiliSearch Host',
        config_parameter='meili.host',
        help='MeiliSearch server URL (e.g., http://localhost:7700)'
    )
    meili_admin_key = fields.Char(
        string='MeiliSearch Admin Key',
        config_parameter='meili.admin_key',
        help='Your MeiliSearch admin API key'
    )

