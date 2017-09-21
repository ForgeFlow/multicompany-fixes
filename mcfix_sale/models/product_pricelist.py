# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if rec.company_id:
                order_id = self.env['sale.order'].search(
                    [('pricelist_id', '=', rec.id), ('company_id', '!=',
                                                     rec.company_id.id)],
                    limit=1)
                if order_id:
                    raise ValidationError(_('Sales Orders already exist '
                                            'referencing this pricelist in '
                                            'other companies.'))
