# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Stock Account",
    "version": "13.0.1.0.0",
    "summary": "Stock Account Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "depends": ["multicompany_property_account", "multicompany_property_stock"],
    "data": [
        "views/product_views.xml",
        "views/product_category_views.xml",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
