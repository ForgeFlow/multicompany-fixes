# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Stock',
    'version': '1',
    'summary': 'Creu Blanca configuration',
    'author': 'Creu Blanca',
    'sequence': 30,
    'description': "",
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
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
