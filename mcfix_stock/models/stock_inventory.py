from odoo import api, models, _
from odoo.exceptions import ValidationError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def create(self, vals):
        if vals.get('location_id') and not vals.get('company_id'):
            location = self.env['stock.location'].browse(vals['location_id'])
            if location.company_id:
                vals['company_id'] = location.company_id.id
        return super(Inventory, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if not self.product_id.check_company(self.company_id):
            self.product_id = False
        if not self.location_id.check_company(self.company_id):
            if self.product_id.location_id:
                self.location_id = self.product_id.location_id
            else:
                self._cache.update(self._convert_to_cache(
                    {'location_id': False}, update=True))
        if not self.partner_id.check_company(self.company_id):
            self.partner_id = False
        if not self.package_id.check_company(self.company_id):
            self.package_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if not rec.package_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Stock Quant Package must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.line_ids, self.move_ids, ]
        return res


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if not rec.partner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'inventory_id')
    def _check_company_id_inventory_id(self):
        for rec in self.sudo():
            if not rec.inventory_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Inventory must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if not rec.package_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Quant Package must be the same.'))
