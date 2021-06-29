from odoo import fields, models


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order", [("fiscal_position_id", "=", self.id)]),
        ]
        return res


class Partner(models.Model):
    _inherit = "res.partner"

    sale_order_ids = fields.One2many(check_company=True)

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("sale.order", [("partner_id", "=", self.id)]),
        ]
        return res
