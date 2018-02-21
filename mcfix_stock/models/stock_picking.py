from odoo import api, models, _
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        super(Picking, self).onchange_picking_type()
        if self.picking_type_id:
            self.company_id = self.picking_type_id.warehouse_id.company_id.id

    @api.model
    def create(self, vals):
        defaults = self.default_get(['picking_type_id'])
        if not vals.get('company_id'):
            vals['company_id'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).\
                warehouse_id.company_id.id
        return super(Picking, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.backorder_id:
            if self.company_id and self.picking_type_id.warehouse_id.\
                    company_id and self.picking_type_id.warehouse_id.\
                    company_id != self.company_id:
                self._cache.update(self._convert_to_cache(
                    {'picking_type_id': False}, update=True))
            if self.company_id and self.partner_id.company_id and \
                    self.partner_id.company_id != self.company_id:
                self.partner_id = False
            if self.company_id and self.location_id.company_id and \
                    self.location_id.company_id != self.company_id:
                self.location_id = False
            if self.company_id and self.location_dest_id.company_id and \
                    self.location_dest_id.company_id != self.company_id:
                self.location_dest_id = False
            if self.company_id and self.owner_id.company_id and \
                    self.owner_id.company_id != self.company_id:
                self.owner_id = False
            if self.company_id and self.move_lines:
                for line in self.move_lines:
                    if line.company_id and line.company_id != self.company_id:
                        line.company_id = self.company_id

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and\
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_dest_id')
    def _check_company_id_location_dest_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_dest_id.company_id and\
                    rec.company_id != rec.location_dest_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'owner_id')
    def _check_company_id_owner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.owner_id.company_id and\
                    rec.company_id != rec.owner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'backorder_id')
    def _check_company_id_backorder_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.backorder_id.company_id and\
                    rec.company_id != rec.backorder_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Picking must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.search(
                    [('backorder_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Picking is assigned to Stock Picking '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('picking_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Picking is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
