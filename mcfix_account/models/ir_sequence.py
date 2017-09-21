# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def write(self, vals):
        if 'company_id' in vals and vals['company_id']:
            for rec in self:
                if self.env['account.journal'].search(
                        [('sequence_id', '=', rec.id),
                         ('company_id', '!=', rec.company_id.id)], limit=1):
                    raise ValidationError(_(
                        'This sequence is already being used in journals that '
                        'belongs to another company.'))
                if self.env['account.journal'].search(
                        [('refund_sequence_id', '=', rec.id),
                         ('company_id', '!=', rec.company_id.id)], limit=1):
                    raise ValidationError(_(
                        'This sequence is already being used in journals as '
                        'refund sequence, that belongs to another company.'))
