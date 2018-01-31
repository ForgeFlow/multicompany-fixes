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
