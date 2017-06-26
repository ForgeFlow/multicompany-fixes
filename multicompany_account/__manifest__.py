# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Accounting',
    'version': '1',
    'summary': 'Creu Blanca configuration',
    'author': 'Creu Blanca',
    'sequence': 30,
    'description': "",
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
    'depends': ['account', 'multicompany', 'multicompany_product', 'payment'],
    'data': [
        'views/partner.xml',
        'views/product.xml',
        'views/product_category.xml',
        'views/company.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
