# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAssetProfile(models.Model):
    _inherit = "account.asset.profile"
    _check_company_auto = True

    account_analytic_id = fields.Many2one(check_company=True)
    account_asset_id = fields.Many2one(check_company=True)
    account_depreciation_id = fields.Many2one(check_company=True)
    account_expense_depreciation_id = fields.Many2one(check_company=True)
    account_plus_value_id = fields.Many2one(check_company=True)
    account_min_value_id = fields.Many2one(check_company=True)
    account_residual_value_id = fields.Many2one(check_company=True)
    journal_id = fields.Many2one(check_company=True)
