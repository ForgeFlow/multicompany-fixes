# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import MissingError


class ModelProperty(models.AbstractModel):
    _name = "model.property"
    _description = "model property"

    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", required=True, readonly=True
    )

    def _compute_property_fields(self):
        """This method must be redefined by modules that
        introduce property fields in the relevant models.
        If it is not defined by the models, will raise an error message."""
        raise MissingError(_("It must be redefined"))

    def get_property_fields(self, obj, properties):
        """This method must be redefined by modules that
        introduce property fields in the relevant models.
        It intends to be used to compute the value of property fields.
        The models that implement this method will define the the logic
        to obtain the value of the property field for a certain object.
        If it is not defined by the models, will raise an error message.
        @param obj: actual object for which we intend to get the property
        values.
        @param properties: ir.property recordset, including in
        the context the company for which we intend to obtain the value
        for the given object.

        @returns: Does not expect to return anything
        """
        raise MissingError(_("It must be redefined"))

    def set_property(self, obj, fieldname, value, properties):
        """This method will set the intended value
        of a property field to the ir.property table, in the right company.
        @param obj: actual object for which we intend to set the property
        value.
        @param fieldname: property field for the given object that we intend
        to save.
        @param value: value of the property to save.
        @param properties: ir.property recordset, including in
        the context the company for which we intend to save the value
        for the given object.
        """
        properties.with_company(self.company_id).sudo()._set_multi(
            fieldname, obj._name, {obj.id: value}
        )

    def get_property_value(self, field, obj, prop_obj):
        """This method will assist in obtaining the value of a property
        field from the ir.property table, in the right company.
        @param obj: actual object for which we intend to set the property
        value.
        @param field: property field for the given object that we intend
        to save.
        @param prop_obj: ir.property recordset, including in the context
        the company for which we intend to save the value for
        the given object.
        """
        value = prop_obj._get(field, obj._name, (obj._name + ",%s") % obj.id)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        value = prop_obj._get(field, obj._name)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        return False

    def get_property_fields_list(self):
        """This should be implemented by the models that implement this
        abstract method, providing the list of property fields that the model
        includes. This will help to set/get the property values.
        """
        return []
