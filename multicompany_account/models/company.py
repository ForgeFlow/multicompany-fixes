from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_sale_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string="Default Sale Tax",
        help="This sale tax will be assigned by default on new products.",
        oldname="default_sale_tax")
    default_purchase_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string="Default Purchase Tax",
        help="This purchase tax will be assigned by default on new products.",
        oldname="default_purchase_tax")

    default_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string="Default payable account",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]"
    )
    default_account_receivable_id = fields.Many2one(
        comodel_name='account.account',
        string="Default receivable account",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]"
    )
    default_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        help="The fiscal position will determine taxes and accounts used for the partner.")
    default_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Customer Payment Terms',
        help="This payment term will be used instead of the default one for sale orders and customer invoices")
    default_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Vendor Payment Terms',
        help="This payment term will be used instead of the default one for purchase orders and vendor bills")

    default_account_income_id = fields.Many2one(
        comodel_name='account.account',
        string="Default income account",
        domain="('deprecated', '=', False)]"
    )

    default_account_expense_id = fields.Many2one(
        comodel_name='account.account',
        string="Default expense account",
        domain="('deprecated', '=', False)]"
    )
