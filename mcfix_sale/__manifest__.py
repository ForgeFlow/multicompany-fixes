# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Sale',
    'version': '11.0.1.0.0',
    'summary': 'Sale fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['sale', 'mcfix_sales_team', 'mcfix_account'],
    'data': [
        'views/sale_views.xml',
        'wizard/sale_make_invoice_advance_views.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
