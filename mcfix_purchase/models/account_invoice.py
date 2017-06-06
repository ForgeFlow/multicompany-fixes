from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        if not self.account_id:
            self.account_id = self.partner_id.with_context(force_company=self.company_id.id).property_account_payable_id
        return res

    def _prepare_invoice_line_from_po_line(self, line):
        return super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line.with_context(force_company=self.company_id.id))
