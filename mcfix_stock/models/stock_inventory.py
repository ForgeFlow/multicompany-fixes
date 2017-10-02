# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockInventory, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.location_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for inventory in self.sudo():
            if inventory.company_id and inventory.location_id and \
                    inventory.company_id != inventory.location_id.company_id:
                raise ValidationError(_('The Company in the Inventory and in '
                                        'Location must be the same.'))
        return True
