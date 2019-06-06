from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('payment.acquirer', [('journal_id', '=', self.id)]),
        ]
        return res
