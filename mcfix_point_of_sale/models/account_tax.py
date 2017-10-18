# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountTax, self)._check_company_id()
        for rec in self:
            order_line = self.env['pos.order.line'].search(
                [('tax_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Tax is assigned to Pos Order Line '
                      '%s of Pos Order %s.' % (
                          order_line.name, order_line.order_id.name)))
