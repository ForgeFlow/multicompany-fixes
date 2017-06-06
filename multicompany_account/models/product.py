from odoo import models, fields, api


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductTemplate, self).get_properties()

        self.property_account_income_id = self.get_property(self.property, 'property_account_income_id', False)
        self.property_account_expense_id = self.get_property(self.property, 'property_account_expense_id', False)

    @api.one
    def get_taxes(self):
        properties = self.env['product.template.property'].search([('product_id', '=', self.id)])
        self.taxes_id = self.env['account.tax'].search(
            [('id', 'in', [tax.id for property in properties for tax in property.taxes_id])]
        )
        self.supplier_taxes_id = self.env['account.tax'].search(
            [('id', 'in', [tax.id for property in properties for tax in property.supplier_taxes_id])]
        )

    taxes_id = fields.Many2many(
        default=get_taxes,
        compute='get_taxes',
        relation=False,
        column1=False,
        column2=False,
        readonly=True,
        store=False,
        domain=[('type_tax_use', '=', 'sale')])
    supplier_taxes_id = fields.Many2many(
        default=get_taxes,
        compute='get_taxes',
        relation=False,
        column1=False,
        column2=False,
        readonly=True,
        store=False,
        domain=[('type_tax_use', '=', 'purchase')])
    property_account_income_id = fields.Many2one(
        default=get_properties,
        compute='get_properties',
        company_dependent=False,
        store=False,
        comodel_name='account.account',
        string="Income Account",
        domain=[('deprecated', '=', False)],
        readonly=True,
        help="This account will be used for invoices instead of the default one to value sales for the current product.")
    property_account_expense_id = fields.Many2one(
        default=get_properties,
        compute='get_properties',
        company_dependent=False,
        store=False,
        comodel_name='account.account',
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        readonly=True,
        help="This account will be used for invoices instead of the default one to value expenses for the current product.")


class ProductProperty(models.Model):
    _inherit = 'product.template.property'
    taxes_id = fields.Many2many(
        comodel_name='account.tax',
        relation='product_prop_taxes_rel',
        column1='prop_id',
        column2='tax_id',
        string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')])
    supplier_taxes_id = fields.Many2many(
        comodel_name='account.tax',
        relation='product_prop_supplier_taxes_rel',
        column1='prop_id',
        column2='tax_id',
        string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase')])
    property_account_income_id = fields.Many2one(
        comodel_name='account.account',
        string="Income Account",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices instead of the default one to value sales for the current product.")
    property_account_expense_id = fields.Many2one(
        comodel_name='account.account',
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices instead of the default one to value expenses for the current product.")

    _sql_constraints = [('company_partner_unique',
                         'UNIQUE(company_id, product_id)',
                         "The company must be unique"),
                        ]
