from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_income_categ_id = fields.Many2one(readonly=True)
    property_account_expense_categ_id = fields.Many2one(readonly=True)


class ProductCategoryProperty(models.TransientModel):
    _inherit = 'product.category.property'

    property_account_income_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Income Account", oldname="property_account_income_categ",
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This account will be used for invoices to value sales.")
    property_account_expense_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Expense Account",
        oldname="property_account_expense_categ",
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This account will be used for invoices to value expenses.")

    @api.one
    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(
            object, properties)
        self.property_account_income_categ_id = self.get_property_value(
            'property_account_income_categ_id', object, properties)
        self.property_account_expense_categ_id = self.get_property_value(
            'property_account_expense_categ_id', object, properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ProductCategoryProperty, self).set_properties(object, properties)
        self.set_property(
            object,
            'property_account_income_categ_id',
            self.property_account_income_categ_id.id, properties)
        self.set_property(
            object, 'property_account_expense_categ_id',
            self.property_account_expense_categ_id.id, properties)
