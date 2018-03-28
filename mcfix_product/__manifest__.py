# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Product',
    'version': '11.0.1.0.0',
    'summary': 'Product fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['product', 'mcfix_mail'],
    'demo': [
        'data/product_demo.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
