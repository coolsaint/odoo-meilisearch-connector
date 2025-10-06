{
    'name': 'MeiliSearch Connector v12',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'summary': 'Connector to sync Odoo 12 with MeiliSearch Cloud',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'data/ir_config_parameter_data.xml',
        'data/server_actions.xml',
    ],
    'installable': True,
    'application': False,
}
