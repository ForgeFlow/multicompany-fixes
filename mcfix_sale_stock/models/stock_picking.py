# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(StockPicking, self).onchange_company_id()
        self.sale_id = False

    @api.multi
    @api.constrains('sale_id', 'company_id')
    def _check_company_sale_id(self):
        for picking in self.sudo():
            if picking.company_id and picking.sale_id.company_id and \
                    picking.company_id != picking.sale_id.company_id:
                raise ValidationError(
                    _('The Company in the Picking and in '
                      'Sales Order must be the same.'))
        return True
