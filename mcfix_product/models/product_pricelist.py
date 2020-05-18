from odoo import api, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"
    _check_company_auto = True

    @api.depends('company_id')
    def name_get(self):
        names = super(Pricelist, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [self.item_ids, ]
        return res
