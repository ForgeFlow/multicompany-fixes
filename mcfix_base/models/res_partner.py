# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ResPartner, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.one
    def _compute_current_company_id(self):
        self.current_company_id = self.env['res.company'].browse(
            self._context.get('force_company') or
            self.env.user.company_id.id).ensure_one()

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=_compute_current_company_id,
        compute='_compute_current_company_id',
        store=False
    )
