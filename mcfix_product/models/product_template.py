from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _check_company_auto = True

    product_variant_ids = fields.One2many(check_company=True)
    variant_seller_ids = fields.One2many(check_company=True)
    seller_ids = fields.One2many(check_company=True)
    pricelist_item_ids = fields.One2many(
        "product.pricelist.item", inverse_name="product_tmpl_id", check_company=True
    )

    @api.onchange("company_id")
    def _onchange_company_id(self):
        """To be used by other modules (mcfix_account)"""

    @api.depends("company_id")
    def name_get(self):
        names = super(ProductTemplate, self).name_get()
        res = self.add_company_suffix(names)
        return res

    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if values.get("company_id", False):
            company = self.env["res.company"].browse(values["company_id"])
            for variant in self.product_variant_ids:
                if not variant.check_company(company):
                    variant.write({"company_id": values["company_id"]})
        return res

    @api.constrains("company_id")
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()
