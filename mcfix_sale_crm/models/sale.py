# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('company_id')
    def onchange_company_id(self):
        super(SaleOrder, self).onchange_company_id()
        self.opportunity_id = False

    @api.constrains('company_id')
    def _check_company_id(self):
        super(SaleOrder, self)._check_company_id()
        for rec in self:
            lead = self.env['crm.lead'].search(
                [('order_ids', 'in', [rec.id]),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if lead:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Orders is assigned to Lead '
                      '%s.' % lead.name))

    @api.multi
    @api.constrains('opportunity_id', 'company_id')
    def _check_company_opportunity_id(self):
        for order in self.sudo():
            if order.company_id and order.opportunity_id.company_id and \
                    order.company_id != order.opportunity_id.company_id:
                raise ValidationError(
                    _('The Company in the Sales Order and in '
                      'Opportunity must be the same.'))
        return True
