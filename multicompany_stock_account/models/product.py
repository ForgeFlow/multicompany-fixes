from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_valuation = fields.Selection(readonly=True)

    property_cost_method = fields.Selection(readonly=True)

    property_stock_account_input = fields.Many2one(readonly=True)
    property_stock_account_output = fields.Many2one(readonly=True)


class ProductProperty(models.Model):
    _inherit = 'product.template.property'

    property_valuation = fields.Selection([
        ('manual_periodic', 'Periodic (manual)'),
        ('real_time', 'Perpetual (automated)')], string='Inventory Valuation', copy=True, default='manual_periodic',
        help="If perpetual valuation is enabled for a product, the system will automatically create journal entries corresponding to stock moves, with product price as specified by the 'Costing Method'" \
             "The inventory variation account set on the product category will represent the current inventory value, and the stock input and stock output account will hold the counterpart moves for incoming and outgoing products.")

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('average', 'Average Price'),
        ('real', 'Real Price')], string='Costing Method', copy=True, default='standard',
        help="""Standard Price: The cost price is manually updated at the end of a specific period (usually once a year).
                        Average Price: The cost price is recomputed at each incoming shipment and used for the product valuation.
                        Real Price: The cost price displayed is the price of the last outgoing product (will be use in case of inventory loss for example).""")
    property_stock_account_input = fields.Many2one(
        'account.account', 'Stock Input Account', domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the source location. When not set on the product, the one from the product category is used.")
    property_stock_account_output = fields.Many2one(
        'account.account', 'Stock Output Account', domain=[('deprecated', '=', False)],
        help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the destination location. When not set on the product, the one from the product category is used.")

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_valuation', False):
            self.set_property(object, 'property_valuation', vals.get('property_valuation', False), properties)
        if vals.get('property_cost_method', False):
            self.set_property(object, 'property_cost_method', vals.get('property_cost_method', False), properties)
        if vals.get('property_stock_account_input', False):
            self.set_property(object, 'property_stock_account_input', vals.get('property_stock_account_input', False), properties)
        if vals.get('property_stock_account_output', False):
            self.set_property(object, 'property_stock_account_output', vals.get('property_stock_account_output', False), properties)
        return super(ProductProperty, self).set_properties(object, vals, properties)