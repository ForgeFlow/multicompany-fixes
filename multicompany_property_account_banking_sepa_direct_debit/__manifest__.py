# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Multi Company Property Account Banking SEPA Direct Debit",
    "version": "13.0.1.0.0",
    "summary": "Account Company Properties",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "sequence": 30,
    "license": "AGPL-3",
    "website": "http://www.forgeflow.com",
    "depends": [
        "multicompany_property_account_banking_pain_base",
        "account_banking_sepa_direct_debit",
    ],
    "data": ["views/res_company_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
