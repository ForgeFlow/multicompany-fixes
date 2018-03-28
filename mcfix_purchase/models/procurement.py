from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('stock.warehouse', [('buy_pull_id', '=', self.id)]),
        ]
        return res
