# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

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

    @api.multi
    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(
            object, properties)
        for rec in self:
            rec.property_account_income_categ_id = rec.get_property_value(
                'property_account_income_categ_id', object, properties)
            rec.property_account_expense_categ_id = rec.get_property_value(
                'property_account_expense_categ_id', object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductCategoryProperty, self).get_property_fields_list()
        res.append('property_account_income_categ_id')
        res.append('property_account_expense_categ_id')
        return res
