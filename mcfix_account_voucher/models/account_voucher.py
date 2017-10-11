# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountVoucher, self).name_get()
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
        self.journal_id = False
        self.account_id = False
        self.move_id = False

    @api.multi
    @api.constrains('journal_id', 'company_id')
    def _check_company_journal_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.journal_id.company_id and \
                    voucher.company_id != voucher.journal_id.company_id:
                raise ValidationError(
                    _('The Company in the Voucher and in '
                      'Journal must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.account_id.company_id and \
                    voucher.company_id != voucher.account_id.company_id:
                raise ValidationError(
                    _('The Company in the Voucher and in '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('move_id', 'company_id')
    def _check_company_move_id(self):
        for voucher in self.sudo():
            if voucher.company_id and voucher.move_id.company_id and \
                    voucher.company_id != voucher.move_id.company_id:
                raise ValidationError(
                    _('The Company in the Voucher and in '
                      'Account Move must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            voucher_line = self.env['account.voucher.line'].search(
                [('voucher_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'account voucher is assigned to Voucher Line '
                      '%s.' % voucher_line.name))


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(AccountVoucherLine, self).name_get()
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
        self.voucher_id = False
        self.account_id = False
        self.account_analytic_id = False
        self.tax_ids = False

    @api.multi
    @api.constrains('voucher_id', 'company_id')
    def _check_company_voucher_id(self):
        for voucher_line in self.sudo():
            if voucher_line.company_id and voucher_line.voucher_id.company_id \
                    and voucher_line.company_id != voucher_line.voucher_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Account voucher line and in '
                      'Account voucher must be the same.'))
        return True

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for voucher_line in self.sudo():
            if voucher_line.company_id and voucher_line.account_id.company_id \
                    and voucher_line.company_id != voucher_line.account_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Voucher Line and in '
                      'Account must be the same.'))
        return True

    @api.multi
    @api.constrains('account_analytic_id', 'company_id')
    def _check_company_account_analytic_id(self):
        for voucher_line in self.sudo():
            if voucher_line.company_id and voucher_line.account_analytic_id.\
                    company_id and voucher_line.company_id != voucher_line.\
                    account_analytic_id.company_id:
                raise ValidationError(
                    _('The Company in the Voucher Line and in '
                      'Account Analytic must be the same.'))
        return True

    @api.multi
    @api.constrains('tax_ids', 'company_id')
    def _check_company_tax_ids(self):
        for voucher_line in self.sudo():
            for account_tax in voucher_line.tax_ids:
                if voucher_line.company_id and account_tax.company_id and \
                        voucher_line.company_id != account_tax.company_id:
                    raise ValidationError(
                        _('The Company in the Voucher Line and in '
                          'Tax must be the same.'))
        return True
