# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = "procurement.rule"

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProcurementRule, self).onchange_company_id()
        self.location_id = False
        self.location_src_id = False
        self.route_id = False
        self.warehouse_id = False
        self.propagate_warehouse_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.location_id.company_id and \
                    rule.company_id != rule.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule '
                      'and in Location must be the same.'))
        return True

    @api.multi
    @api.constrains('location_src_id', 'company_id')
    def _check_company_location_src_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.location_src_id.company_id and \
                    rule.company_id != rule.location_src_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule '
                      'and in Location must be the same.'))
        return True

    @api.multi
    @api.constrains('route_id', 'company_id')
    def _check_company_route_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.route_id.company_id and \
                    rule.company_id != rule.route_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule '
                      'and in Route must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.warehouse_id.company_id and \
                    rule.company_id != rule.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule '
                      'and in Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('propagate_warehouse_id', 'company_id')
    def _check_company_propagate_warehouse_id(self):
        for rule in self.sudo():
            if rule.company_id and rule.propagate_warehouse_id.company_id and \
                    rule.company_id != rule.propagate_warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule '
                      'and in Warehouse must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProcurementRule, self)._check_company_id()
        for rec in self:
            if not rec.company_id:
                continue
            move = self.env['stock.move'].search(
                [('rule_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Rule is assigned to Move '
                      '%s.' % move.name))
            warehouse = self.env['stock.warehouse'].search(
                [('mto_pull_id', '=', rec.id),
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
        self.location_id = False
        self.move_dest_id = False
        self.route_ids = False
        self.warehouse_id = False
        self.orderpoint_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for order in self.sudo():
            if order.company_id and order.location_id.company_id and \
                    order.company_id != order.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('move_dest_id', 'company_id')
    def _check_company_move_dest_id(self):
        for order in self.sudo():
            if order.company_id and order.move_dest_id.company_id and \
                    order.company_id != order.move_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Stock Move must be the same.'))
        return True

    @api.multi
    @api.constrains('route_ids', 'company_id')
    def _check_company_route_ids(self):
        for order in self.sudo():
            for stock_location_route in order.route_ids:
                if order.company_id and stock_location_route.company_id and \
                        order.company_id != stock_location_route.company_id:
                    raise ValidationError(
                        _('The Company in the Procurement Order and in '
                          'Location Route must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for order in self.sudo():
            if order.company_id and order.warehouse_id.company_id and \
                    order.company_id != order.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('orderpoint_id', 'company_id')
    def _check_company_orderpoint_id(self):
        for order in self.sudo():
            if order.company_id and order.orderpoint_id.company_id and \
                    order.company_id != order.orderpoint_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Order and in '
                      'Warehouse Orderpoint must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProcurementOrder, self)._check_company_id()
        for rec in self:
            move = self.env['stock.move'].search(
                [('procurement_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Procurement Order is assigned to Move '
                      '%s.' % move.name))
