from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    _check_company_auto = True

    journal_id = fields.One2many(check_company=True)
    bank_statement_line_ids = fields.One2many(
        "account.bank.statement.line",
        inverse_name="bank_account_id",
        check_company=True,
    )
    account_move_ids = fields.One2many(
        "account.move", inverse_name="invoice_partner_bank_id", check_company=True
    )
