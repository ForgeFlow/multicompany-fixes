# Copyright 2021 Creu Blanca
# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Stock",
    "version": "13.0.1.0.0",
    "summary": "Delivery Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "LGPL-3",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "depends": ["delivery", "multicompany_property_stock"],
    "data": ["views/partner_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
