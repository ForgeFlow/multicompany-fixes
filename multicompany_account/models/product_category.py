from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_income_categ_id = fields.Many2one(readonly=True)
    property_account_expense_categ_id = fields.Many2one(readonly=True)


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

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_account_income_categ_id', False):
            self.set_property(object, 'property_account_income_categ_id',
                              vals.get('property_account_income_categ_id', False), properties)
        if vals.get('property_account_expense_categ_id', False):
            self.set_property(object, 'property_account_expense_categ_id',
                              vals.get('property_account_expense_categ_id', False), properties)
        return super(ProductCategoryProperty, self).set_properties(object, vals, properties)
