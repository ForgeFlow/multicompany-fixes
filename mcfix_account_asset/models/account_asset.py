# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountAssetCategory, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        res = {}
        for asset in self:
            journal = self.env['account.journal'].\
                search([('company_id', '=', asset.company_id.id),
                        ('type', '=', asset.journal_id.type)], limit=1)
            asset.journal_id = journal
            if asset.journal_id and\
                    asset.journal_id.company_id != asset.company_id:
                asset.journal_id = False
            if asset.account_analytic_id and\
                    asset.account_analytic_id.company_id != asset.company_id:
                asset.account_analytic_id = False
            if asset.account_asset_id and\
                    asset.account_asset_id.company_id != asset.company_id:
                asset.account_asset_id = False
            if asset.account_depreciation_id and\
                    asset.account_depreciation_id.company_id != asset.\
                    company_id:
                asset.account_depreciation_id = False
            if asset.account_depreciation_expense_id and\
                    asset.account_depreciation_expense_id.company_id != asset.\
                    company_id:
                asset.account_depreciation_expense_id = False
        return res

    @api.multi
    @api.constrains('account_analytic_id', 'company_id')
    def _check_company_analytic_account(self):
        for asset in self:
            if asset.company_id and asset.account_analytic_id.company_id and\
                    asset.company_id != asset.account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset category '
                      'and in Analytic Account must '
                      'be the same.'))
        return True

    @api.multi
    @api.constrains('account_asset_id', 'company_id')
    def _check_company_asset_account(self):
        for asset in self:
            if asset.company_id and asset.account_asset_id.company_id and\
                    asset.company_id != asset.account_asset_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset category '
                      'and in Asset Account must '
                      'be the same.'))
        return True

    @api.multi
    @api.constrains('account_depreciation_id', 'company_id')
    def _check_company_depreciation_account(self):
        for asset in self:
            if asset.company_id and asset.account_depreciation_id.company_id \
                    and asset.company_id != asset.account_depreciation_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Asset category '
                      'and in Depreciation Account must '
                      'be the same.'))
        return True

    @api.multi
    @api.constrains('account_depreciation_expense_id', 'company_id')
    def _check_company_depreciation_expense_account(self):
        for asset in self:
            if asset.company_id and asset.account_depreciation_expense_id.\
                    company_id and asset.company_id != asset.\
                    account_depreciation_expense_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset category '
                      'and in Depreciation Expense Account '
                      'must be the same.'))
        return True

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal(self):
        for asset in self:
            if asset.company_id and asset.journal_id.company_id and\
                    asset.company_id != asset.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset category '
                      'and in Journal must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            invoice_line = self.env['account.invoice.line'].search(
                [('asset_category_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if invoice_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Asset category is assigned to Invoice Line '
                      '%s.' % invoice_line.name))
            asset_asset = self.env['account.asset.asset'].search(
                [('category_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if asset_asset:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Asset category is assigned to Asset '
                      '%s.' % asset_asset.name))
            asset_report = self.env['asset.asset.report'].search(
                [('asset_category_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if asset_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Asset category is assigned to Asset Report '
                      '%s.' % asset_report.name))
            template = self.env['product.template'].search(
                [('asset_category_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Asset Type is assigned to Product Template '
                      '%s.' % template.name))
            template = self.env['product.template'].search(
                [('deferred_revenue_category_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Deferred Revenue Type is assigned to Product Template '
                      '%s.' % template.name))


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountAssetAsset, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.category_id = False
        self.invoice_id = False

    @api.constrains('category_id', 'company_id')
    def _check_company_asset_categ(self):
        for asset in self.sudo():
            if asset.company_id and asset.category_id.company_id and\
                    asset.company_id != asset.category_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset and in '
                      'Asset Category must be the same.'))
        return True

    @api.multi
    @api.constrains('invoice_id', 'company_id')
    def _check_company_invoice_id(self):
        for asset in self.sudo():
            if asset.company_id and asset.invoice_id.company_id and \
                    asset.company_id != asset.invoice_id.company_id:
                raise ValidationError(
                    _('The Company in the Asset and in '
                      'Invoice must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            asset_report = self.env['asset.asset.report'].search(
                [('asset_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if asset_report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Asset is assigned to Asset Report '
                      '%s.' % asset_report.name))
