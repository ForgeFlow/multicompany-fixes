# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Stock Account',
    'version': '13.0.1.0.0',
    'summary': 'Stock Account fixes',
    'author': 'ForgeFlow, Odoo Community Association (OCA)',
    'website': 'http://www.forgeflow.com',
    'license': 'LGPL-3',
    'depends': ['stock_account', 'mcfix_stock', 'mcfix_account'],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
