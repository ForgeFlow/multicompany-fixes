# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('company_id')
    def _check_company_id(self):
        super(SaleOrder, self)._check_company_id()
        for rec in self:
            lead = self.env['crm.lead'].search(
                [('order_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if lead:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Orders is assigned to Lead '
                      '%s.' % lead.name))
