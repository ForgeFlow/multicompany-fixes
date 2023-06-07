# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    property_ids = fields.One2many(
        comodel_name="res.partner.property",
        compute="_compute_properties",
        inverse="_inverse_properties",
        string="Properties",
    )

    def _inverse_properties(self):
        """Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable."""
        return

    def _compute_properties(self):
        for record in self:
            property_obj = self.env["res.partner.property"]
            values = []
            for company in self.env.companies:
                val = property_obj.create(
                    {"partner_id": record.id, "company_id": company.id}
                )
                values.append(val.id)
            record.property_ids = values

    def _children_sync(self, values):
        """
        Convert property values to the actual fields set on the partner, so that the
        children contacts inherit the values correctly just as Odoo standard does.
        """
        if "property_ids" in values:
            property_obj = self.env["res.partner.property"]
            comm_fields = set(self._commercial_fields())
            all_property_vals = values.get("property_ids")
            for p_vals in all_property_vals:
                is_list = isinstance(p_vals, list)
                if not is_list or (is_list and len(p_vals) != 3):
                    continue
                p_id = p_vals[1]
                p_val = p_vals[2]
                prop = property_obj.browse(p_id)
                if not p_val or not prop.exists():
                    continue
                company_id = prop.company_id.id
                fields_to_sync = set(p_val.keys()) & comm_fields
                if fields_to_sync:
                    vals = {f: p_val.get(f) for f in fields_to_sync}
                    self.with_context(force_company=company_id)._children_sync(vals)
            values.pop("property_ids")
        return super()._children_sync(values)


class PartnerProperty(models.TransientModel):
    _name = "res.partner.property"
    _description = "Properties of Partner"
    _inherit = "model.property"
    _description = "Partner Properties"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")

    def _compute_property_fields(self):
        for rec in self:
            rec.get_property_fields(
                rec.partner_id,
                rec.env["ir.property"].with_company(rec.company_id),
            )

    def get_property_fields(self, obj, properties):
        """We have no property fields in this module, but we still
        have to implement the method to avoid error."""
        return

    def write(self, vals):
        prop_obj = self.env["ir.property"].with_company(self.company_id)
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    self.set_property(rec.partner_id, field, vals[field], prop_obj)
        return super(PartnerProperty, self).write(vals)
