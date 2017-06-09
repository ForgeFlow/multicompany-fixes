from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.one
    def _default_stock_properties(self):
        ir_property_obj = self.env['ir.property']
        self.default_stock_journal = ir_property_obj.with_context(
            force_company=self.id).get(
            'property_stock_journal', 'product.category')
        self.default_stock_account_input_categ_id = \
            ir_property_obj.with_context(force_company=self.id).get(
            'property_stock_account_input_categ_id', 'product.category')
        self.default_stock_account_output_categ_id = \
            ir_property_obj.with_context(force_company=self.id).get(
            'property_stock_account_output_categ_id', 'product.category')
        self.default_stock_valuation_account_id = \
            ir_property_obj.with_context(force_company=self.id).get(
            'property_stock_valuation_account_id', 'product.category')

    default_stock_journal = fields.Many2one(
        comodel_name='account.journal',
        required=False,
        string="Default stock Journal",
        default=_default_stock_properties
    )
    default_stock_account_input_categ_id = fields.Many2one(
        comodel_name='account.account',
        required=False,
        string="Default stock input account for category",
        default=_default_stock_properties
    )
    default_stock_account_output_categ_id = fields.Many2one(
        comodel_name='account.account',
        required=False,
        string="Default stock output account for category",
        default=_default_stock_properties
    )
    default_stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        required=False,
        string="Default stock valuation account",
        default=_default_stock_properties
    )
