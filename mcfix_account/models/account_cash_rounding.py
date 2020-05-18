from odoo import fields, models


class AccountCashRounding(models.Model):
    _inherit = 'account.cash.rounding'

    account_id = fields.Many2one(company_dependent=True)
