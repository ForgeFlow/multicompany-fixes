# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Multi Company Account Product Analytic",
    "version": "13.0.1.0.0",
    "summary": "Product Analytic Company Properties",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "AGPL-3",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "depends": ["multicompany_property_account", "product_analytic"],
    "data": ["views/product_views.xml", "views/product_category_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
