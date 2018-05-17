# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_sale_tax_id = fields.Many2one(
        'account.tax',
        string="Default Sale Tax",
        compute='_compute_tax',
        inverse='_inverse_tax',
        domain="[('type_tax_use', 'in', ('sale', 'all')), "
               "('company_id', '=', active_id)]",
        store=False,
    )
    default_purchase_tax_id = fields.Many2one(
        'account.tax',
        string="Default Purchase Tax",
        compute='_compute_tax',
        inverse='_inverse_tax',
        domain="[('type_tax_use', 'in', ('purchase', 'all')), "
               "('company_id', '=', active_id)]",
        store=False,
    )
    transfer_account_id = fields.Many2one(
        domain=lambda self: (
            "["
            "('reconcile', '=', True),"
            "('user_type_id.id', '='," +
            str(self.env.ref(
                'account.data_account_type_current_assets').id) +
            "),"
            "('company_id', '=', active_id),"
            "('deprecated', '=', False)]"
        ),
    )
    expects_chart_of_accounts = fields.Boolean(
        string='Expects a Chart of Accounts', default=True)
    property_stock_account_input_categ_id = fields.Many2one(
        domain="[('company_id', '=', active_id)]",
    )
    property_stock_account_output_categ_id = fields.Many2one(
        domain="[('company_id', '=', active_id)]",
    )
    property_stock_valuation_account_id = fields.Many2one(
        domain="[('company_id', '=', active_id)]",
    )
    partner_account_payable_id = fields.Many2one(
        'account.account',
        domain="[('internal_type', '=', 'payable'),"
               "('deprecated', '=', False),"
               "('company_id', '=', active_id)]",
        compute='_compute_partner_account_payable',
        inverse='_inverse_partner_account_payable',
        string="Default Account Payable in Partner",
    )
    partner_account_receivable_id = fields.Many2one(
        'account.account',
        domain="[('internal_type', '=', 'receivable'),"
               "('deprecated', '=', False),"
               "('company_id', '=', active_id)]",
        compute='_compute_partner_account_receivable',
        inverse='_inverse_partner_account_receivable',
        string="Default Account Receivable in Partner",
    )
    categ_account_expense_id = fields.Many2one(
        'account.account',
        domain="[('internal_type', '=', 'expense'),"
               "('deprecated', '=', False),"
               "('company_id', '=', active_id)]",
        compute='_compute_categ_account_expense',
        inverse='_inverse_categ_account_expense',
        string="Default Expense Account in Product Category",
    )
    categ_account_income_id = fields.Many2one(
        'account.account',
        domain="[('internal_type', '=', 'income'),"
               "('deprecated', '=', False),"
               "('company_id', '=', active_id)]",
        compute='_compute_categ_account_income',
        inverse='_inverse_categ_account_income',
        string="Default Income Account in Product Category",
    )

    def get_property_value(self, model, field):
        value = self.env['ir.property'].with_context(
            force_company=self.id).sudo().get(field, model)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        return False

    def set_property_value(self, model, field_name, value):
        field = self.env['ir.model.fields'].sudo().search([
            ('name', '=', field_name),
            ('model', '=', model)
        ], limit=1)
        if isinstance(value, models.BaseModel):
            if value:
                val = value.id
            else:
                val = False
        else:
            val = value
        prop = self.env['ir.property'].sudo().search([
            ('name', '=', field_name),
            ('fields_id', '=', field.id),
            ('company_id', '=', self.id),
            ('res_id', '=', False)
        ])
        if not prop:
            prop = self.env['ir.property'].sudo().create({
                'name': field_name,
                'fields_id': field.id,
                'company_id': self.id,
                'res_id': False,
            })
        prop.write({'value': val})

    @api.model
    def _compute_partner_account_payable(self):
        for rec in self:
            rec.partner_account_payable_id = rec.get_property_value(
                'res.partner', 'property_account_payable_id'
            )

    @api.model
    def _inverse_partner_account_payable(self):
        for rec in self:
            rec.set_property_value(
                'res.partner', 'property_account_payable_id',
                rec.partner_account_payable_id
            )

    @api.model
    def _compute_partner_account_receivable(self):
        for rec in self:
            rec.partner_account_receivable_id = rec.get_property_value(
                'res.partner', 'property_account_receivable_id'
            )

    @api.model
    def _inverse_partner_account_receivable(self):
        for rec in self:
            rec.set_property_value(
                'res.partner', 'property_account_receivable_id',
                rec.partner_account_receivable_id
            )

    @api.model
    def _compute_categ_account_expense(self):
        for rec in self:
            rec.categ_account_expense_id = rec.get_property_value(
                'product.category', 'property_account_expense_categ_id'
            )

    @api.model
    def _inverse_categ_account_expense(self):
        for rec in self:
            rec.set_property_value(
                'product.category', 'property_account_expense_categ_id',
                rec.categ_account_expense_id
            )

    @api.model
    def _compute_categ_account_income(self):
        for rec in self:
            rec.categ_account_income_id = rec.get_property_value(
                'product.category', 'property_account_income_categ_id'
            )

    @api.model
    def _inverse_categ_account_income(self):
        for rec in self:
            rec.set_property_value(
                'product.category', 'property_account_income_categ_id',
                rec.categ_account_income_id
            )

    @api.model
    def _compute_tax(self):
        IrDefault = self.env['ir.default'].sudo()
        tax_obj = self.env['account.tax']
        for record in self:
            record.default_sale_tax_id = tax_obj.browse(IrDefault.get(
                'product.template', "taxes_id", company_id=record.id))
            record.default_purchase_tax_id = tax_obj.browse(IrDefault.get(
                'product.template', "supplier_taxes_id", company_id=record.id))

    @api.multi
    def _inverse_tax(self):
        IrDefault = self.env['ir.default'].sudo()
        for record in self:
            IrDefault.set(
                'product.template', "taxes_id",
                record.default_sale_tax_id.ids, company_id=record.id)
            IrDefault.set(
                'product.template', "supplier_taxes_id",
                record.default_purchase_tax_id.ids, company_id=record.id)
