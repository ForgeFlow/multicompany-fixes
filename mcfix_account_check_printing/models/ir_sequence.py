from odoo import models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ("account.journal", [("check_sequence_id", "=", self.id)]),
        ]
        return res
