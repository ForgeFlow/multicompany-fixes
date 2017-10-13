# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if rec.company_id:
                order_line_id = self.env['sale.order.line'].search(
                    [('tax_id', 'in', [rec.id]),
                     ('company_id', '!=', rec.company_id.id)], limit=1)

                if order_line_id:
                    raise ValidationError(
                        _('Sales Order line already exists referencing this '
                          'tax in other company : %s.') %
                        order_line_id.company_id.name)
