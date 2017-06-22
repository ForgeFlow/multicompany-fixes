import odoo.addons.decimal_precision as dp

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_ids = fields.One2many(
        comodel_name='product.template.property',
        compute='_get_properties',
        inverse='_set_properties',
        string='Properties'
    )

    @api.multi
    def _set_properties(self):
        ''' Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable, '''
        return

    @api.multi
    def _get_properties(self):
        for record in self:
            property_obj = self.env['product.template.property']
            companies = self.env['res.company'].search([])
            for company in companies:
                val = property_obj.create({
                    'company_id': company.id,
                    'product_template_id': record.id
                })
                record.property_ids += val


class ProductProperty(models.TransientModel):
    _name = 'product.template.property'
    _inherit = 'multicompany.property.abstract'

    _description = "Properties of Product categories"

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string="Product"
    )

    standard_price = fields.Float(
        'Cost',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for "
             "standard stock valuation in accounting "
             "and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.",
        compute='_compute_property_fields',
        readonly=False)

    @api.one
    def _compute_property_fields(self):
        self.get_property_fields(self.product_template_id,
                                 self.env['ir.property'].with_context(
                                     force_company=self.company_id.id))

    @api.one
    def get_property_fields(self, object, properties):
        if len(self.product_template_id.product_variant_ids) == 1:
            variant = object.product_variant_ids[0]
            self.standard_price = self.get_property_value('standard_price',
                                                          variant, properties)
        else:
            self.standard_price = 0.0

    @api.multi
    def write(self, vals):
        prop_obj = self.env['ir.property'].with_context(
            force_company=self.company_id.id)
        if 'standard_price' in vals:
            for rec in self:
                if len(rec.product_template_id.product_variant_ids) == 1:
                    for pv in rec.product_template_id.product_variant_ids:
                        self.set_property(pv, 'standard_price',
                                          vals['standard_price'], prop_obj)

        return super(ProductProperty, self).write(vals)
