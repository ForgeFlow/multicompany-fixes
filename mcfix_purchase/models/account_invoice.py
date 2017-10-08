# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        if not self.account_id:
            self.account_id = self.partner_id.with_context(
                force_company=self.company_id.id).property_account_payable_id
        return res

    def _prepare_invoice_line_from_po_line(self, line):
        return super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line.with_context(force_company=self.company_id.id))

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        if not self.env.context.get('default_journal_id') and\
            self.partner_id and self.currency_id and\
            self.type in ['in_invoice', 'in_refund'] and\
            self.currency_id != self.partner_id.\
                with_context(force_company=self.company_id.id).\
                property_purchase_currency_id:
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.partner_id.
                 with_context(force_company=self.company_id.id).
                 property_purchase_currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(
                journal_domain, limit=1)
            if default_journal_id:
                self.journal_id = default_journal_id
        return res

    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        i_line = i_line.with_context(force_company=self.company_id.id)
        nself = self.with_context(force_company=self.company_id.id)
        return super(AccountInvoice, nself)._anglo_saxon_purchase_move_lines(
            i_line, res)

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountInvoice, self).onchange_company_id()
        self.purchase_id = False

    @api.multi
    @api.constrains('purchase_id', 'company_id')
    def _check_company_purchase_id(self):
        for invoice in self.sudo():
            if invoice.company_id and invoice.purchase_id.company_id and \
                    invoice.company_id != invoice.purchase_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice and in '
                      'Purchase Order must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoice, self).onchange_company_id()
        for rec in self:
            order = self.env['purchase.order'].search(
                [('invoice_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'invoice is assigned to Purchase Order '
                      '%s.' % order.name))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountInvoiceLine, self)._check_company_id()
        self.purchase_line_id = False
        self.purchase_id = False

    @api.multi
    @api.constrains('purchase_line_id', 'company_id')
    def _check_company_purchase_line_id(self):
        for invoice_line in self.sudo():
            if invoice_line.company_id and invoice_line.purchase_line_id.\
                    company_id and invoice_line.company_id != invoice_line.\
                    purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Invoice Line and in '
                      'Purchase Order Line must be the same.'))
        return True

    @api.multi
    @api.constrains('purchase_id', 'company_id')
    def _check_company_purchase_id(self):
        for invoice_line in self.sudo():
            if invoice_line.company_id and invoice_line.purchase_id.company_id\
                    and invoice_line.company_id != invoice_line.purchase_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Invoice Line and in '
                      'Purchase Order must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(AccountInvoiceLine, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            order_line = self.env['purchase.order.line'].search(
                [('invoice_lines', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Invoice Line is assigned to Purchase Order Line '
                      '%s of Purchase Order %s.' % (order_line.name,
                                                    order_line.order_id.name)))
