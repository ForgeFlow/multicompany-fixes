from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    taxes_id = fields.Many2many(check_company=True)
    supplier_taxes_id = fields.Many2many(check_company=True)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(ProductTemplate, self)._onchange_company_id()
        if not self.taxes_id.check_company(self.company_id):
            self.taxes_id = self.taxes_id.filtered(
                lambda t: t.company_id == self.company_id)
        if not self.supplier_taxes_id.check_company(self.company_id):
            self.supplier_taxes_id = self.supplier_taxes_id.filtered(
                lambda t: t.company_id == self.company_id)
