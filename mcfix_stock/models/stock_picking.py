from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    company_id = fields.Many2one(
        'res.company', related='warehouse_id.company_id', string='Company',
        readonly=True, default=lambda self: self.env.user.company_id)

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(PickingType, self).name_get()
        res = self.add_company_suffix(names)
        return res


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
            if not self.picking_type_id.warehouse_id.check_company(
                self.company_id
            ):
                self.picking_type_id = self.env['stock.picking.type'].search(
                    [('code', '=', self.picking_type_id.code),
                     ('warehouse_id.company_id', '=', self.company_id.id)],
                    limit=1)
                if not self.picking_type_id:
                    self.picking_type_id = self.env['stock.picking.type'].\
                        search(
                        [('code', '=', self.picking_type_id.code),
                         ('warehouse_id', '=', False)],
                        limit=1)
            if not self.partner_id.check_company(self.company_id):
                self.partner_id = False
            if not self.location_id.check_company(self.company_id):
                self.location_id = False
            if not self.location_dest_id.check_company(self.company_id):
                self.location_dest_id = False
            if not self.owner_id.check_company(self.company_id):
                self.owner_id = False
            if self.company_id and self.move_lines:
                for line in self.move_lines:
                    if line.check_company(self.company_id):
                        line.company_id = self.company_id

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_dest_id')
    def _check_company_id_location_dest_id(self):
        for rec in self.sudo():
            if not rec.location_dest_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'owner_id')
    def _check_company_id_owner_id(self):
        for rec in self.sudo():
            if not rec.owner_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'backorder_id')
    def _check_company_id_backorder_id(self):
        for rec in self.sudo():
            if not rec.backorder_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Stock Picking and in '
                      'Stock Picking must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.move_lines, self.move_line_ids, ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.picking', [('backorder_id', '=', self.id)]),
            ('stock.scrap', [('picking_id', '=', self.id)]),
        ]
        return res
