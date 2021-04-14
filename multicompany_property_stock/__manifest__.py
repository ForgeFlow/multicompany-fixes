# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Stock",
    "version": "13.0.1.0.0",
    "summary": "Stock Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "http://www.forgeflow.com",
    "depends": ["stock", "multicompany_property_product"],
    "data": [
        "views/product_views.xml",
        "views/partner_views.xml",
        "views/stock_warehouse_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
