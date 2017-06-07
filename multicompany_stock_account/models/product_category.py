from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_valuation = fields.Selection(readonly=True)
    property_cost_method = fields.Selection(readonly=True)
    property_stock_journal = fields.Many2one(readonly=True)
    property_stock_account_input_categ_id = fields.Many2one(readonly=True)
    property_stock_account_output_categ_id = fields.Many2one(readonly=True)
    property_stock_valuation_account_id = fields.Many2one(readonly=True)


class ProductCategoryProperty(models.Model):
    _inherit = 'product.category.property'

    property_valuation = fields.Selection([
        ('manual_periodic', 'Periodic (manual)'),
        ('real_time', 'Perpetual (automated)')], string='Inventory Valuation',
        company_dependent=False, copy=True, required=True,
        default='manual_periodic',
        help="If perpetual valuation is enabled for a product, the system "
             "will automatically create journal entries corresponding to "
             "stock moves, with product price as specified by the 'Costing "
             "Method'. The inventory variation account set on the product "
             "category will represent the current inventory value, and the "
             "stock input and stock output account will hold the counterpart "
             "moves for incoming and outgoing products.")

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('average', 'Average Price'),
        ('real', 'Real Price')], string="Costing Method",
        default='standard',
        copy=True, required=True,
        help="Standard Price: The cost price is manually updated at the end "
             "of a specific period (usually once a year).\nAverage Price: "
             "The cost price is recomputed at each incoming shipment and "
             "used for the product valuation.\nReal Price: The cost price "
             "displayed is the price of the last outgoing product (will be "
             "used in case of inventory loss for example).""")
    property_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal',
        help="When doing real-time inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed.")
    property_stock_account_input_categ_id = fields.Many2one(
        'account.account', 'Stock Input Account',
        domain=[('deprecated', '=', False)], oldname="property_stock_account_input_categ",
        help="When doing real-time inventory valuation, counterpart journal items for all incoming stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the source location. This is the default value for all products in this category. It "
             "can also directly be set on each product")
    property_stock_account_output_categ_id = fields.Many2one(
        'account.account', 'Stock Output Account',
        domain=[('deprecated', '=', False)], oldname="property_stock_account_output_categ",
        help="When doing real-time inventory valuation, counterpart journal items for all outgoing stock moves will be posted in this account, unless "
             "there is a specific valuation account set on the destination location. This is the default value for all products in this category. It "
             "can also directly be set on each product")
    property_stock_valuation_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account',
        domain=[('deprecated', '=', False)],
        help="When real-time inventory valuation is enabled on a product, this account will hold the current value of the products.", )

    @api.model
    def set_properties(self, object, vals, properties=False):
        if vals.get('property_valuation', False):
            self.set_property(object, 'property_valuation', vals.get('property_valuation', False), properties)
        if vals.get('property_cost_method', False):
            self.set_property(object, 'property_cost_method', vals.get('property_cost_method', False), properties)
        if vals.get('property_stock_journal', False):
            self.set_property(object, 'property_stock_journal', vals.get('property_stock_journal', False), properties)
        if vals.get('property_stock_account_input_categ_id', False):
            self.set_property(object, 'property_stock_account_input_categ_id', vals.get('property_stock_account_input_categ_id', False), properties)
        if vals.get('property_stock_account_output_categ_id', False):
            self.set_property(object, 'property_stock_account_output_categ_id', vals.get('property_stock_account_output_categ_id', False), properties)
        if vals.get('property_stock_valuation_account_id', False):
            self.set_property(object, 'property_stock_valuation_account_id', vals.get('property_stock_valuation_account_id', False), properties)
        return super(ProductCategoryProperty, self).set_properties(object, vals, properties)
