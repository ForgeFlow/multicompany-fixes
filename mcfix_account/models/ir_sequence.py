# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def write(self, vals):
        if vals.get('company_id', False):
            if not self.env.context.get('bypass_company_validation', False):
                for rec in self:
                    if self.env['account.journal'].search(
                            [('sequence_id', '=', rec.id),
                             ('company_id', '!=', vals['company_id'])],
                            limit=1):
                        raise ValidationError(_(
                            'This sequence is already being used in journals '
                            'that belongs to another company.'))
                    if self.env['account.journal'].search(
                            [('refund_sequence_id', '=', rec.id),
                             ('company_id', '!=', vals['company_id'])],
                            limit=1):
                        raise ValidationError(_(
                            'This sequence is already being used in journals '
                            'as refund sequence, that belongs to another '
                            'company.'))
        return super(IrSequence, self).write(vals)
