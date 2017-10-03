# -*- coding: utf-8 -*-
from odoo import api, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(Pricelist, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
