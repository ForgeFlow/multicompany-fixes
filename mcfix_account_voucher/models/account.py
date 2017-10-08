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
                voucher = self.env['account.voucher'].search(
                    [('account_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if voucher:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'account is assigned to Account Voucher '
                          '%s.' % voucher.name))
                voucher_line = self.env['account.voucher.line'].search(
                    [('account_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if voucher_line:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Account is assigned to Account Voucher Line '
                          '%s in Account Voucher %s.' % (
                           voucher_line.name,
                           voucher_line.voucher_id.name)))


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountJournal, self)._check_company_id()
        for rec in self:
            voucher = self.env['account.voucher'].search(
                [('journal_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      ' is assigned to Account Voucher '
                      '%s.' % voucher.name))


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountMove, self)._check_company_id()
        for rec in self:
            voucher = self.env['account.voucher'].search(
                [('move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      ' is assigned to Account Voucher '
                      '%s.' % voucher.name))


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountTax, self)._check_company_id()
        for rec in self:
            voucher_line = self.env['account.voucher.line'].search(
                [('tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'tax is assigned to Account Voucher Line '
                      '%s in Account Voucher %s.' % (
                       voucher_line.name, voucher_line.voucher_id.name)))
