# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountInvoice, self).onchange_company_id()
        self.team_id = False

    @api.multi
    @api.constrains('team_id', 'company_id')
    def _check_company_team_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.team_id.company_id and \
                    invoice.company_id != invoice.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice and in '
                      'Sales Team must be the same.'))
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if not rec.company_id:
                continue
            order_line_id = self.env['sale.order.line'].search(
                [('invoice_lines', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line_id:
                raise ValidationError(
                    _('Sales Order lines already exist referencing this '
                      'Invoice line in other companies.'))
