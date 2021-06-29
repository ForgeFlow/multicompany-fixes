from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.account_move_ids,
        ]
        return res
