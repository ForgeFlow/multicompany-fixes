# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProductTemplate, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            pos_order = self.env['report.pos.order'].search(
                [('product_tmpl_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pos_order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Pos Order '
                      '%s.' % pos_order.name))
