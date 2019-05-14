# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Multi Company Fix Analytic',
    'version': '12.0.1.0.0',
    'summary': 'Analytic fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/multi-company',
    'license': 'LGPL-3',
    'depends': ['analytic', 'mcfix_base'],
    'data': [
        'views/analytic_account_views.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
