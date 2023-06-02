from odoo import api, models


class PartnerProperty(models.TransientModel):
    _inherit = "res.partner.property"

    @api.model
    def _get_payment_term_fields_applicable_on_mapping(self):
        apt_model = self.env["account.payment.term"]
        return {
            "property_payment_term_id": apt_model.get_sale_applicable_on(),
            "property_supplier_payment_term_id": apt_model.get_purchase_applicable_on(),
        }

    def set_property(self, obj, fieldname, value, properties):
        if self.env.context.get("skip_payment_term_restriction", False):
            return super().set_property(obj, fieldname, value, properties)
        pt_fields_dict = self._get_payment_term_fields_applicable_on_mapping()
        if fieldname in pt_fields_dict.keys():
            payment_term = self.env["account.payment.term"].browse(value)
            applicable_on = pt_fields_dict.get(fieldname)
            if payment_term.exists():
                payment_term.check_not_applicable(applicable_on, record=obj)
        super().set_property(obj, fieldname, value, properties)
