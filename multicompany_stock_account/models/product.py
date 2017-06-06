from odoo import models, api, fields


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductTemplate, self).get_properties()

        self.property_valuation = self.get_property(
            self.property, 'property_valuation', self.categ_id.property_valuation)
        self.property_cost_method = self.get_property(
            self.property, 'property_cost_method', self.categ_id.property_cost_method)
        self.property_stock_account_input = self.get_property(
            self.property, 'property_stock_account_input', self.categ_id.property_stock_account_input_categ_id)
        self.property_stock_account_output = self.get_property(
            self.property, 'property_stock_account_output', self.categ_id.property_stock_account_output_categ_id)

    property_valuation = fields.Selection(
        company_dependent=False,
        default=get_properties,
        compute='get_properties')

    property_cost_method = fields.Selection(
        company_dependent=False,
        default=get_properties,
        compute='get_properties'
    )

    property_stock_account_input = fields.Many2one(
        'account.account',
        company_dependent=False,
        default=get_properties,
        compute='get_properties')
    property_stock_account_output = fields.Many2one(
        'account.account',
        company_dependent=False,
        default=get_properties,
        compute='get_properties')


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
