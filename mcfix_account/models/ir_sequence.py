# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(IrSequence, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = "%s [%s]" % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

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
