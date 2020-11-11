# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Stock',
    'version': '12.0.1.0.0',
    'summary': 'Stock fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'mcfix_product'],
    'data': [
        'views/stock_inventory_views.xml',
        'views/stock_location_views.xml',
        'views/stock_move_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_scrap_views.xml',
        'views/stock_warehouse_views.xml',
    ],
    'demo': [
        'data/stock_demo.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
    'pre_init_hook': 'pre_init_hook',
}
