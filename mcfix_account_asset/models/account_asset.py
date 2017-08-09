# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        res = {}
        for asset in self:
            journal = self.env['account.journal'].search(
                    [('company_id', '=', asset.company_id.id),
                     ('type', '=', asset.journal_id.type)
                     ], limit=1)
            asset.journal_id = journal
            if asset.journal_id and asset.journal_id.company_id != asset.company_id:
                asset.journal_id = False
            if asset.account_analytic_id and asset.account_analytic_id.company_id != asset.company_id:
                asset.account_analytic_id = False
            if asset.account_asset_id and asset.account_asset_id.company_id != asset.company_id:
                asset.account_asset_id = False
            if asset.account_depreciation_id and asset.account_depreciation_id.company_id != asset.company_id:
                asset.account_depreciation_id = False
            if asset.account_depreciation_expense_id and asset.account_depreciation_expense_id.company_id != asset.company_id:
                asset.account_depreciation_expense_id = False
        return res

    @api.multi
    @api.constrains('account_analytic_id', 'company_id')
    def _check_company_analytic_account(self):
        for asset in self:
            if asset.company_id and asset.account_analytic_id and\
                    asset.company_id != asset.account_analytic_id.company_id:
                raise ValidationError(_('The Company in the Asset category '
                                        'and in Analytic Account must '
                                        'be the same.'))
        return True

    @api.multi
    @api.constrains('account_asset_id', 'company_id')
    def _check_company_asset_account(self):
        for asset in self:
            if asset.company_id and asset.account_asset_id and\
                    asset.company_id != asset.account_asset_id.company_id:
                raise ValidationError(_('The Company in the Asset category '
                                        'and in Asset Account must '
                                        'be the same.'))
        return True

    @api.multi
    @api.constrains('account_depreciation_id', 'company_id')
    def _check_company_depreciation_account(self):
        for asset in self:
            if asset.company_id and asset.account_depreciation_id and\
                    asset.company_id != asset.account_depreciation_id.company_id:
                raise ValidationError(_('The Company in the Asset category '
                                        'and in Depreciation Account must '
                                        'be the same.'))
        return True

    @api.multi
    @api.constrains('account_depreciation_expense_id', 'company_id')
    def _check_company_depreciation_expense_account(self):
        for asset in self:
            if asset.company_id and asset.account_depreciation_expense_id and\
                    asset.company_id != asset.account_depreciation_expense_id.company_id:
                raise ValidationError(_('The Company in the Asset category '
                                        'and in Depreciation Expense Account '
                                        'must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal(self):
        for asset in self:
            if asset.company_id and asset.journal_id and\
                    asset.company_id != asset.journal_id.company_id:
                raise ValidationError(_('The Company in the Asset category '
                                        'and in Journal must be the same.'))
        return True

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.constrains('category_id', 'company_id')
    def _check_company_asset_categ(self):
        for asset in self:
            if asset.company_id and asset.category_id and\
                    asset.company_id != asset.category_id.company_id:
                raise ValidationError(_('The Company in the Asset and in '
                                        'Asset Category must be the same.'))
        return True