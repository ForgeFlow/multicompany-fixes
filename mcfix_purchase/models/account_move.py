from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    purchase_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super()._onchange_company_id()
        if not self.purchase_id.check_company(self.company_id):
            self.purchase_id = self.refund_invoice_id.purchase_id

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("purchase.order", [("invoice_ids", "in", self.ids)]),
        ]
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    purchase_line_id = fields.Many2one(check_company=True)
