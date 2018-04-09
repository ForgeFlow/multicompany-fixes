# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Multi Company Fix Point of Sale',
    'version': '11.0.1.0.0',
    'summary': 'Point of Sale fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/multi-company',
    'category': 'Point Of Sale',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'mcfix_stock_account', 'mcfix_account'],
    'data': [
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'wizard/pos_details.xml',
    ],
    'demo': [
        'data/point_of_sale_demo.xml',
    ],
    'sequence': 30,
    'installable': True,
    'application': False,
    'auto_install': True,
}
