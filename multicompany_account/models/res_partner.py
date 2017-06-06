from odoo import fields, models, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ResPartner,self).get_properties()

        self.property_account_payable_id = self.get_property(
            self.property, 'property_account_payable_id', self.current_company_id.default_account_payable_id)
        self.property_account_receivable_id = self.get_property(
            self.property, 'property_account_receivable_id', self.current_company_id.default_account_receivable_id)
        self.property_account_position_id = self.get_property(
            self.property, 'property_account_position_id', self.current_company_id.default_account_position_id)
        self.property_supplier_payment_term_id = self.get_property(
            self.property, 'property_supplier_payment_term_id', self.current_company_id.default_supplier_payment_term_id)
        self.property_payment_term_id = self.get_property(
            self.property, 'property_payment_term_id', self.current_company_id.default_payment_term_id)

    property_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=False,
        string="Account Payable",  # oldname="property_account_payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=False,
        store=False,
        default=get_properties,
        compute='get_properties')

    property_account_receivable_id = fields.Many2one(
        comodel_name='account.account', company_dependent=False,
        string="Account Payable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=False,
        store=False,
        default=get_properties,
        compute='get_properties')

    property_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position', company_dependent=False,
        string="Fiscal Position",
        help="The fiscal position will determine taxes and accounts used for the partner.",
        oldname="property_account_position",
        store=False,
        default=get_properties,
        compute='get_properties'
    )
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', company_dependent=False,
        string='Customer Payment Terms',
        help="This payment term will be used instead of the default one for sale orders and customer invoices",
        oldname="property_payment_term",
        store=False,
        default=get_properties,
        compute='get_properties'
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', company_dependent=False,
        string='Vendor Payment Terms',
        help="This payment term will be used instead of the default one for purchase orders and vendor bills",
        oldname="property_supplier_payment_term",
        store=False,
        default=get_properties,
        compute='get_properties')


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
        required=True)
    property_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        help="The fiscal position will determine taxes and accounts used for the partner.")
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Customer Payment Terms',
        help="This payment term will be used instead of the default one for sale orders and customer invoices")
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Vendor Payment Terms',
        help="This payment term will be used instead of the default one for purchase orders and vendor bills")
