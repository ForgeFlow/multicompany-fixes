# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    property_purchase_currency_id = fields.Many2one(readonly=True)


class PartnerProperties(models.TransientModel):
    _inherit = 'res.partner.property'

    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Supplier Currency",
        compute='_compute_property_fields',
        readonly=False,
        help="This currency will be used, instead of the "
             "default one, for purchases from the current partner")

    @api.multi
    def get_property_fields(self, object, properties):
        super(PartnerProperties, self).get_property_fields(object, properties)
        for rec in self:
            rec.property_purchase_currency_id = \
                rec.get_property_value('property_purchase_currency_id',
                                       object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(PartnerProperties, self).get_property_fields_list()
        res.append('property_purchase_currency_id')
        return res
