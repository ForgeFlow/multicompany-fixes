# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Web',
    'version': '12.0.1.0.0',
    'summary': 'Web fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['web', 'mcfix_base'],
    'data': [
        'views/report_templates.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
