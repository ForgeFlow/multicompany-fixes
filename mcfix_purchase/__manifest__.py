# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Purchase',
    'version': '12.0.1.0.0',
    'summary': 'Purchase fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['purchase_stock', 'mcfix_stock_account', 'uom'],
    'data': [
        'views/purchase_views.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
