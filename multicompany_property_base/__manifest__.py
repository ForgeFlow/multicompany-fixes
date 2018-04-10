# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Multi Company Property Base',
    'version': '11.0.1.0.0',
    'summary': 'Base Company Properties',
    'author': 'Creu Blanca, '
              'Eficent, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'sequence': 30,
    'website': 'https://github.com/OCA/multi-company',
    'depends': ['base'],
    'data': [
        'views/partner_views.xml',
        'views/res_company_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
