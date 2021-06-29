from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"
    _check_company_auto = True

    @api.model
    def _default_receivable_account_id(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        company = self.env["res.company"].browse(company_id)
        return company.account_default_pos_receivable_account_id

    @api.model
    def _default_company(self):
        return self.env.context.get("company_id", self.env.company.id)

    receivable_account_id = fields.Many2one(default=_default_receivable_account_id)
    cash_journal_id = fields.Many2one(check_company=True)
    open_session_ids = fields.Many2many(check_company=True)
    config_ids = fields.Many2many(check_company=True)
    company_id = fields.Many2one(default=_default_company)
