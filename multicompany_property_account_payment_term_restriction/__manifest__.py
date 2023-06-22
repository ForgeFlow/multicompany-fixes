# Copyright 2023 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Multi Company Account Payment Term Restriction",
    "version": "15.0.1.0.0",
    "summary": "Payment Term Multi-Company Restrictions",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "license": "LGPL-3",
    "depends": [
        "multicompany_property_account",
        "account_payment_term_restriction_sale",
        "account_payment_term_restriction_purchase",
    ],
    "data": ["views/partner_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
