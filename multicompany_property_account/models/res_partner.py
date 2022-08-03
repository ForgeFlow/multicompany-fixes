# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    property_account_payable_id = fields.Many2one(
        comodel_name="account.account",
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="This account will be used instead of the default "
        "one as the payable account for the current partner",
        required=True,
    )
    property_account_receivable_id = fields.Many2one(
        comodel_name="account.account",
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="This account will be used instead of "
        "the default one as the receivable account "
        "for the current partner",
        required=True,
    )
    property_account_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="The fiscal position determines the taxes/accounts "
        "used for this contact.",
    )
    property_payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Customer Payment Terms",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="This payment term will be used instead of the "
        "default one for sale orders and customer invoices",
    )
    property_supplier_payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Vendor Payment Terms",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        help="This payment term will be used instead of the "
        "default one for purchase orders and vendor bills",
    )
    trust = fields.Selection(
        [("good", "Good Debtor"), ("normal", "Normal Debtor"), ("bad", "Bad Debtor")],
        string="Degree of trust you have in this debtor",
        compute="_compute_property_fields",
        readonly=False,
    )

    def get_property_fields(self, obj, properties):
        res = super(PartnerProperty, self).get_property_fields(obj, properties)
        for rec in self:
            rec.property_account_payable_id = rec.get_property_value(
                "property_account_payable_id", obj, properties
            )
            rec.property_account_receivable_id = rec.get_property_value(
                "property_account_receivable_id", obj, properties
            )
            rec.property_account_position_id = rec.get_property_value(
                "property_account_position_id", obj, properties
            )
            rec.property_payment_term_id = rec.get_property_value(
                "property_payment_term_id", obj, properties
            )
            rec.property_supplier_payment_term_id = rec.get_property_value(
                "property_supplier_payment_term_id", obj, properties
            )
            rec.trust = rec.get_property_value("trust", obj, properties)
        return res

    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append("property_account_payable_id")
        res.append("property_account_receivable_id")
        res.append("property_account_position_id")
        res.append("property_payment_term_id")
        res.append("property_supplier_payment_term_id")
        res.append("trust")
        return res
