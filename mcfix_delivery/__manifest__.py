# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Delivery',
    'version': '11.0.1.0.0',
    'summary': 'Delivery fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['mcfix_sale_stock', 'mcfix_stock', 'delivery'],
    'data': [
        'views/sale_views.xml',
        'views/stock_picking_views.xml',
    ],
    'demo': [
        'data/delivery_demo.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
