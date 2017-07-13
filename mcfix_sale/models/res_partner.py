# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.constrains('company_id')
    def _check_sales_order_company(self):
        for rec in self:
            if rec.company_id:
                orders_partner = self.env['sale.order'].\
                    search([('partner_id', '=', rec.id),
                            ('company_id', '!=', rec.company_id.id)], limit=1)
                orders_partner_shipping = self.env['sale.order'].search(
                    [('partner_shipping_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                partner_invoice_id = self.env['sale.order'].search(
                    [('partner_shipping_id', '=', rec.id),
                     ('company_id', '!=', rec.company_id.id)], limit=1)

                if orders_partner or orders_partner_shipping or \
                        partner_invoice_id:
                    raise ValidationError(_('Sales orders already exist '
                                            'referencing this partner in '
                                            'other companies.'))
