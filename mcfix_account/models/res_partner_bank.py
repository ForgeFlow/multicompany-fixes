from odoo import models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.journal_id, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('account.bank.statement.line',
             [('bank_account_id', '=', self.id)]),
            ('account.move', [('invoice_partner_bank_id', '=', self.id)]),
        ]
        return res
