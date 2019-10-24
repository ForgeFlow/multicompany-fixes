# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAssetProfile(models.Model):
    _inherit = 'account.asset.profile'

    @api.constrains('company_id', 'account_analytic_id')
    def _check_company_id_account_analytic_id(self):
        for rec in self.sudo():
            if not rec.account_analytic_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account Analytic account must be the same.'))

    @api.constrains('company_id', 'account_asset_id')
    def _check_company_id_account_asset_id(self):
        for rec in self.sudo():
            if not rec.account_asset_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account Asset must be the same.'))

    @api.constrains('company_id', 'account_depreciation_id')
    def _check_company_id_account_depreciation_id(self):
        for rec in self.sudo():
            if not rec.account_depreciation_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account must be the same. (Depreciation account)'))

    @api.constrains('company_id', 'account_expense_depreciation_id')
    def _check_company_id_account_expense_depreciation_id(self):
        for rec in self.sudo():
            if not rec.account_expense_depreciation_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account must be the same. (Expense account)'))

    @api.constrains('company_id', 'account_plus_value_id')
    def _check_company_id_account_plus_value_id(self):
        for rec in self.sudo():
            if not rec.account_plus_value_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account must be the same. (Plus value)'))

    @api.constrains('company_id', 'account_min_value_id')
    def _check_company_id_account_min_value_id(self):
        for rec in self.sudo():
            if not rec.profile_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account must be the same. (Min value)'))

    @api.constrains('company_id', 'account_residual_value_id')
    def _check_company_id_account_residual_value_id(self):
        for rec in self.sudo():
            if not rec.profile_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account must be the same. (Residual)'))

    @api.constrains('company_id', 'journal_id')
    def _check_company_id_journal_id(self):
        for rec in self.sudo():
            if not rec.profile_id.check_company(
                    rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Account Asset Profile and in '
                      'Account Journal must be the same.'))
