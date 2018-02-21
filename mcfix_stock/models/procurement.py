from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        # if self.company_id and self.location_src_id.company_id and \
        #         self.location_src_id.company_id != self.company_id:
        #     self.location_src_id = False
        if self.company_id and self.location_id.company_id and \
                self.location_id.company_id != self.company_id:
            self.location_id = self.location_src_id.location_id
        if self.company_id and self.route_id.company_id and \
                self.route_id.company_id != self.company_id:
            self.route_id.company_id = self.company_id
        # if self.company_id and self.partner_address_id.company_id and \
        #         self.partner_address_id.company_id != self.company_id:
        #     self.partner_address_id = False
        if self.company_id and self.warehouse_id.company_id and \
                self.warehouse_id.company_id != self.company_id:
            self.warehouse_id = self.picking_type_id.warehouse_id
        if self.company_id and self.propagate_warehouse_id.company_id \
                and self.propagate_warehouse_id.company_id != self.company_id:
            self.propagate_warehouse_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'route_id')
    def _check_company_id_route_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.route_id.company_id and\
                    rec.company_id != rec.route_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_address_id')
    def _check_company_id_partner_address_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_address_id.company_id and\
                    rec.company_id != rec.partner_address_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.warehouse_id.company_id and\
                    rec.company_id != rec.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'propagate_warehouse_id')
    def _check_company_id_propagate_warehouse_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.propagate_warehouse_id.company_id and\
                    rec.company_id != rec.propagate_warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_src_id')
    def _check_company_id_location_src_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_src_id.company_id and\
                    rec.company_id != rec.location_src_id.company_id:
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.warehouse'].search(
                    [('mto_pull_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Procurement Rule is assigned to Stock Warehouse '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('rule_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Procurement Rule is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))
