# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(readonly=True)
    property_account_receivable_id = fields.Many2one(readonly=True)
    property_account_position_id = fields.Many2one(readonly=True)
    property_payment_term_id = fields.Many2one(readonly=True)
    property_supplier_payment_term_id = fields.Many2one(readonly=True)


class PartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_account_payable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), "
               "('deprecated', '=', False)]",
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This account will be used instead of the default "
             "one as the payable account for the current partner",
        required=True
    )
    property_account_receivable_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), "
               "('deprecated', '=', False)]",
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This account will be used instead of "
             "the default one as the receivable account "
             "for the current partner",
        required=True
    )
    property_account_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="The fiscal position will determine taxes "
             "and accounts used for the partner."
    )
    property_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Customer Payment Terms',
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This payment term will be used instead of the "
             "default one for sale orders and customer invoices"
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Vendor Payment Terms',
        compute='_compute_property_fields',
        readonly=False, store=False,
        help="This payment term will be used instead of the "
             "default one for purchase orders and vendor bills")

    @api.one
    def get_property_fields(self, object, properties):
        super(PartnerProperty, self).get_property_fields(object, properties)
        self.property_account_payable_id =\
            self.get_property_value('property_account_payable_id', object,
                                    properties)
        self.property_account_receivable_id =\
            self.get_property_value('property_account_receivable_id', object,
                                    properties)
        self.property_account_position_id =\
            self.get_property_value('property_account_position_id', object,
                                    properties)
        self.property_payment_term_id =\
            self.get_property_value('property_payment_term_id', object,
                                    properties)
        self.property_supplier_payment_term_id =\
            self.get_property_value('property_supplier_payment_term_id',
                                    object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append('property_account_payable_id')
        res.append('property_account_receivable_id')
        res.append('property_account_position_id')
        res.append('property_payment_term_id')
        res.append('property_supplier_payment_term_id')
        return res
