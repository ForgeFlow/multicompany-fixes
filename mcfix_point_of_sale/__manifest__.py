# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Multi Company Fix Point of Sale",
    "version": "13.0.1.0.0",
    "summary": "Point of Sale fixes",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/multi-company",
    "category": "Point Of Sale",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "mcfix_stock_account"],
    "data": [
        "data/point_of_sale_data.xml",
        "views/pos_session_view.xml",
        "wizard/pos_details.xml",
    ],
    "sequence": 30,
    "installable": True,
    "application": False,
    "auto_install": True,
}
