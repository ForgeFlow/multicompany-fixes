# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Multi Company Fix Sale",
    "version": "13.0.1.0.0",
    "summary": "Sale fixes",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "http://www.forgeflow.com",
    "license": "LGPL-3",
    "depends": ["sale", "mcfix_sales_team", "mcfix_account"],
    "data": ["report/sale_report_templates.xml"],
    "sequence": 30,
    "installable": True,
    "application": False,
    "auto_install": True,
}
