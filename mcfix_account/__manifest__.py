# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Accounting',
    'version': '9.0.1.0.0',
    'summary': 'Fixes ',
    'author': 'Creu Blanca,'
              'Eficent,'
              'Odoo Community Association (OCA)',
    'sequence': 30,
    'description': "",
    'category': 'Multicompany',
    'website': 'http://www.creublanca.es',
    'depends': ['account', 'payment', 'mcfix_product'],
    'data': [
        'security/account_security.xml',
        'views/account_move_view.xml',
        'views/account_invoice_view.xml',
        'views/account_tax_view.xml',
        'views/account_payment_view.xml',
        'views/product_template_view.xml',
        'views/res_partner_view.xml',
        'views/product_category_view.xml',
        'wizard/wizard_tax_adjustments_views.xml',
        'views/account_payment_term_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
