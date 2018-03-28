from odoo import models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('account.invoice', [('partner_bank_id', '=', self.id)]),
            ('account.bank.statement.line',
             [('bank_account_id', '=', self.id)]),
            ('account.journal', [('bank_account_id', '=', self.id)]),
        ]
        return res
