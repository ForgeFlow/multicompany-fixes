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
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/stock_warehouse_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
