# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    property_delivery_carrier_id = fields.Many2one(readonly=True)


class PartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_delivery_carrier_id = fields.Many2one(
        'delivery.carrier',
        string="Delivery Method",
        compute='_compute_property_fields',
        readonly=False,
        store=False,
        help="This delivery method will be used when invoicing from picking.")

    @api.multi
    def get_property_fields(self, object, properties):
        super(PartnerProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.property_delivery_carrier_id = self.get_property_value(
                'property_delivery_carrier_id', object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append('property_delivery_carrier_id')
        return res
