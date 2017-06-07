# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Accounting',
    'version': '1',
    'summary': 'Creu Blanca configuration',
    'author': 'Creu Blanca',
    'sequence': 30,
    'description': "",
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
    'depends': ['account', 'payment', 'mcfix_product'],
    'data': [
        'views/account_move.xml',
        'views/account_invoice.xml',
        'views/account_budget_views.xml',
        'views/account_tax.xml',
        'views/account_payment.xml',
        'views/product.xml',
        'views/partner.xml',
        'views/product_category.xml',
        'wizard/wizard_tax_adjustments_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
