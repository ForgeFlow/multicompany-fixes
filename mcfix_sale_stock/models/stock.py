# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.constrains('company_id')
    def _check_company_id(self):
        super(StockWarehouse, self)._check_company_id()
        for rec in self:
            order = self.env['sale.order'].search(
                [('warehouse_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Warehouse is assigned to Sales Order '
                      '%s.' % order.name))
