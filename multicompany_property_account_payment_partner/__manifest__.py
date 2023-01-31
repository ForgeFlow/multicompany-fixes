# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Account Payment Partner",
    "version": "13.0.1.0.0",
    "summary": "Account Payment Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "AGPL-3",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "depends": ["multicompany_property_account", "account_payment_partner"],
    "data": ["views/partner_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
