# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountAnalyticAccount, self)._check_company_id()
        for rec in self:
            order_line = self.env['purchase.order.line'].search(
                [('account_analytic_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Analytic Account is assigned to Purchase Order Line '
                      '%s of Purchase Order %s.' % (order_line.name,
                                                    order_line.order_id.name)))
