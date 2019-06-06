# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class ProductProperty(models.TransientModel):
    _inherit = 'product.property'

    property_account_income_id = fields.Many2one(
        comodel_name='account.account',
        string="Income Account",
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False,
        store=False,
        help="This account will be used for invoices instead "
             "of the default one to value sales for the current product."
    )
    property_account_expense_id = fields.Many2one(
        comodel_name='account.account',
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False,
        store=False,
        help="This account will be used for invoices instead "
             "of the default one to value expenses for the current product.")

    @api.multi
    def get_property_fields(self, object, properties):
        super(ProductProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.property_account_income_id = \
                rec.get_property_value('property_account_income_id', object,
                                       properties)
            rec.property_account_expense_id = \
                rec.get_property_value('property_account_expense_id', object,
                                       properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductProperty, self).get_property_fields_list()
        res.append('property_account_income_id')
        res.append('property_account_expense_id')
        return res
