from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    journal_ids = fields.One2many(
        "account.journal", inverse_name="sequence_id", check_company=True
    )
    refund_journal_ids = fields.One2many(
        "account.journal", inverse_name="refund_sequence_id", check_company=True
    )
