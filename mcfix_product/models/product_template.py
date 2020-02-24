from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """To be used by other modules"""
        pass

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        names = super(ProductTemplate, self).name_get()
        res = self.add_company_suffix(names)
        return res

    @api.multi
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if values.get('company_id'):
            for variant in self.product_variant_ids:
                if variant.company_id and variant.company_id.id != \
                        values['company_id']:
                    variant.write({'company_id': values['company_id']})
        return res

    @api.constrains('company_id')
    def _check_company_id_out_model(self):
        self._check_company_id_base_model()

    def _check_company_id_fields(self):
        res = super()._check_company_id_fields()
        res += [
            self.item_ids, self.product_variant_ids,
            self.variant_seller_ids, self.seller_ids,
        ]
        return res
