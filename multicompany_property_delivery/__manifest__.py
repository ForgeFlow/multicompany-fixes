# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Multi Company Delivery',
    'version': '11.0.1.0.0',
    'summary': 'Delivery Company Properties',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'sequence': 30,
    'license': 'LGPL-3',
    'website': 'http://www.eficent.com',
    'depends': ['delivery', 'multicompany_property_stock_account'],
    'data': [
        'views/partner.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
