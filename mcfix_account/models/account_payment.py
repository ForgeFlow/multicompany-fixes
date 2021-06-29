from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"
    _check_company_auto = True

    journal_id = fields.Many2one(check_company=True)
    partner_bank_account_id = fields.Many2one(check_company=True)
    partner_id = fields.Many2one(check_company=True)
    destination_account_id = fields.Many2one(check_company=True)
    writeoff_account_id = fields.Many2one(check_company=True)
    invoice_ids = fields.Many2many(check_company=True)
    move_line_ids = fields.One2many(check_company=True)

    @api.constrains("journal_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
