# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.multi
    def write(self, values):
        # We are deleting currency_id if it does not change because if it is set,
        # the product.res_company.py will create a pricelist and will duplicate ir.properties.
        if values.get('currency_id', False) and self.currency_id.id == values.get('currency_id', False):
            values.pop('currency_id', False)
        return super(ResCompany, self).write(values)
