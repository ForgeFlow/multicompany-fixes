from odoo import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'


class QuantPackage(models.Model):
    _inherit = "stock.quant.package"

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
