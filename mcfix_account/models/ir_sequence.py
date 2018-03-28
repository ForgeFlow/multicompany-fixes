from odoo import models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def chart_template_id(self):
        res = super().chart_template_id()
        res = res + [
            ('account.journal', [('refund_sequence_id', '=', self.id)]),
            ('account.journal', [('sequence_id', '=', self.id)]),
        ]
        return res
