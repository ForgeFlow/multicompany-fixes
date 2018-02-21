from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.location_id.company_id and\
                    rec.company_id != rec.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.package_id.company_id and\
                    rec.company_id != rec.package_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Stock Quant Package must be the same.'))

    @api.multi
    @api.constrains('company_id', 'owner_id')
    def _check_company_id_owner_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.owner_id.company_id and\
                    rec.company_id != rec.owner_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if rec.company_id and rec.product_id.company_id and\
                    rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Product Product must be the same.'))


class QuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(QuantPackage, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['stock.inventory.line'].search(
                    [('package_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Quant Package is assigned to '
                          'Stock Inventory Line (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['stock.inventory'].search(
                    [('package_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Quant Package is assigned to Stock Inventory '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['stock.quant'].search(
                    [('package_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Stock Quant Package is assigned to Stock Quant '
                          '(%s).' % field.name_get()[0][1]))
