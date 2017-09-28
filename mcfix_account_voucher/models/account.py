# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAccount, self)._check_company_id()
        for rec in self:
            voucher = self.env['account.voucher'].search(
                [('account_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      ' is assigned to Voucher '
                      '%s.' % voucher.name))


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
                      ' is assigned to Voucher '
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
                      ' is assigned to Voucher '
                      '%s.' % voucher.name))
