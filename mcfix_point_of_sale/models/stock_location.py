# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(StockLocation, self)._check_company_id()
        for rec in self:
            order = self.env['pos.order'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Pos Order '
                      '%s.' % order.name))
            pos_order = self.env['report.pos.order'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Report Pos Order '
                      '%s.' % pos_order.name))
            pos_order = self.env['report.pos.order'].search(
                [('stock_location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Warehouse is assigned to Report Pos Order '
                      '%s.' % pos_order.name))
            config = self.env['pos.config'].search(
                [('stock_location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Stock Location is assigned to Pos Config '
                      '%s.' % config.name))
