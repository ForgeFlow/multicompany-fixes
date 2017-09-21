# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if rec.company_id:
                order_line_id = self.env['sale.order.line'].search(
                    [('invoice_lines', 'in', [rec.id]),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if order_line_id:
                    raise ValidationError(_('Sales Order lines already exist '
                                            'referencing this Invoice line '
                                            'in other companies.'))
