import odoo.addons.decimal_precision as dp

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        self.current_company_id = self.env['res.company'].browse(
            self._context.get('force_company') or self.env.user.company_id.id).ensure_one()
        property_id = self.env['product.template.property'].search(
            [('product_id', '=', self.id),
             ('company_id', '=', self.current_company_id.id)])
        self.property = property_id.ensure_one() if property_id else False

        self.standard_price = self.get_property(self.property, 'standard_price', 0)

    property = fields.Many2one(
        comodel_name='product.template.property',
        default=get_properties,
        compute='get_properties',
        store=False
    )

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=get_properties,
        compute='get_properties',
        store=False
    )

    standard_price = fields.Float(
        string='Cost',
        company_dependent=False,
        readonly=True,
        store=False,
        default=get_properties,
        compute='get_properties',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.")

    property_ids = fields.One2many(
        comodel_name='product.template.property',
        inverse_name='product_id',
        string='Properties'
    )


class ProductProperty(models.Model):
    _name = 'product.template.property'
    _description = "Properties of Product categories"

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product'
    )
    standard_price = fields.Float(
        'Cost',
        digits=dp.get_precision('Product Price'),
        groups="base.group_user",
        help="Cost of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
             "Expressed in the default unit of measure of the product.")

    _sql_constraints = [('company_partner_unique',
                         'UNIQUE(company_id, product_id)',
                         "The company must be unique"),
                        ]
