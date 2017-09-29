# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountPaymentTerm, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('payment_term_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Payment Term is assigned to Sales Order '
                      '%s.' % order.name))
