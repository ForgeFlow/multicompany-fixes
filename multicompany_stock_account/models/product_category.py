from odoo import models, fields, api


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'multicompany.abstract']

    @api.one
    def get_properties(self):
        super(ProductCategory, self).get_properties()
        ir_property_obj = self.env['ir.property']
        self.property_valuation = self.get_property(
            self.property, 'property_valuation', ir_property_obj.get('property_valuation', 'product.category'))
        self.property_cost_method = self.get_property(
            self.property, 'property_cost_method', ir_property_obj.get('property_cost_method', 'product.category'))
        self.property_stock_journal = self.get_property(
            self.property, 'property_stock_journal', self.current_company_id.default_stock_journal)
        self.property_stock_account_input_categ_id = self.get_property(
            self.property, 'property_stock_account_input_categ_id',
            self.current_company_id.default_stock_account_input_categ_id)
        self.property_stock_account_output_categ_id = self.get_property(
            self.property, 'property_stock_account_output_categ_id',
            self.current_company_id.default_stock_account_output_categ_id)
        self.property_stock_valuation_account_id = self.get_property(
            self.property, 'property_stock_valuation_account_id',
            self.current_company_id.default_stock_valuation_account_id)

    property_valuation = fields.Selection(
        copy=False, required=False,
        company_dependent=False,
        store=False,
        compute='get_properties',
        default=get_properties)

    property_cost_method = fields.Selection(
        company_dependent=False, copy=False, required=False,
        store=False,
        compute='get_properties',
        default=get_properties)
    property_stock_journal = fields.Many2one(
        comodel_name='account.journal',
        company_dependent=False,
        store=False,
        compute='get_properties',
        default=get_properties
    )
    property_stock_account_input_categ_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=False,
        store=False,
        compute='get_properties',
        default=get_properties)
    property_stock_account_output_categ_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=False,
        store=False,
        compute='get_properties',
        default=get_properties
    )
    property_stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=False,
        store=False,
        compute='get_properties',
        default=get_properties)


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
