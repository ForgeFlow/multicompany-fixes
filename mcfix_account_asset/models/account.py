# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAccount, self)._check_company_id()
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                asset_category = self.env['account.asset.category'].search(
                    [('account_asset_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if asset_category:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'account is assigned to Asset Category '
                          '%s.' % asset_category.name))
                asset_category = self.env['account.asset.category'].search(
                    [('account_depreciation_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if asset_category:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'account is assigned to Asset Category '
                          '%s.' % asset_category.name))
                asset_category = self.env['account.asset.category'].search(
                    [('account_depreciation_expense_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if asset_category:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'account is assigned to Asset Category '
                          '%s.' % asset_category.name))


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountJournal, self)._check_company_id()
        for rec in self:
            asset_category = self.env['account.asset.category'].search(
                [('journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if asset_category:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Journal is assigned to Asset Category '
                      '%s.' % asset_category.name))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoice, self)._check_company_id()
        for rec in self:
            asset_asset = self.env['account.asset.asset'].search(
                [('invoice_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if asset_asset:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice is assigned to Asset '
                      '%s.' % asset_asset.name))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountInvoiceLine, self)._check_company_id()
        self.asset_category_id = False

    @api.multi
    @api.constrains('asset_category_id', 'company_id')
    def _check_company_asset_category_id(self):
        for invoice_line in self.sudo():
            if invoice_line.company_id and invoice_line.asset_category_id.\
                    company_id and invoice_line.company_id != invoice_line.\
                    asset_category_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Line and in '
                      'Asset Category must be the same.'))
        return True
