from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('pos.order', [('account_move', '=', self.id)]),
        ]
        return res
