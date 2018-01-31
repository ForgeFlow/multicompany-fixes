# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProductTemplate, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            report = self.env['sale.report'].search(
                [('product_tmpl_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if report:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Report '
                      '%s.' % report.name))