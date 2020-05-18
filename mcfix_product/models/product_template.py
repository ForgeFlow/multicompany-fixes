from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _check_company_auto = False

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """To be used by other modules (mcfix_account)"""
        pass

    @api.depends('company_id')
    def name_get(self):
        names = super(ProductTemplate, self).name_get()
        res = self.add_company_suffix(names)
        return res

    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if values.get('company_id', False):
            company = self.env["res.company"].browse(values['company_id'])
            for variant in self.product_variant_ids:
                if not variant.check_company(company):
                    variant.write({'company_id': values['company_id']})
        return res

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.product_variant_ids,
            self.variant_seller_ids, self.seller_ids,
        ]
        return res

    def _check_company_id_search(self):
        res = super()._check_company_id_search()
        res += [
            ('product.pricelist.item', [('product_tmpl_id', '=', self.id)]),
        ]
        return res
