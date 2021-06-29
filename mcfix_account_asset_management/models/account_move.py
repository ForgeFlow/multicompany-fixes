# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    asset_profile_id = fields.Many2one(check_company=True)
    asset_id = fields.Many2one(check_company=True)
