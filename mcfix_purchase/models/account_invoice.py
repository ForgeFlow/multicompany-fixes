from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id:
            self.company_id = self.purchase_id.company_id
        return super().purchase_order_change()

    def _prepare_invoice_line_from_po_line(self, line):
        data = super()._prepare_invoice_line_from_po_line(line)
        data['account_id'] = False
        account = self.env['account.invoice.line'].get_invoice_line_account(
            'in_invoice',
            line.with_context(force_company=line.company_id.id).product_id,
            line.order_id.fiscal_position_id,
            line.company_id)
        if account:
            data['account_id'] = account.id
        return data

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super()._onchange_company_id()
        if not self.purchase_id.check_company(self.company_id):
            if self.refund_invoice_id.purchase_id:
                self.purchase_id = self.refund_invoice_id.purchase_id
            else:
                self.purchase_id = False

    @api.multi
    @api.constrains('company_id', 'purchase_id')
    def _check_company_id_purchase_id(self):
        for rec in self.sudo():
            if not rec.purchase_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice and in '
                      'Purchase Order must be the same.'))

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('purchase.order', [('invoice_ids', 'in', self.ids)]),
        ]
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    @api.constrains('company_id', 'purchase_line_id')
    def _check_company_id_purchase_line_id(self):
        for rec in self.sudo():
            if not rec.purchase_line_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Account Invoice Line and in '
                      'Purchase Order Line must be the same.'))
