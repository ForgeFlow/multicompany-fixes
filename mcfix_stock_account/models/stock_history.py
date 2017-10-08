# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockHistory(models.Model):
    _inherit = 'stock.history'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockHistory, self).name_get()
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
        self.move_id = False
        self.location_id = False
        self.product_template_id = False

    @api.multi
    @api.constrains('move_id', 'company_id')
    def _check_company_move_id(self):
        for history in self.sudo():
            if history.company_id and history.move_id.company_id and \
                    history.company_id != history.move_id.company_id:
                raise ValidationError(
                    _('The Company in the History and in '
                      'Move must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for history in self.sudo():
            if history.company_id and history.location_id.company_id and \
                    history.company_id != history.location_id.company_id:
                raise ValidationError(
                    _('The Company in the History and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('product_template_id', 'company_id')
    def _check_company_product_template_id(self):
        for history in self.sudo():
            if history.company_id and history.product_template_id.company_id \
                    and history.company_id != history.product_template_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the History and in '
                      'Product Template must be the same.'))
        return True
