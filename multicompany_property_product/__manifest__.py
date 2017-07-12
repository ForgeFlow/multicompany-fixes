# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Product',
    'version': '1',
    'summary': 'Creu Blanca configuration',
    'author': 'Creu Blanca',
    'sequence': 30,
    'description': "",
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
    'depends': ['product', 'multicompany_property'],
    'data': [
        'views/product_views.xml',
        'views/product_category_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
