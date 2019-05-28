# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Sale Stock',
    'version': '12.0.1.0.0',
    'summary': 'Sale Stock fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['sale_stock', 'mcfix_stock_account', 'mcfix_sale'],
    'data': [
        'views/sale_views.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
