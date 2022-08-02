# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Multi Company Stock',
    'version': '11.0.1.0.0',
    'summary': 'Stock Company Properties',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'sequence': 30,
    'license': 'LGPL-3',
    'website': 'http://www.eficent.com',
    'depends': ['stock', 'multicompany_property_product'],
    'data': [
        'views/product.xml',
        'views/partner.xml',
        'views/stock_warehouse.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
