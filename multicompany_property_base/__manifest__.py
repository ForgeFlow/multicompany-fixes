# Copyright 2017 Creu Blanca
# Copyright 2017-21 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Property Base",
    "version": "14.0.1.0.0",
    "summary": "Base Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "sequence": 30,
    "website": "https://github.com/OCA/multicompany-fixes",
    "depends": ["base"],
    "data": [
        "views/partner_views.xml",
        "views/res_company_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
