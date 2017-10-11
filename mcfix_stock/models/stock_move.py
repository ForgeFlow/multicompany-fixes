# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockMove, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.product_tmpl_id = False
        self.location_id = False
        self.location_dest_id = False
        self.move_dest_id = False
        self.picking_id = False
        self.split_from = False
        self.backorder_id = False
        self.quant_ids = False
        self.procurement_id = False
        self.rule_id = False
        self.push_rule_id = False
        self.inventory_id = False
        self.origin_returned_move_id = False
        self.route_ids = False
        self.warehouse_id = False

    @api.multi
    @api.constrains('product_tmpl_id', 'company_id')
    def _check_company_product_tmpl_id(self):
        for move in self.sudo():
            if move.company_id and move.product_tmpl_id.company_id and \
                    move.company_id != move.product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Product Template must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for move in self.sudo():
            if move.company_id and move.location_id.company_id and \
                    move.company_id != move.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('location_dest_id', 'company_id')
    def _check_company_location_dest_id(self):
        for move in self.sudo():
            if move.company_id and move.location_dest_id.company_id and \
                    move.company_id != move.location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('move_dest_id', 'company_id')
    def _check_company_move_dest_id(self):
        for move in self.sudo():
            if move.company_id and move.move_dest_id.company_id and \
                    move.company_id != move.move_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Move Destination must be the same.'))
        return True

    @api.multi
    @api.constrains('picking_id', 'company_id')
    def _check_company_picking_id(self):
        for move in self.sudo():
            if move.company_id and move.picking_id.company_id and \
                    move.company_id != move.picking_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Picking must be the same.'))
        return True

    @api.multi
    @api.constrains('split_from', 'company_id')
    def _check_company_split_from(self):
        for move in self.sudo():
            if move.company_id and move.split_from.company_id and \
                    move.company_id != move.split_from.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Move Split From must be the same.'))
        return True

    @api.multi
    @api.constrains('backorder_id', 'company_id')
    def _check_company_backorder_id(self):
        for move in self.sudo():
            if move.company_id and move.backorder_id.company_id and \
                    move.company_id != move.backorder_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Backorder must be the same.'))
        return True

    @api.multi
    @api.constrains('quant_ids', 'company_id')
    def _check_company_quant_ids(self):
        for move in self.sudo():
            for stock_quant in move.quant_ids:
                if move.company_id and stock_quant.company_id and \
                        move.company_id != stock_quant.company_id:
                    raise ValidationError(
                        _('The Company in the Move and in '
                          'Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('procurement_id', 'company_id')
    def _check_company_procurement_id(self):
        for move in self.sudo():
            if move.company_id and move.procurement_id.company_id and \
                    move.company_id != move.procurement_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Procurement must be the same.'))
        return True

    @api.multi
    @api.constrains('rule_id', 'company_id')
    def _check_company_rule_id(self):
        for move in self.sudo():
            if move.company_id and move.rule_id.company_id and \
                    move.company_id != move.rule_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Rule must be the same.'))
        return True

    @api.multi
    @api.constrains('push_rule_id', 'company_id')
    def _check_company_push_rule_id(self):
        for move in self.sudo():
            if move.company_id and move.push_rule_id.company_id and \
                    move.company_id != move.push_rule_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Push Rule must be the same.'))
        return True

    @api.multi
    @api.constrains('inventory_id', 'company_id')
    def _check_company_inventory_id(self):
        for move in self.sudo():
            if move.company_id and move.inventory_id.company_id and \
                    move.company_id != move.inventory_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Inventory must be the same.'))
        return True

    @api.multi
    @api.constrains('origin_returned_move_id', 'company_id')
    def _check_company_origin_returned_move_id(self):
        for move in self.sudo():
            if move.company_id and move.origin_returned_move_id.company_id and\
                    move.company_id != move.origin_returned_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Origin Return Move must be the same.'))
        return True

    @api.multi
    @api.constrains('route_ids', 'company_id')
    def _check_company_route_ids(self):
        for move in self.sudo():
            for stock_location_route in move.route_ids:
                if move.company_id and stock_location_route.company_id and \
                        move.company_id != stock_location_route.company_id:
                    raise ValidationError(
                        _('The Company in the Move and in '
                          'Location Route must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for move in self.sudo():
            if move.company_id and move.warehouse_id.company_id and \
                    move.company_id != move.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Move and in '
                      'Warehouse must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            order = self.env['procurement.order'].search(
                [('move_dest_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Procurement Order '
                      '%s.' % order.name))
            quant = self.env['stock.quant'].search(
                [('reservation_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Quant '
                      '%s.' % quant.name))
            quant = self.env['stock.quant'].search(
                [('history_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Quant '
                      '%s.' % quant.name))
            quant = self.env['stock.quant'].search(
                [('negative_move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Quant '
                      '%s.' % quant.name))
            move = self.search(
                [('move_dest_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Move '
                      '%s.' % move.name))
            move = self.search(
                [('split_from', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Move '
                      '%s.' % move.name))
            move = self.search(
                [('origin_returned_move_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Move is assigned to Move '
                      '%s.' % move.name))
