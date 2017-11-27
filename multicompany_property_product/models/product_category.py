# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_ids = fields.One2many(
        comodel_name='product.category.property',
        compute='_compute_properties',
        inverse='_inverse_properties',
        string='Properties'
    )

    @api.multi
    def _inverse_properties(self):
        prop_obj = self.env['ir.property'].with_context(
            force_company=self.company_id.id)
        for record in self:
            for rec_property in record.property_ids:
                rec_property.set_properties(record, prop_obj)

    @api.multi
    def _compute_properties(self):
        for record in self:
            property_obj = self.env['product.category.property']
            values = []
            companies = self.env['res.company'].search([])
            for company in companies:
                val = property_obj.create({
                    'categ_id': record.id,
                    'company_id': company.id
                })
                values.append(val.id)
            record.property_ids = values


class ProductCategoryProperty(models.TransientModel):
    _name = 'product.category.property'
    _inherit = 'model.property'
    _description = "Properties of Product categories"

    categ_id = fields.Many2one(
        comodel_name='product.category'
    )

    @api.one
    def get_properties(self):
        self.get_property_fields(self.categ_id,
                                 self.env['ir.property'].with_context(
                                     force_company=self.company_id.id))

    @api.one
    def get_property_fields(self, object, properties):
        return

    @api.model
    def set_properties(self, object, properties=False):
        return

    @api.multi
    def write(self, vals):
        prop_obj = self.env['ir.property'].with_context(
            force_company=self.company_id.id)
        p_fields = self.get_property_fields_list()
        for field in p_fields:
            if field in vals:
                for rec in self:
                    self.set_property(rec.partner_id, field,
                                      vals[field], prop_obj)
        return super(ProductCategoryProperty, self).write(vals)
