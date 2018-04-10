# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Multi Company Account',
    'version': '11.0.1.0.0',
    'summary': 'Account Company Properties',
    'author': 'Creu Blanca, Eficent, Odoo Community Association (OCA)',
    'sequence': 30,
    'license': 'LGPL-3',
    'website': 'http://www.eficent.com',
    'depends': ['account', 'multicompany_property_product',
                'payment'],
    'data': [
        'views/partner_views.xml',
        'views/product_views.xml',
        'views/product_category_views.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
