# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class ProductCategoryProperty(models.TransientModel):
    _inherit = 'product.category.property'

    property_valuation = fields.Selection([
        ('manual_periodic', 'Periodic (manual)'),
        ('real_time', 'Perpetual (automated)')], string='Inventory Valuation',
        compute='_compute_property_fields',
        readonly=False,
        help="If perpetual valuation is enabled for a product, the system "
             "will automatically create journal entries corresponding to "
             "stock moves, with product price as specified by the 'Costing "
             "Method'. The inventory variation account set on the product "
             "category will represent the current inventory value, and the "
             "stock input and stock output account will hold the counterpart "
             "moves for incoming and outgoing products.")

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')], string="Costing Method",
        compute='_compute_property_fields',
        readonly=False,
        help="Standard Price: The products are valued at their standard cost "
        "defined on the product.\nAverage Cost (AVCO): The products are "
        "valued at weighted average cost.\nFirst In First Out (FIFO): The "
        "products are valued supposing those that enter the company first "
        "will also leave it first.")
    property_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal',
        compute='_compute_property_fields',
        readonly=False,
        help="When doing real-time inventory valuation, this is "
             "the Accounting Journal in which entries will be "
             "automatically posted when stock moves are processed.")
    property_stock_account_input_categ_id = fields.Many2one(
        'account.account', 'Stock Input Account',
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False,
        help="When doing real-time inventory valuation, counterpart "
             "journal items for all incoming stock moves will be posted "
             "in this account, unless "
             "there is a specific valuation account set on the "
             "source location. This is the default value for all products "
             "in this category. It "
             "can also directly be set on each product")
    property_stock_account_output_categ_id = fields.Many2one(
        'account.account', 'Stock Output Account',
        domain=[('deprecated', '=', False)],
        compute='_compute_property_fields',
        readonly=False,
        help="When doing real-time inventory valuation, counterpart journal "
             "items for all outgoing stock moves will be posted in this "
             "account, unless there is a specific valuation account set "
             "on the destination location. This is the default value "
             "for all products in this category. It "
             "can also directly be set on each product")
    property_stock_valuation_account_id = fields.Many2one(
        'account.account', 'Stock Valuation Account',
        compute='_compute_property_fields',
        readonly=False,
        domain=[('deprecated', '=', False)],
        help="When real-time inventory valuation is enabled "
             "on a product, this account will hold the current "
             "value of the products.", )

    @api.multi
    def get_property_fields(self, object, properties):
        super(ProductCategoryProperty, self).get_property_fields(
            object, properties)
        for rec in self:
            rec.property_valuation = rec.get_property_value(
                'property_valuation', object, properties)
            rec.property_cost_method = rec.get_property_value(
                'property_cost_method', object, properties)
            rec.property_stock_journal = rec.get_property_value(
                'property_stock_journal', object, properties)
            rec.property_stock_account_input_categ_id = rec.get_property_value(
                'property_stock_account_input_categ_id', object, properties)
            rec.property_stock_account_output_categ_id = rec.\
                get_property_value('property_stock_account_output_categ_id',
                                   object, properties)
            rec.property_stock_valuation_account_id = rec.get_property_value(
                'property_stock_valuation_account_id', object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(ProductCategoryProperty, self).get_property_fields_list()
        res.append('property_valuation')
        res.append('property_cost_method')
        res.append('property_stock_journal')
        res.append('property_stock_account_input_categ_id')
        res.append('property_stock_account_output_categ_id')
        res.append('property_stock_valuation_account_id')
        return res
