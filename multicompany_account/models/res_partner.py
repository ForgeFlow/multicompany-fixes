from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(readonly=True)
    property_account_receivable_id = fields.Many2one(readonly=True)
    property_account_position_id = fields.Many2one(readonly=True)
    property_payment_term_id = fields.Many2one(readonly=True)
    property_supplier_payment_term_id = fields.Many2one(readonly=True)


class ResPartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        compute='get_properties',
        readonly=False, store=False,
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True
    )
    property_account_receivable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        compute='get_properties',
        readonly=False, store=False,
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True
    )
    property_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='get_properties',
        readonly=False, store=False,
        help="The fiscal position will determine taxes and accounts used for the partner."
    )
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Customer Payment Terms',
        compute='get_properties',
        readonly=False, store=False,
        help="This payment term will be used instead of the default one for sale orders and customer invoices"
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Vendor Payment Terms',
        compute='get_properties',
        readonly=False, store=False,
        help="This payment term will be used instead of the default one for purchase orders and vendor bills")

    @api.one
    def get_property_fields(self, object, properties):
        super(ResPartnerProperty, self).get_property_fields(object, properties)
        self.property_account_payable_id = self.get_property_value('property_account_payable_id', object, properties)
        self.property_account_receivable_id = self.get_property_value('property_account_receivable_id', object,
                                                                      properties)
        self.property_account_position_id = self.get_property_value('property_account_position_id', object, properties)
        self.property_payment_term_id = self.get_property_value('property_payment_term_id', object, properties)
        self.property_supplier_payment_term_id = self.get_property_value('property_supplier_payment_term_id', object,
                                                                         properties)

    @api.model
    def set_properties(self, object, properties=False):
        super(ResPartnerProperty, self).set_properties(object, properties)
        self.set_property(object, 'property_account_payable_id', self.property_account_payable_id.id, properties)
        self.set_property(object, 'property_account_receivable_id', self.property_account_receivable_id.id, properties)
        self.set_property(object, 'property_account_position_id', self.property_account_position_id.id, properties)
        self.set_property(object, 'property_payment_term_id', self.property_payment_term_id.id, properties)
        self.set_property(object, 'property_supplier_payment_term_id', self.property_supplier_payment_term_id.id,
                          properties)
