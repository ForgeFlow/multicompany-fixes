# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockLocationPath(models.Model):
    _inherit = 'stock.location.path'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockLocationPath, self).name_get()
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
        self.route_id = False
        self.location_from_id = False
        self.location_dest_id = False
        self.warehouse_id = False

    @api.multi
    @api.constrains('route_id', 'company_id')
    def _check_company_route_id(self):
        for location_path in self.sudo():
            if location_path.company_id and location_path.route_id.company_id\
                    and location_path.company_id != location_path.route_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Location Path and in '
                      'Location Route must be the same.'))
        return True

    @api.multi
    @api.constrains('location_from_id', 'company_id')
    def _check_company_location_from_id(self):
        for location_path in self.sudo():
            if location_path.company_id and location_path.location_from_id.\
                    company_id and location_path.company_id != location_path.\
                    location_from_id.company_id:
                raise ValidationError(
                    _('The Company in the Location Path and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('location_dest_id', 'company_id')
    def _check_company_location_dest_id(self):
        for location_path in self.sudo():
            if location_path.company_id and location_path.location_dest_id.\
                    company_id and location_path.company_id != location_path.\
                    location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Location Path and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for location_path in self.sudo():
            if location_path.company_id and location_path.warehouse_id.\
                    company_id and location_path.company_id != location_path.\
                    warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Location Path and in '
                      'Warehouse must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            move = self.env['stock.move'].search(
                [('push_rule_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Path is assigned to Move '
                      '%s.' % move.name))


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockLocationRoute, self).name_get()
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
        self.supplied_wh_id = False
        self.supplier_wh_id = False
        self.product_ids = False
        self.warehouse_ids = False

    @api.multi
    @api.constrains('supplied_wh_id', 'company_id')
    def _check_company_supplied_wh_id(self):
        for location_route in self.sudo():
            if location_route.company_id and location_route.supplied_wh_id.\
                    company_id and location_route.company_id != location_route\
                    .supplied_wh_id.company_id:
                raise ValidationError(
                    _('The Company in the Location Route and in '
                      'Supplied Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('supplier_wh_id', 'company_id')
    def _check_company_supplier_wh_id(self):
        for location_route in self.sudo():
            if location_route.company_id and location_route.supplier_wh_id.\
                    company_id and location_route.company_id != location_route\
                    .supplier_wh_id.company_id:
                raise ValidationError(
                    _('The Company in the Location Route and in '
                      'Supplying Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('product_ids', 'company_id')
    def _check_company_product_ids(self):
        for location_route in self.sudo():
            for product_template in location_route.product_ids:
                if location_route.company_id and product_template.company_id\
                        and location_route.company_id != product_template.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Location Route and in '
                          'Product Template must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_ids', 'company_id')
    def _check_company_warehouse_ids(self):
        for location_route in self.sudo():
            for stock_warehouse in location_route.warehouse_ids:
                if location_route.company_id and stock_warehouse.company_id \
                        and location_route.company_id != stock_warehouse.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Location Route and in '
                          'Warehouse must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            order = self.env['procurement.order'].search(
                [('route_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Procurement Order '
                      '%s.' % order.name))
            rule = self.env['procurement.rule'].search(
                [('route_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if rule:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Procurement Rule '
                      '%s.' % rule.name))
            location_path = self.env['stock.location.path'].search(
                [('route_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location_path:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Location Path '
                      '%s.' % location_path.name))
            move = self.env['stock.move'].search(
                [('route_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Move '
                      '%s.' % move.name))
            warehouse = self.env['stock.warehouse'].search(
                [('route_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('crossdock_route_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Crossdock Route is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('reception_route_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Reception Route is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('delivery_route_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Delivery Route is assigned to Warehouse '
                      '%s.' % warehouse.name))
            template = self.env['product.template'].search(
                [('route_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location Route is assigned to Product Template '
                      '%s.' % template.name))


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockLocation, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.location_id = False

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for location in self.sudo():
            if location.company_id and location.location_id.company_id and \
                    location.company_id != location.location_id.company_id:
                raise ValidationError(_('The Company in both Locations '
                                        'must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            order = self.env['procurement.order'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if order:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Procurement Order '
                      '%s.' % order.name))
            rule = self.env['procurement.rule'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if rule:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Procurement Rule '
                      '%s.' % rule.name))
            rule = self.env['procurement.rule'].search(
                [('location_src_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if rule:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Procurement Rule '
                      '%s.' % rule.name))
            inventory = self.env['stock.inventory'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if inventory:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Inventory '
                      '%s.' % inventory.name))
            inventory_line = self.env['stock.inventory.line'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if inventory_line:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Inventory Line '
                      '%s in Inventory %s.' % (
                          inventory_line.name,
                          inventory_line.inventory_id.name)))
            picking = self.env['stock.picking'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if picking:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Picking '
                      '%s.' % picking.name))
            picking = self.env['stock.picking'].search(
                [('location_dest_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if picking:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Picking '
                      '%s.' % picking.name))
            quant = self.env['stock.quant'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Quant '
                      '%s.' % quant.name))
            location = self.search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Location '
                      '%s.' % location.name))
            location_path = self.env['stock.location.path'].search(
                [('location_from_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location_path:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Location Path '
                      '%s.' % location_path.name))
            location_path = self.env['stock.location.path'].search(
                [('location_dest_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location_path:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Location Path '
                      '%s.' % location_path.name))
            move = self.env['stock.move'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Move '
                      '%s.' % move.name))
            move = self.env['stock.move'].search(
                [('location_dest_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if move:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Move '
                      '%s.' % move.name))
            warehouse = self.env['stock.warehouse'].search(
                [('view_location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('lot_stock_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('wh_input_stock_loc_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('wh_qc_stock_loc_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('wh_output_stock_loc_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse = self.env['stock.warehouse'].search(
                [('wh_pack_stock_loc_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse '
                      '%s.' % warehouse.name))
            warehouse_orderpoint = self.env[
                'stock.warehouse.orderpoint'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if warehouse_orderpoint:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Warehouse Orderpoint '
                      '%s.' % warehouse_orderpoint.name))
            template = self.env['product.template'].search(
                [('property_stock_procurement', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Product Template '
                      '%s.' % template.name))
            template = self.env['product.template'].search(
                [('property_stock_production', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Product Template '
                      '%s.' % template.name))
            template = self.env['product.template'].search(
                [('property_stock_inventory', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Product Template '
                      '%s.' % template.name))
            template = self.env['product.template'].search(
                [('location_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Location is assigned to Product Template '
                      '%s.' % template.name))
