# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class PartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_stock_customer = fields.Many2one(
        'stock.location', string="Customer Location",
        compute='_compute_property_fields',
        readonly=False,
        help="This stock location will be used, instead of "
             "the default one, as the destination location for "
             "goods you send to this partner")
    property_stock_supplier = fields.Many2one(
        'stock.location', string="Vendor Location",
        compute='_compute_property_fields',
        readonly=False,
        help="This stock location will be used, instead of "
             "the default one, as the source location for goods "
             "you receive from the current partner")

    @api.multi
    def get_property_fields(self, object, properties):
        super(PartnerProperty, self).get_property_fields(
            object, properties)
        for rec in self:
            rec.property_stock_customer = rec.get_property_value(
                'property_stock_customer', object, properties)
            rec.property_stock_supplier = rec.get_property_value(
                'property_stock_supplier', object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append('property_stock_customer')
        res.append('property_stock_supplier')
        return res
