from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_tmpl_id = fields.Many2one(check_company=True)

    @api.depends("company_id")
    def name_get(self):
        names = super(ProductProduct, self).name_get()
        res = self.add_company_suffix(names)
        return res

    def write(self, values):
        if values.get("company_id", False):
            res = super(
                ProductProduct, self.with_context(bypass_company_validation=True)
            ).write(values)
            company = self.env["res.company"].browse(values["company_id"])
            if not self.product_tmpl_id.check_company(company):
                self.product_tmpl_id.write({"company_id": values["company_id"]})
        else:
            res = super(ProductProduct, self).write(values)
        return res
