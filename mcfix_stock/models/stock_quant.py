from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.constrains('company_id', 'location_id')
    def _check_company_id_location_id(self):
        for rec in self.sudo():
            if not rec.location_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Stock Location must be the same.'))

    @api.multi
    @api.constrains('company_id', 'package_id')
    def _check_company_id_package_id(self):
        for rec in self.sudo():
            if not rec.package_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Stock Quant Package must be the same.'))

    @api.multi
    @api.constrains('company_id', 'owner_id')
    def _check_company_id_owner_id(self):
        for rec in self.sudo():
            if not rec.owner_id.check_company(rec.company_id):
                raise ValidationError(
                    _('The Company in the Stock Quant and in '
                      'Res Partner must be the same.'))

    @api.multi
    @api.constrains('company_id', 'product_id')
    def _check_company_id_product_id(self):
        for rec in self.sudo():
            if not rec.product_id.check_company(rec.company_id):
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
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.current_picking_move_line_ids, self.move_line_ids,
            self.quant_ids,
        ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res = res + [
            ('stock.inventory', [('package_id', '=', self.id)]),
            ('stock.inventory.line', [('package_id', '=', self.id)]),
            ('stock.scrap', [('package_id', '=', self.id)]),
        ]
        return res
