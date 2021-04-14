# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Product",
    "version": "13.0.1.0.0",
    "summary": "Product Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "http://www.forgeflow.com",
    "depends": ["product", "multicompany_property_base"],
    "data": ["views/product_views.xml", "views/product_category_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
