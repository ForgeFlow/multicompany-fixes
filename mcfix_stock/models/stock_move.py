from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(StockMove, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.model
    def create(self, vals):
        if vals.get('picking_id') and not vals.get('company_id'):
            picking = self.env['stock.picking'].browse(vals['picking_id'])
            vals['company_id'] = \
                picking.picking_type_id.warehouse_id.company_id.id
        return super(StockMove, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.origin_returned_move_id:
            if self.company_id and self.picking_id.company_id and \
                    self.picking_id.company_id != self.company_id:
                self.picking_id.company_id = self.company_id
            if self.company_id and self.product_id.company_id and \
                    self.product_id.company_id != self.company_id:
                self._cache.update(self._convert_to_cache(
                    {'product_id': False}, update=True))
            # if self.company_id and self.restrict_partner_id.company_id and \
            #         self.restrict_partner_id.company_id != self.company_id:
            #     self.restrict_partner_id = False
            if self.company_id and self.location_id.company_id and \
                    self.location_id.company_id != self.company_id:
                if self.picking_id.location_id:
                    self.location_id = self.picking_id.location_id
                else:
                    self._cache.update(self._convert_to_cache(
                        {'location_id': False}, update=True))
            if self.company_id and self.partner_id.company_id and \
                    self.partner_id.company_id != self.company_id:
                self.partner_id = self.picking_id.partner_id
            if self.company_id and self.location_dest_id.company_id and \
                    self.location_dest_id.company_id != self.company_id:
                if self.picking_id.location_dest_id:
                    self.location_dest_id = self.picking_id.location_dest_id
                else:
                    self._cache.update(self._convert_to_cache(
                        {'location_dest_id': False}, update=True))
            if self.company_id and self.inventory_id.company_id and \
                    self.inventory_id.company_id != self.company_id:
                self.inventory_id = False
            if self.company_id and self.rule_id.company_id and \
                    self.rule_id.company_id != self.company_id:
                self.rule_id = False
            if self.company_id and self.push_rule_id.company_id and \
                    self.push_rule_id.company_id != self.company_id:
                self.push_rule_id = False
            if self.company_id and self.move_orig_ids:
                self.move_orig_ids = self.env['stock.move'].search(
                    [('move_dest_ids', 'in', [self.id]),
                     ('company_id', '=', False),
                     ('company_id', '=', self.company_id.id)])
            if self.company_id and self.move_dest_ids:
                self.move_dest_ids = self.env['stock.move'].search(
                    [('move_orig_ids', 'in', [self.id]),
                     ('company_id', '=', False),
                     ('company_id', '=', self.company_id.id)])

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.warehouse_id.company_id and\
                    rec.company_id != rec.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Product Product must be the same.'))

    @api.multi
    @api.constrains('company_id', 'picking_id')
    def _check_company_id_picking_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.picking_id.company_id and\
                    rec.company_id != rec.picking_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Picking must be the same.'))

    @api.multi
    @api.constrains('company_id', 'restrict_partner_id')
    def _check_company_id_restrict_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.restrict_partner_id.company_id and\
                    rec.company_id != rec.restrict_partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'rule_id')
    def _check_company_id_rule_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.rule_id.company_id and\
                    rec.company_id != rec.rule_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Procurement Rule must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'inventory_id')
    def _check_company_id_inventory_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.inventory_id.company_id and\
                    rec.company_id != rec.inventory_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Inventory must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_dest_id')
    def _check_company_id_location_dest_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_dest_id.company_id and\
                    rec.company_id != rec.location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Move and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'push_rule_id')
    def _check_company_id_push_rule_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.push_rule_id.company_id and\
                    rec.company_id != rec.push_rule_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Location Path must be the same.'))

    @api.multi
    @api.constrains('company_id', 'origin_returned_move_id')
    def _check_company_id_origin_returned_move_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.origin_returned_move_id.company_id and\
                    rec.company_id != rec.origin_returned_move_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Move and in '
                      'Stock Move must be the same.'))

    @api.multi
    @api.constrains('company_id', 'move_orig_ids')
    def _check_company_id_move_orig_ids(self):
        for rec in self.sudo():
            for line in rec.move_orig_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Move and in '
                          'Stock Move (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.multi
    @api.constrains('company_id', 'move_dest_ids')
    def _check_company_id_move_dest_ids(self):
        for rec in self.sudo():
            for line in rec.move_dest_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Stock Move and in '
                          'Stock Move (%s) must be the same.'
                          ) % line.name_get()[0][1])

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.search(
                    [('origin_returned_move_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Move is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('move_orig_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Move is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.search(
                    [('move_dest_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Move is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.location.route'].search(
                    [('move_ids', 'in', [rec.id]),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Move is assigned to Stock Location Route '
                          '(%s).' % field.name_get()[0][1]))


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    company_id = fields.Many2one(
        'res.company', compute='_compute_company_id', string='Company',
        readonly=True, store=False)

    @api.one
    @api.depends('move_id')
    def _compute_company_id(self):
        if self.move_id:
            self.company_id = self.move_id.company_id
        else:
            self.company_id = self.env.user.company_id
