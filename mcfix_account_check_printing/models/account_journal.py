from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    check_sequence_id = fields.Many2one(check_company=True)
