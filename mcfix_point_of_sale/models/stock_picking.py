# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(StockPicking, self)._check_company_id()
        for rec in self:
            order = self.env['pos.order'].search(
                [('picking_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Picking is assigned to Pos Order '
                      '%s.' % order.name))
