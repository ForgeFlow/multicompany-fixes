from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(readonly=True)
    property_account_receivable_id = fields.Many2one(readonly=True)
    property_account_position_id = fields.Many2one(readonly=True)
    property_payment_term_id = fields.Many2one(readonly=True)
    property_supplier_payment_term_id = fields.Many2one(readonly=True)


class ResPartnerProperties(models.Model):
    _inherit = 'res.partner.property'

    property_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True
    )
    property_account_receivable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True
    )
    property_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        help="The fiscal position will determine taxes and accounts used for the partner."
    )
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Customer Payment Terms',
        help="This payment term will be used instead of the default one for sale orders and customer invoices"
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Vendor Payment Terms',
        help="This payment term will be used instead of the default one for purchase orders and vendor bills")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_account_payable_id', False):
            self.set_property(object, 'property_account_payable_id', vals.get('property_account_payable_id', False),
                              properties)
        if vals.get('property_account_receivable_id', False):
            self.set_property(object, 'property_account_receivable_id', vals.get('property_account_receivable_id', False),
                              properties)
        if vals.get('property_account_position_id', False):
            self.set_property(object, 'property_account_position_id', vals.get('property_account_position_id', False),
                              properties)
        if vals.get('property_payment_term_id', False):
            self.set_property(object, 'property_payment_term_id', vals.get('property_payment_term_id', False),
                              properties)
        if vals.get('property_supplier_payment_term_id', False):
            self.set_property(object, 'property_supplier_payment_term_id', vals.get('property_supplier_payment_term_id', False),
                              properties)
        return super(ResPartnerProperties, self).set_properties(object, vals, properties)
