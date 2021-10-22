# Copyright 2017 Creu Blanca
# Copyright 2017-21 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Property Account",
    "version": "14.0.1.0.0",
    "summary": "Account Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "https://github.com/OCA/multicompany-fixes",
    "depends": ["account", "multicompany_property_product"],
    "data": [
        "security/ir.model.access.csv",
        "views/partner_views.xml",
        "views/product_views.xml",
        "views/product_category_views.xml",
        "views/res_company_views.xml",
        "views/tax_group_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
