from odoo import fields, models, api


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        self.current_company_id = self.env['res.company'].browse(
            self._context.get('force_company') or self.env.user.company_id.id).ensure_one()
        property_id = self.env['product.category.property'].search(
            [('categ_id', '=', self.id),
             ('company_id', '=', self.current_company_id.id)])
        self.property = property_id.ensure_one() if property_id else False


    property = fields.Many2one(
        comodel_name='product.category.property',
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

    property_ids = fields.One2many(
        comodel_name='product.category.property',
        inverse_name='categ_id',
        string='Properties'

    )

    class ProductCategoryProperty(models.Model):
        _name = 'product.category.property'
        _description = "Properties of Product categories"

        company_id = fields.Many2one(
            comodel_name='res.company',
            string='Company',
            required=True
        )

        categ_id = fields.Many2one(
            comodel_name='product.category',
            string='Product category'
        )

        _sql_constraints = [('company_partner_unique',
                             'UNIQUE(company_id, categ_id)',
                             "The company must be unique"),
                            ]
