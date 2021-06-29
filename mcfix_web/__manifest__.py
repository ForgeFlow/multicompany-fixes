# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Multi Company Fix Web",
    "version": "13.0.1.0.0",
    "summary": "Web fixes",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "http://www.forgeflow.com",
    "license": "LGPL-3",
    "depends": ["web", "mcfix_base"],
    "data": ["views/report_templates.xml"],
    "sequence": 30,
    "installable": True,
    "application": False,
    "auto_install": True,
}
