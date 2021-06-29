# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.session"
    _check_company_auto = True

    config_id = fields.Many2one(check_company=True)
