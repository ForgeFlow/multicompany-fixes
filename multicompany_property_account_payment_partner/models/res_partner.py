# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    supplier_payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Supplier Payment Mode",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        domain="[('payment_type', '=', 'outbound')]",
        help="Select the default payment mode for this supplier.",
    )
    customer_payment_mode_id = fields.Many2one(
        "account.payment.mode",
        string="Customer Payment Mode",
        compute="_compute_property_fields",
        readonly=False,
        store=False,
        domain="[('payment_type', '=', 'inbound')]",
        help="Select the default payment mode for this customer.",
    )

    def get_property_fields(self, object, properties):
        super(PartnerProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.supplier_payment_mode_id = rec.get_property_value(
                "supplier_payment_mode_id", object, properties
            )
            rec.customer_payment_mode_id = rec.get_property_value(
                "customer_payment_mode_id", object, properties
            )

    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append("supplier_payment_mode_id")
        res.append("customer_payment_mode_id")
        return res
