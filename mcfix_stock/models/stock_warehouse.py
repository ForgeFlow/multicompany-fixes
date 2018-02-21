from odoo import api, models, _
from odoo.exceptions import ValidationError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = self.company_id.partner_id
        if self.company_id and self.default_resupply_wh_id.company_id and \
                self.default_resupply_wh_id.company_id != self.company_id:
            self.default_resupply_wh_id = False
        if self.company_id and self.resupply_wh_ids:
            self.resupply_wh_ids = self.env['stock.warehouse'].search(
                [('resupply_wh_ids', 'in', [self.id]),
                 ('company_id', '=', False),
                 ('company_id', '=', self.company_id.id)])
        if self.company_id and self.route_ids:
            self.route_ids = self.env['stock.location.route'].search(
                [('warehouse_selectable', '=', True),
                 ('warehouse_ids', 'in', [self.id]),
                 ('company_id', '=', False),
                 ('company_id', '=', self.company_id.id)])
        # if self.company_id and self.wh_input_stock_loc_id.company_id and \
        #         self.wh_input_stock_loc_id.company_id != self.company_id:
        #     self.wh_input_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_input_stock_loc_id
        # if self.company_id and self.crossdock_route_id.company_id and \
        #         self.crossdock_route_id.company_id != self.company_id:
        #     self.crossdock_route_id = self.default_resupply_wh_id.\
        #         crossdock_route_id
        # if self.company_id and self.wh_qc_stock_loc_id.company_id and \
        #         self.wh_qc_stock_loc_id.company_id != self.company_id:
        #     self.wh_qc_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_qc_stock_loc_id
        # if self.company_id and self.reception_route_id.company_id and \
        #         self.reception_route_id.company_id != self.company_id:
        #     self.reception_route_id = self.default_resupply_wh_id.\
        #         reception_route_id
        # if self.company_id and self.mto_pull_id.company_id and \
        #         self.mto_pull_id.company_id != self.company_id:
        #     self.mto_pull_id = self.default_resupply_wh_id.mto_pull_id
        # if self.company_id and self.view_location_id.company_id and \
        #         self.view_location_id.company_id != self.company_id:
        #     self.view_location_id = self.default_resupply_wh_id.\
        #         view_location_id
        # if self.company_id and self.wh_output_stock_loc_id.company_id and \
        #         self.wh_output_stock_loc_id.company_id != self.company_id:
        #     self.wh_output_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_output_stock_loc_id
        # if self.company_id and self.lot_stock_id.company_id and \
        #         self.lot_stock_id.company_id != self.company_id:
        #     self.lot_stock_id = self.default_resupply_wh_id.lot_stock_id
        # if self.company_id and self.wh_pack_stock_loc_id.company_id \
        #         and self.wh_pack_stock_loc_id.company_id != self.company_id:
        #     self.wh_pack_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_pack_stock_loc_id
        # if self.company_id and self.delivery_route_id.company_id and \
        #         self.delivery_route_id.company_id != self.company_id:
        #     self.delivery_route_id = self.default_resupply_wh_id.\
        #         delivery_route_id

    @api.multi
    @api.constrains('company_id', 'wh_input_stock_loc_id')
    def _check_company_id_wh_input_stock_loc_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.wh_input_stock_loc_id.company_id and\
                    rec.company_id != rec.wh_input_stock_loc_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'crossdock_route_id')
    def _check_company_id_crossdock_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.crossdock_route_id.company_id and\
                    rec.company_id != rec.crossdock_route_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Warehouse and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'default_resupply_wh_id')
    def _check_company_id_default_resupply_wh_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.default_resupply_wh_id.company_id and\
                    rec.company_id != rec.default_resupply_wh_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_qc_stock_loc_id')
    def _check_company_id_wh_qc_stock_loc_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.wh_qc_stock_loc_id.company_id and\
                    rec.company_id != rec.wh_qc_stock_loc_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'reception_route_id')
    def _check_company_id_reception_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.reception_route_id.company_id and\
                    rec.company_id != rec.reception_route_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'mto_pull_id')
    def _check_company_id_mto_pull_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.mto_pull_id.company_id and\
                    rec.company_id != rec.mto_pull_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Procurement Rule must be the same.'))

    @api.multi
    @api.constrains('company_id', 'view_location_id')
    def _check_company_id_view_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.view_location_id.company_id and\
                    rec.company_id != rec.view_location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_output_stock_loc_id')
    def _check_company_id_wh_output_stock_loc_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.wh_output_stock_loc_id.company_id and\
                    rec.company_id != rec.wh_output_stock_loc_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'lot_stock_id')
    def _check_company_id_lot_stock_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.lot_stock_id.company_id and\
                    rec.company_id != rec.lot_stock_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_pack_stock_loc_id')
    def _check_company_id_wh_pack_stock_loc_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.wh_pack_stock_loc_id.company_id and\
                    rec.company_id != rec.wh_pack_stock_loc_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'resupply_wh_ids')
    def _check_company_id_resupply_wh_ids(self):
        for rec in self.sudo():
            for line in rec.resupply_wh_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Warehouse and in '
                          'Stock Warehouse (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'delivery_route_id')
    def _check_company_id_delivery_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.delivery_route_id.company_id and\
                    rec.company_id != rec.delivery_route_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.warehouse.orderpoint'].search(
                    [('warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to '
                          'Stock Warehouse Orderpoint (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.location.path'].search(
                    [('warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Stock Location Path '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.location.route'].search(
                    [('supplier_wh_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to '
                          'Stock Location Route (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.location.route'].search(
                    [('supplied_wh_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to '
                          'Stock Location Route (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.location.route'].search(
                    [('warehouse_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to '
                          'Stock Location Route (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['product.template'].search(
                    [('warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Product Template '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('resupply_wh_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('default_resupply_wh_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['procurement.rule'].search(
                    [('warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Procurement Rule '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['procurement.rule'].search(
                    [('propagate_warehouse_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Warehouse is assigned to Procurement Rule '
                          '(%s).' % field.name_get()[0][1]))


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.product_id.company_id and \
                self.product_id.company_id != self.company_id:
            self.product_id = False
        if self.company_id and self.warehouse_id.company_id and \
                self.warehouse_id.company_id != self.company_id:
            self.warehouse_id = self.product_id.warehouse_id
        if self.company_id and self.location_id.company_id and \
                self.location_id.company_id != self.company_id:
            self.location_id = self.product_id.location_id

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.warehouse_id.company_id and\
                    rec.company_id != rec.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Product Product must be the same.'))
