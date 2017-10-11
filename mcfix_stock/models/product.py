# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(ProductTemplate, self).onchange_company_id()
        self.property_stock_procurement = False
        self.property_stock_production = False
        self.property_stock_inventory = False
        self.location_id = False
        self.warehouse_id = False
        self.route_ids = False
        self.route_from_categ_ids = False

    @api.multi
    @api.constrains('property_stock_procurement', 'company_id')
    def _check_company_property_stock_procurement(self):
        for template in self.sudo():
            if template.company_id and template.property_stock_procurement.\
                    company_id and template.company_id != template.\
                    property_stock_procurement.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('property_stock_production', 'company_id')
    def _check_company_property_stock_production(self):
        for template in self.sudo():
            if template.company_id and template.property_stock_production.\
                    company_id and template.company_id != template.\
                    property_stock_production.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      ' must be the same.'))
        return True

    @api.multi
    @api.constrains('property_stock_inventory', 'company_id')
    def _check_company_property_stock_inventory(self):
        for template in self.sudo():
            if template.company_id and template.property_stock_inventory.\
                    company_id and template.company_id != template.\
                    property_stock_inventory.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Property Stock Inventory must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for template in self.sudo():
            if template.company_id and template.location_id.company_id and \
                    template.company_id != template.location_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('warehouse_id', 'company_id')
    def _check_company_warehouse_id(self):
        for template in self.sudo():
            if template.company_id and template.warehouse_id.company_id and \
                    template.company_id != template.warehouse_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Warehouse must be the same.'))
        return True

    @api.multi
    @api.constrains('route_ids', 'company_id')
    def _check_company_route_ids(self):
        for template in self.sudo():
            for stock_location_route in template.route_ids:
                if template.company_id and stock_location_route.company_id \
                        and template.company_id != stock_location_route.\
                        company_id:
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Location Route must be the same.'))
        return True

    @api.multi
    @api.constrains('route_from_categ_ids', 'company_id')
    def _check_company_route_from_categ_ids(self):
        for template in self.sudo():
            for stock_location_route in template.route_from_categ_ids:
                if template.company_id and stock_location_route.company_id and\
                        template.company_id != stock_location_route.company_id:
                    raise ValidationError(
                        _('The Company in the Product and in '
                          'Category Route must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        super(ProductTemplate, self)._check_company_id()
        for rec in self:
            location_route = self.env['stock.location.route'].search(
                [('product_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if location_route:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Location Route '
                      '%s.' % location_route.name))
