from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    team_id = fields.Many2one(check_company=True)
    partner_shipping_id = fields.Many2one(check_company=True)

    @api.onchange("company_id")
    def _onchange_company_id(self):
        super()._onchange_company_id()
        if not self.partner_shipping_id.check_company(self.company_id):
            self.partner_shipping_id = False
            if self.refund_invoice_id.partner_shipping_id:
                self.partner_shipping_id = self.refund_invoice_id.partner_shipping_id
            else:
                self.partner_shipping_id = False
        if not self.team_id.check_company(self.company_id):
            self.team_id = False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sale_line_ids = fields.Many2many(check_company=True)

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order.line", [("invoice_lines", "in", self.ids)]),
        ]
        return res
