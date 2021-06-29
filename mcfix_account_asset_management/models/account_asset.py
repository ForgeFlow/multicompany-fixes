# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"
    _check_company_auto = True

    company_id = fields.Many2one(readonly=False)
    profile_id = fields.Many2one(check_company=True)
    account_move_line_ids = fields.One2many(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    account_analytic_id = fields.Many2one(check_company=True)


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"
    _check_company_auto = True

    company_id = fields.Many2one(
        "res.company", store=True, readonly=True, related="asset_id.company_id",
    )
    move_id = fields.Many2one(check_company=True)
