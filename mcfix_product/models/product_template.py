from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self:
                if not rec.company_id:
                    continue
                field = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Product Template is assigned to '
                          'Product Supplierinfo (%s)'
                          '.' % field.name_get()[0][1]))
                field = self.env['product.product'].search(
                    [('product_tmpl_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Product Template is assigned to Product Product '
                          '(%s).' % field.name_get()[0][1]))
                field = self.env['product.pricelist.item'].search(
                    [('product_tmpl_id', '=', rec.id),
                     ('company_id', '!=', False),
                     ('company_id', '!=', rec.company_id.id)], limit=1)
                if field:
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Product Template is assigned to '
                          'Product Pricelist Item (%s)'
                          '.' % field.name_get()[0][1]))
