from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        # if not self.location_src_id.check_company(self.company_id):
        #     self.location_src_id = False
        if not self.location_id.check_company(self.company_id):
            self.location_id = self.location_src_id.location_id
        if not self.route_id.check_company(self.company_id):
            self.route_id.company_id = self.company_id
        # if not self.partner_address_id.check_company(self.company_id):
        #     self.partner_address_id = False
        if not self.warehouse_id.check_company(self.company_id):
            self.warehouse_id = self.picking_type_id.warehouse_id
        if not self.propagate_warehouse_id.check_company(self.company_id):
            self.propagate_warehouse_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'route_id')
    def _check_company_id_route_id(self):
        for rec in self.sudo():
            if not rec.route_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location Route must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_address_id')
    def _check_company_id_partner_address_id(self):
        for rec in self.sudo():
            if not rec.partner_address_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'warehouse_id')
    def _check_company_id_warehouse_id(self):
        for rec in self.sudo():
            if not rec.warehouse_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'propagate_warehouse_id')
    def _check_company_id_propagate_warehouse_id(self):
        for rec in self.sudo():
            if not rec.propagate_warehouse_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Warehouse must be the same.'))

    @api.multi
    @api.constrains('company_id', 'location_src_id')
    def _check_company_id_location_src_id(self):
        for rec in self.sudo():
            if not rec.location_src_id.check_company(
                rec.company_id
            ):
                raise ValidationError(
                    _('The Company in the Procurement Rule and in '
                      'Stock Location must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.move', [('rule_id', '=', self.id)]),
            ('stock.warehouse', [('mto_pull_id', '=', self.id)]),
        ]
        return res
