# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Purchase",
    "version": "13.0.1.0.0",
    "summary": "Purchase Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "depends": ["purchase", "multicompany_property_stock_account"],
    "data": [
        "views/partner_views.xml",
        "views/product_views.xml",
        "views/product_category_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
