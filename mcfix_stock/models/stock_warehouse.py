from odoo import api, models, _
from odoo.exceptions import ValidationError


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.name:
            self.name = self.company_id.name
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = self.company_id.partner_id
        if not self.default_resupply_wh_id.check_company(self.company_id):
            self.default_resupply_wh_id = False
        if not self.resupply_wh_ids.check_company(self.company_id):
            self.resupply_wh_ids = self.env['stock.warehouse'].search(
                [('resupply_wh_ids', 'in', [self.id]),
                 ('company_id', '=', False),
                 ('company_id', '=', self.company_id.id)])
        if not self.route_ids.check_company(self.company_id):
            self.route_ids = self.env['stock.location.route'].search(
                [('warehouse_selectable', '=', True),
                 ('warehouse_ids', 'in', [self.id]),
                 ('company_id', '=', False),
                 ('company_id', '=', self.company_id.id)])
        # if not self.wh_input_stock_loc_id.check_company(self.company_id):
        #     self.wh_input_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_input_stock_loc_id
        # if not self.crossdock_route_id.check_company(self.company_id):
        #     self.crossdock_route_id = self.default_resupply_wh_id.\
        #         crossdock_route_id
        # if not self.wh_qc_stock_loc_id.check_company(self.company_id):
        #     self.wh_qc_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_qc_stock_loc_id
        # if not self.reception_route_id.check_company(self.company_id):
        #     self.reception_route_id = self.default_resupply_wh_id.\
        #         reception_route_id
        # if not self.mto_pull_id.check_company(self.company_id):
        #     self.mto_pull_id = self.default_resupply_wh_id.mto_pull_id
        # if not self.view_location_id.check_company(self.company_id):
        #     self.view_location_id = self.default_resupply_wh_id.\
        #         view_location_id
        # if not self.wh_output_stock_loc_id.check_company(self.company_id):
        #     self.wh_output_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_output_stock_loc_id
        # if not self.lot_stock_id.check_company(self.company_id):
        #     self.lot_stock_id = self.default_resupply_wh_id.lot_stock_id
        # if not self.wh_pack_stock_loc_id.check_company(self.company_id)::
        #     self.wh_pack_stock_loc_id = self.default_resupply_wh_id.\
        #         wh_pack_stock_loc_id
        # if not self.delivery_route_id.check_company(self.company_id):
        #     self.delivery_route_id = self.default_resupply_wh_id.\
        #         delivery_route_id

    @api.multi
    @api.constrains('company_id', 'wh_input_stock_loc_id')
    def _check_company_id_wh_input_stock_loc_id(self):
        for rec in self.sudo():
            if not rec.wh_input_stock_loc_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'crossdock_route_id')
    def _check_company_id_crossdock_route_id(self):
        for rec in self.sudo():
            if not rec.crossdock_route_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Stock Warehouse and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'default_resupply_wh_id')
    def _check_company_id_default_resupply_wh_id(self):
        for rec in self.sudo():
            if not rec.default_resupply_wh_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_qc_stock_loc_id')
    def _check_company_id_wh_qc_stock_loc_id(self):
        for rec in self.sudo():
            if not rec.wh_qc_stock_loc_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'reception_route_id')
    def _check_company_id_reception_route_id(self):
        for rec in self.sudo():
            if not rec.reception_route_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'mto_pull_id')
    def _check_company_id_mto_pull_id(self):
        for rec in self.sudo():
            if not rec.mto_pull_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Procurement Rule must be the same.'))

    @api.multi
    @api.constrains('company_id', 'view_location_id')
    def _check_company_id_view_location_id(self):
        for rec in self.sudo():
            if not rec.view_location_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_output_stock_loc_id')
    def _check_company_id_wh_output_stock_loc_id(self):
        for rec in self.sudo():
            if not rec.wh_output_stock_loc_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'lot_stock_id')
    def _check_company_id_lot_stock_id(self):
        for rec in self.sudo():
            if not rec.lot_stock_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'wh_pack_stock_loc_id')
    def _check_company_id_wh_pack_stock_loc_id(self):
        for rec in self.sudo():
            if not rec.wh_pack_stock_loc_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'resupply_wh_ids')
    def _check_company_id_resupply_wh_ids(self):
        for rec in self.sudo():
            for line in rec.resupply_wh_ids:
                if not line.check_company(rec.company_id):
                    raise ValidationError(
                        _('The Company in the Stock Warehouse and in '
                          'Stock Warehouse (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'delivery_route_id')
    def _check_company_id_delivery_route_id(self):
        for rec in self.sudo():
            if not rec.delivery_route_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Warehouse and in '
                      'Stock Location Route must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.route_ids, self.resupply_route_ids, self.resupply_wh_ids]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('procurement.rule', [('propagate_warehouse_id', '=', self.id)]),
            ('procurement.rule', [('warehouse_id', '=', self.id)]),
            ('stock.location.path', [('warehouse_id', '=', self.id)]),
            ('stock.location.route', [('warehouse_ids', 'in', self.ids)]),
            ('stock.move', [('warehouse_id', '=', self.id)]),
            ('stock.picking.type', [('warehouse_id', '=', self.id)]),
            ('stock.warehouse', [('default_resupply_wh_id', '=', self.id)]),
            ('stock.warehouse', [('resupply_wh_ids', 'in', self.ids)]),
            ('stock.warehouse.orderpoint', [('warehouse_id', '=', self.id)]),
        ]
        return res


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.product_id.check_company(self.company_id):
            self.product_id = False
        if not self.warehouse_id.check_company(self.company_id):
            self.warehouse_id = self.product_id.warehouse_id
        if not self.location_id.check_company(self.company_id):
            self.location_id = self.product_id.location_id

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if not rec.warehouse_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Warehouse Orderpoint and in '
                      'Product Product must be the same.'))
