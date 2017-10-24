# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.constrains('company_id')
    def _check_company_id(self):
        super(Pricelist, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            order = self.env['pos.order'].search(
                [('pricelist_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Pos Order '
                      '%s.' % order.name))
            pos_order = self.env['report.pos.order'].search(
                [('pricelist_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Report Pos Order '
                      '%s.' % pos_order.name))
            config = self.env['pos.config'].search(
                [('pricelist_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if config:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Pos Config '
                      '%s.' % config.name))
