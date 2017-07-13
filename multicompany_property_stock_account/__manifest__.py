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
    'depends': ['multicompany_property_account',
                'multicompany_property_stock'],
    'data': [
        'views/product.xml',
        'views/product_category.xml',
        'views/res_company_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
