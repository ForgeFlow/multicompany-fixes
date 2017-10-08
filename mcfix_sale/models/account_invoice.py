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
            if invoice.company_id and invoice.team_id and \
                    invoice.company_id != invoice.team_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice and in '
                      'Sales Team must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoice, self).onchange_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('invoice_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'invoice is assigned to Sales Order '
                      '%s.' % order.name))

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoice, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('invoice_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice is assigned to Sales Order '
                      '%s.' % order.name))


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
