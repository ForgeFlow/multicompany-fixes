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


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id')
    def _check_purchase_order_company(self):
        for rec in self:
            if rec.company_id:
                order_line_id = self.env['purchase.order.line'].search(
                    [('invoice_lines', 'in', [rec.id]),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if order_line_id:
                    raise ValidationError(_('Purchase Order lines already '
                                            'exist referencing this invoice '
                                            'line in other companies.'))
