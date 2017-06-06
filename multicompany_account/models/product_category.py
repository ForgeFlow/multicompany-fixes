from odoo import fields, models, api


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductCategory, self).get_properties()
        self.property_account_income_categ_id = self.get_property(
            self.property, 'property_account_income_categ_id', self.current_company_id.default_account_income_id)
        self.property_account_expense_categ_id = self.get_property(
            self.property, 'property_account_expense_categ_id', self.current_company_id.default_account_expense_id)

    property_account_income_categ_id = fields.Many2one(
        comodel_name='account.account', company_dependent=False,
        string="Income Account", oldname="property_account_income_categ",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices to value sales.",
        store=False,
        default=get_properties,
        compute='get_properties')
    property_account_expense_categ_id = fields.Many2one(
        comodel_name='account.account', company_dependent=False,
        string="Expense Account",
        oldname="property_account_expense_categ",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices to value expenses.",
        store=False,
        default=get_properties,
        compute='get_properties')


class ProductCategoryProperty(models.Model):
    _inherit = 'product.category.property'

    property_account_income_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Income Account", oldname="property_account_income_categ",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices to value sales.")
    property_account_expense_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Expense Account",
        oldname="property_account_expense_categ",
        domain=[('deprecated', '=', False)],
        help="This account will be used for invoices to value expenses.")
