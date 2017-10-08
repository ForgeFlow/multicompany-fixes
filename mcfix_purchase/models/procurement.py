# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProcurementRule, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            warehouse = self.env['stock.warehouse'].search(
                [('buy_pull_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Rule is assigned to Warehouse '
                      '%s.' % warehouse.name))


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProcurementOrder, self).onchange_company_id()
        self.purchase_line_id = False

    @api.multi
    @api.constrains('purchase_line_id', 'company_id')
    def _check_company_purchase_line_id(self):
        for order in self.sudo():
            if order.company_id and order.purchase_line_id.company_id and \
                    order.company_id != order.purchase_line_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Purchase Order Line must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProcurementOrder, self)._check_company_id()
        for rec in self:
            order_line = self.env['purchase.order.line'].search(
                [('procurement_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Order is assigned to Purchase Order Line '
                      '%s in Purchase Order %s.' % (
                       order_line.name, order_line.order_id.name)))
