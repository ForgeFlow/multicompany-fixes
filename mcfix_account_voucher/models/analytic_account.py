# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAnalyticAccount, self)._check_company_id()
        for rec in self:
            voucher_line = self.env['account.voucher.line'].search(
                [('account_analytic_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if voucher_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Voucher Line '
                      '%s.' % voucher_line.name))
