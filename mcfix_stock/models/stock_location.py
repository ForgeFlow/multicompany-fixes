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
        if not self.location_id.check_company(self.company_id):
            self.location_id = False
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Location and in '
                      'Res Partner must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.child_ids, self.quant_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.rule', [('location_id', '=', self.id)]),
            ('stock.rule', [('location_src_id', '=', self.id)]),
            ('stock.inventory', [('location_id', '=', self.id)]),
            ('stock.inventory.line', [('location_id', '=', self.id)]),
            ('stock.move', [('location_id', '=', self.id)]),
            ('stock.move', [('location_dest_id', '=', self.id)]),
            ('stock.move.line', [('location_id', '=', self.id)]),
            ('stock.move.line', [('location_dest_id', '=', self.id)]),
            ('stock.picking', [('location_id', '=', self.id)]),
            ('stock.picking', [('location_dest_id', '=', self.id)]),
            ('stock.picking.type',
             [('default_location_dest_id', '=', self.id)]),
            ('stock.picking.type',
             [('default_location_src_id', '=', self.id)]),
            ('stock.scrap', [('location_id', '=', self.id)]),
            ('stock.scrap', [('scrap_location_id', '=', self.id)]),
            ('stock.warehouse', [('wh_output_stock_loc_id', '=', self.id)]),
            ('stock.warehouse', [('wh_qc_stock_loc_id', '=', self.id)]),
            ('stock.warehouse', [('lot_stock_id', '=', self.id)]),
            ('stock.warehouse', [('wh_input_stock_loc_id', '=', self.id)]),
            ('stock.warehouse', [('view_location_id', '=', self.id)]),
            ('stock.warehouse', [('wh_pack_stock_loc_id', '=', self.id)]),
            ('stock.warehouse.orderpoint', [('location_id', '=', self.id)]),
        ]
        return res


class Route(models.Model):
    _inherit = 'stock.location.route'

    move_ids = fields.Many2many('stock.move',
                                'stock_location_route_move', 'route_id',
                                'move_id', 'Moves',
                                help="Related moves")

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.move_ids:
            # if not self.supplied_wh_id.check_company(self.company_id):
            #     self.supplied_wh_id = False
            # if not self.supplier_wh_id.check_company(self.company_id):
            #     self.supplier_wh_id = False
            if not self.product_ids.check_company(self.company_id):
                self.product_ids = self.env['product.template'].search(
                    [('route_ids', 'in', [self.id]),
                     ('company_id', '=', False),
                     ('company_id', '=', self.company_id.id)])
            if not self.warehouse_ids.check_company(self.company_id):
                if self.company_id and self.warehouse_ids:
                    self.warehouse_ids = self.warehouse_ids.filtered(
                        lambda w: w.company_id == self.company_id)

    @api.multi
    @api.constrains('company_id', 'move_ids')
    def _check_company_id_move_ids(self):
        for rec in self.sudo():
            for line in rec.move_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Stock Move (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'supplier_wh_id')
    def _check_company_id_supplier_wh_id(self):
        for rec in self.sudo():
            if not rec.supplier_wh_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Location Route and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_ids')
    def _check_company_id_product_ids(self):
        for rec in self.sudo():
            for line in rec.product_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Product Template (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'supplied_wh_id')
    def _check_company_id_supplied_wh_id(self):
        for rec in self.sudo():
            if not rec.supplied_wh_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Location Route and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_ids')
    def _check_company_id_warehouse_ids(self):
        for rec in self.sudo():
            for line in rec.warehouse_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Stock Location Route and in '
                          'Stock Warehouse (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.move_ids, self.warehouse_ids,
        ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.move', [('route_ids', 'in', self.ids)]),
            ('stock.warehouse', [('crossdock_route_id', '=', self.id)]),
            ('stock.warehouse', [('delivery_route_id', '=', self.id)]),
            ('stock.warehouse', [('route_ids', 'in', self.ids)]),
            ('stock.warehouse', [('reception_route_id', '=', self.id)]),
        ]
        return res
