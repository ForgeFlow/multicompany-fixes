from odoo import api, models, _
from odoo.exceptions import ValidationError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and self.product_id.company_id and \
                self.product_id.company_id != self.company_id:
            self.product_id = False
        if self.company_id and self.location_id.company_id and \
                self.location_id.company_id != self.company_id:
            if self.product_id.location_id:
                self.location_id = self.product_id.location_id
            else:
                self._cache.update(self._convert_to_cache(
                    {'location_id': False}, update=True))
        if self.company_id and self.partner_id.company_id and \
                self.partner_id.company_id != self.company_id:
            self.partner_id = False
        if self.company_id and self.package_id.company_id and \
                self.package_id.company_id != self.company_id:
            self.package_id = False

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and \
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and \
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.package_id.company_id and \
                    rec.company_id != rec.package_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Stock Quant Package must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and \
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory and in '
                      'Product Product must be the same.'))

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.inventory.line'].search(
                    [('inventory_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Inventory is assigned to '
                          'Stock Inventory Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.move'].search(
                    [('inventory_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Inventory is assigned to Stock Move '
                          '(%s).' % field.name_get()[0][1]))


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and \
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'partner_id')
    def _check_company_id_partner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.partner_id.company_id and \
                    rec.company_id != rec.partner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'inventory_id')
    def _check_company_id_inventory_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.inventory_id.company_id and \
                    rec.company_id != rec.inventory_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Inventory must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.package_id.company_id and \
                    rec.company_id != rec.package_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Inventory Line and in '
                      'Stock Quant Package must be the same.'))

    # @api.multi
    # @api.constrains('company_id', 'product_id')
    # def _check_company_id_product_id(self):
    #     for rec in self.sudo():
    #         if rec.company_id and rec.product_id.company_id and \
    #                 rec.company_id != rec.product_id.company_id:
    #             raise ValidationError(
    #                 _('The Company in the Stock Inventory Line and in '
    #                   'Product Product must be the same.'))
