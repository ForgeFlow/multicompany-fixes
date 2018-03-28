from odoo import api, models, _
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res = res + [
            self.env['account.journal'].search(
                [('refund_sequence_id', '=', self.id)]),
            self.env['account.journal'].search(
                [('sequence_id', '=', self.id)]),
        ]
        return res
