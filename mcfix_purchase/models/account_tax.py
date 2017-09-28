# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountTax, self)._check_company_id()
        for rec in self:
            order_line = self.env['purchase.order.line'].search(
                [('taxes_id', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Tax is assigned to Purchase Order Line '
                      '%s of Purchase %s.' % (order_line.name,
                                              order_line.order_id.name)))
