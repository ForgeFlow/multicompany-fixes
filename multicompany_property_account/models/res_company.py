# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    property_stock_account_input_categ_id = fields.Many2one(readonly=True)
    property_stock_account_output_categ_id = fields.Many2one(readonly=True)
    property_stock_valuation_account_id = fields.Many2one(readonly=True)


class CompanyProperty(models.TransientModel):
    _inherit = 'res.company.property'

    property_stock_account_input_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Input Account for Stock Valuation",
        compute='_compute_property_fields',
        readonly=False, store=False,
    )
    property_stock_account_output_categ_id = fields.Many2one(
        comodel_name='account.account',
        string="Output Account for Stock Valuation",
        compute='_compute_property_fields',
        readonly=False, store=False,
    )
    property_stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Template for Stock Valuation",
        compute='_compute_property_fields',
        readonly=False, store=False,
    )

    @api.one
    def get_property_fields(self, object, properties):
        super(CompanyProperty, self).get_property_fields(object, properties)
        self.property_stock_account_input_categ_id = \
            self.get_property_value('property_stock_account_input_categ_id',
                                    object, properties)
        self.property_stock_account_output_categ_id = \
            self.get_property_value('property_stock_account_output_categ_id',
                                    object, properties)
        self.property_stock_valuation_account_id = \
            self.get_property_value('property_stock_valuation_account_id',
                                    object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(CompanyProperty, self).get_property_fields_list()
        res.append('property_stock_account_input_categ_id')
        res.append('property_stock_account_output_categ_id')
        res.append('property_stock_valuation_account_id')
        return res

    @api.model
    def set_properties(self, object, properties=False):
        super(CompanyProperty, self).set_properties(object, properties)
        self.set_property(object, 'property_stock_account_input_categ_id',
                          self.property_stock_account_input_categ_id.id,
                          properties)
        self.set_property(object, 'property_stock_account_output_categ_id',
                          self.property_stock_account_output_categ_id.id,
                          properties)
        self.set_property(object, 'property_stock_valuation_account_id',
                          self.property_stock_valuation_account_id.id,
                          properties)
