from odoo import models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res = res + [
            self.env['account.invoice'].search(
                [('partner_bank_id', '=', self.id)]),
            self.env['account.bank.statement.line'].search(
                [('bank_account_id', '=', self.id)]),
            self.env['account.journal'].search(
                [('bank_account_id', '=', self.id)]),
        ]
        return res
