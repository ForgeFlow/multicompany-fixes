from odoo import api, fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"
    _check_company_auto = True

    item_ids = fields.One2many(check_company=True)

    @api.depends("company_id")
    def name_get(self):
        names = super(Pricelist, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
