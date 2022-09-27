from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    purchase_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super()._onchange_company_id()
        if not self.purchase_id.check_company(self.company_id):
            self.purchase_id = False


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    purchase_line_id = fields.Many2one(check_company=True)
