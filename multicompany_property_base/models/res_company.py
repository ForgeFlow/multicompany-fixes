# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    property_ids = fields.One2many(
        comodel_name='res.company.property',
        compute='_compute_properties',
        inverse='_inverse_properties',
        string='Properties'
    )

    @api.multi
    def _inverse_properties(self):
        """ Hack here: We do not really store any value here.
        But this allows us to have the fields of the transient
        model editable. """
        return

    @api.multi
    def _compute_properties(self):
        for record in self:
            property_obj = self.env['res.company.property']
            val = property_obj.create({
                'company_id': record.id,
            })
            record.property_ids = [val.id]


class CompanyProperty(models.TransientModel):
    _name = 'res.company.property'
    _inherit = 'model.property'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company'
    )

    @api.one
    def _compute_property_fields(self):
        self.get_property_fields(self.company_id,
                                 self.env['ir.property'].with_context(
                                     force_company=self.company_id.id))

    @api.one
    def get_property_fields(self, object, properties):
        """ This method must be redefined by modules that
        introduce property fields in the res.company model """
        return

    @api.model
    def set_properties(self, object, properties=False):
        """ This method must be redefined by modules that
        introduce property fields in the res.company model """
        return

    @api.multi
    def write(self, vals):
        prop_obj = self.env['ir.property'].with_context(
            force_company=self.company_id.id)
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    self.set_property(rec.company_id, field,
                                      vals[field], prop_obj)
        return super(CompanyProperty, self).write(vals)
