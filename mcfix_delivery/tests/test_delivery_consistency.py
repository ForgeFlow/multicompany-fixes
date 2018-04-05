# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDeliveryConsistency(TransactionCase):

    def setUp(self):
        super(TestDeliveryConsistency, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.company_2 = self.env['res.company'].create({
            'name': 'company 2'
        })
        self.wh = self.env.ref('stock.warehouse0')
        self.wh_2 = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company_2.id)], limit=1)
        self.normal_product = self.env['product.product'].create({
            'name': 'Stockable product',
            'default_code': 'stock_prod',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 10,
            'company_id': False,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        self.delivery_product = self.env['product.product'].create({
            'name': 'Delivery product',
            'default_code': 'del_prod',
            'type': 'service',
            'categ_id': self.env.ref('product.product_category_all').id,
            'sale_ok': False,
            'purchase_ok': False,
            'list_price': 10,
            'company_id': self.company.id,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        self.delivery_product_2 = self.env['product.product'].create({
            'name': 'Delivery product',
            'default_code': 'del_prod',
            'type': 'service',
            'categ_id': self.env.ref('product.product_category_all').id,
            'sale_ok': False,
            'purchase_ok': False,
            'list_price': 10,
            'company_id': self.company_2.id,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        self.carrier_company = self.env['delivery.carrier'].create({
            'name': 'Main company delivery charges',
            'fixed_price': 10.0,
            'sequence': 4,
            'delivery_type': 'fixed',
            'product_id': self.delivery_product.id,
            'company_id': self.company.id,
        })
        self.carrier_company_2 = self.env['delivery.carrier'].create({
            'name': 'Company 2 delivery charges',
            'fixed_price': 10.0,
            'sequence': 4,
            'delivery_type': 'fixed',
            'product_id': self.delivery_product_2.id,
            'company_id': self.company_2.id,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'company_id': False,
        })
        self.partner.with_context(
            force_company=self.company_2.id).property_delivery_carrier_id = \
            self.carrier_company_2
        self.partner.with_context(
            force_company=self.company.id).property_delivery_carrier_id = \
            self.carrier_company

    def test_sale_delivery_onchanges(self):
        sale_order = self.env['sale.order'].new({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
        })
        sale_order.onchange_partner_id_carrier_id()
        self.assertEquals(sale_order.carrier_id,
                          self.carrier_company)
        sale_order.company_id = self.company_2
        sale_order._onchange_company_id()
        self.assertEquals(sale_order.carrier_id,
                          self.carrier_company_2)

    def test_sale_delivery_company_consistency(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'company_id': self.company_2.id,
            'carrier_id': self.carrier_company_2.id,
            'warehouse_id': self.wh_2.id,
        })
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(ValidationError):
            sale_order.write(
                {'carrier_id': self.carrier_company.id})

    def test_sale_picking_carrier_company_consistency(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'carrier_id': self.carrier_company.id,
            'warehouse_id': self.wh.id,
            'order_line': [(0, 0, {'product_id': self.normal_product.id,
                                   'tax_id': False,
                                   'name': 'Sale Order Line'})],
        })
        sale_order.action_confirm()
        pick = sale_order.picking_ids
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(ValidationError):
            pick.carrier_id = self.carrier_company_2

    def test_picking_onchanges(self):
        picking = self.env['stock.picking'].new({
            'picking_type_id': self.ref(
                'stock.picking_type_out'),
            'location_id': self.env.ref(
                'stock.stock_location_stock').id,
            'location_dest_id': self.env.ref(
                'stock.stock_location_customers').id,
            'carrier_id': self.carrier_company.id,
        })
        picking.carrier_id = self.carrier_company_2
        picking._onchange_company_id()
        self.assertEquals(picking.carrier_id,
                          self.carrier_company_2)
