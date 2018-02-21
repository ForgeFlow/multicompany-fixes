from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Location(models.Model):
    _inherit = "stock.location"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(Location, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def _get_top_parent(self):
        parent = self.env['stock.location']
        for location in self:
            if location.location_id:
                if location.location_id.usage and \
                        location.location_id.usage == 'view':
                    parent |= self
                else:
                    parent |= location.location_id._get_top_parent()
            else:
                parent |= self
        return parent

    @api.multi
    def _get_all_children(self):
        childs = self
        for location in self:
            child_ids = self.search(
                [('location_id', '=', location.id)])
            if child_ids:
                childs |= child_ids._get_all_children()
        return childs

    @api.multi
    def write(self, vals):
        company = False
        if vals.get('company_id') and \
                not self._context.get('stop_recursion_company'):
            company = vals['company_id']
            del vals['company_id']
        result = super(Location, self).write(vals)
        if company and not self._context.get('stop_recursion_company'):
            top_parent = self._get_top_parent()
            locations = top_parent._get_all_children()
            locations = locations.filtered(lambda t: t.company_id)
            locations |= self
            result = result and locations.with_context(
                stop_recursion_company=True).write(
                {'company_id': company})
        return result

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.location_id.company_id and \
                self.location_id.company_id != self.company_id:
            self.location_id = False
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Res Partner must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.warehouse.orderpoint'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to '
                          'Stock Warehouse Orderpoint (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.location.path'].search(
                    [('location_dest_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Location Path '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.location.path'].search(
                    [('location_from_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Location Path '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.inventory.line'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Inventory Line '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.picking'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Picking '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.picking'].search(
                    [('location_dest_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Picking '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.inventory'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Inventory '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['product.template'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Product Template '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('wh_input_stock_loc_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('wh_output_stock_loc_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('lot_stock_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('wh_pack_stock_loc_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('wh_qc_stock_loc_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('view_location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('location_dest_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Location '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['procurement.rule'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Procurement Rule '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['procurement.rule'].search(
                    [('location_src_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Procurement Rule '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.quant'].search(
                    [('location_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location is assigned to Stock Quant '
                          '(%s).' % field.name_get()[0][1]))


class PushedFlow(models.Model):
    _inherit = "stock.location.path"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.route_id.company_id and \
                self.route_id.company_id != self.company_id:
            self.route_id.company_id = self.company_id
        # if self.company_id and self.warehouse_id.company_id and \
        #         self.warehouse_id.company_id != self.company_id:
        #     self.warehouse_id = self.picking_type_id.warehouse_id
        if self.company_id and self.location_from_id.company_id and \
                self.location_from_id.company_id != self.company_id:
            self.location_from_id = False
        if self.company_id and self.location_dest_id.company_id and \
                self.location_dest_id.company_id != self.company_id:
            self.location_dest_id = False

    @api.multi
    @api.constrains('company_id', 'route_id')
    def _check_company_id_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.route_id.company_id and\
                    rec.company_id != rec.route_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Path and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_dest_id')
    def _check_company_id_location_dest_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_dest_id.company_id and\
                    rec.company_id != rec.location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Path and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.warehouse_id.company_id and\
                    rec.company_id != rec.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Path and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_from_id')
    def _check_company_id_location_from_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_from_id.company_id and\
                    rec.company_id != rec.location_from_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Path and in '
                      'Stock Location must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.move'].search(
                    [('push_rule_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Path is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))


class Route(models.Model):
    _inherit = 'stock.location.route'

    move_ids = fields.Many2many('stock.move',
                                'stock_location_route_move', 'route_id',
                                'move_id', 'Moves',
                                help="Related moves")

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.move_ids:
            # if self.company_id and self.supplied_wh_id.company_id and \
            #         self.supplied_wh_id.company_id != self.company_id:
            #     self.supplied_wh_id = False
            # if self.company_id and self.supplier_wh_id.company_id and \
            #         self.supplier_wh_id.company_id != self.company_id:
            #     self.supplier_wh_id = False
            if self.company_id and self.product_ids:
                self.product_ids = self.env['product.template'].search(
                    [('route_ids', 'in', [self.id]),
                     ('company_id', '=', False),
                     ('company_id', '=', self.company_id.id)])
            if self.company_id and self.warehouse_ids:
                if self.company_id and self.warehouse_ids:
                    self.warehouse_ids = self.warehouse_ids.filtered(
                        lambda w: w.company_id == self.company_id)

    @api.multi
    @api.constrains('company_id', 'move_ids')
    def _check_company_id_move_ids(self):
        for rec in self.sudo():
            for line in rec.move_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Stock Move (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'supplier_wh_id')
    def _check_company_id_supplier_wh_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.supplier_wh_id.company_id and\
                    rec.company_id != rec.supplier_wh_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Route and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_ids')
    def _check_company_id_product_ids(self):
        for rec in self.sudo():
            for line in rec.product_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Product Template (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'supplied_wh_id')
    def _check_company_id_supplied_wh_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.supplied_wh_id.company_id and\
                    rec.company_id != rec.supplied_wh_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Location Route and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_ids')
    def _check_company_id_warehouse_ids(self):
        for rec in self.sudo():
            for line in rec.warehouse_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Stock Warehouse (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.location.path'].search(
                    [('route_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Stock Location Path (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['product.template'].search(
                    [('route_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Product Template (%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('crossdock_route_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Stock Warehouse (%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('route_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Stock Warehouse (%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('reception_route_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Stock Warehouse (%s).' % field.name_get()[0][1]))
                field = self.env['stock.warehouse'].search(
                    [('delivery_route_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Stock Warehouse (%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('route_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['procurement.rule'].search(
                    [('route_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Location Route is assigned to '
                          'Procurement Rule (%s).' % field.name_get()[0][1]))
