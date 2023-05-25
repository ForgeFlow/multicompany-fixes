# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Multi Company Fix Base",
    "version": "13.0.1.0.0",
    "summary": "Base fixes",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/ForgeFlow/multicompany-fixes",
    "license": "LGPL-3",
    "depends": ["base"],
    # 'demo': [
    #     'demo/res_partner_demo.xml',
    # ],
    "sequence": 150,
    "post_load": "post_load_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
