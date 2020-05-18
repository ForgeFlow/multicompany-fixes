# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TestStockInventory(TransactionCase):

    def setUp(self):
        super(TestStockInventory, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        stock_user_group = self.env.ref('stock.group_stock_user')
        stock_manager_group = self.env.ref('stock.group_stock_manager')
        tracking_owner_group = self.env.ref('stock.group_tracking_owner')
        self.inventory_model = self.env['stock.inventory']
        self.location_model = self.env['stock.location']
        manager_stock_test_group = self.create_full_access(
            ['stock.inventory', 'stock.location'])
        self.company = self.env['res.company'].with_context(
            bypass_company_validation=True
        ).create({
            'name': '1 Company',
        })
        self.company_2 = self.env['res.company'].with_context(
            bypass_company_validation=True
        ).create({
            'name': '2 Company',
            'parent_id': self.company.id,
        })
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].with_user(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   stock_user_group.id,
                                   stock_manager_group.id,
                                   tracking_owner_group.id,
                                   multi_company_group.id,
                                   manager_stock_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id), (4, self.company_2.id)],
             })
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.uom_dunit = self.env['uom.uom'].create({
            'name': 'DeciUnit',
            'category_id': self.uom_unit.category_id.id,
            'factor_inv': 0.1,
            'factor': 10.0,
            'uom_type': 'smaller',
            'rounding': 0.001})

        location_1 = self.env['stock.location'].with_user(self.user).create({
            'name': 'test location Customer',
            'usage': 'customer',
            'company_id': self.company.id,
        })
        self.location_2 = self.env['stock.location'].with_user(self.user).create({
            'name': 'test location Supplier',
            'usage': 'supplier',
            'company_id': self.company_2.id,
        })
        self.template_1 = self.env['product.template'].sudo().create({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company.id,
        })
        self.inventory_1 = self.env['stock.inventory'].with_user(
            self.user).create({
                'name': 'test inventory',
                'product_ids': [(4, self.template_1.product_variant_id.id)],
                'location_ids': [(4, location_1.id)],
                'company_id': self.company.id,
                'start_empty': False,
            })

    def create_full_access(self, list_of_models):
        manager_stock_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_stock_test'
        })
        for model in list_of_models:
            model_id = self.env['ir.model'].sudo().search(
                [('model', '=', model)])
            if model_id:
                access = self.env['ir.model.access'].sudo().create({
                    'name': 'full_access_%s' % model.replace(".", "_"),
                    'model_id': model_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                })
                access.group_id = manager_stock_test_group
        return manager_stock_test_group

    def test_onchanges(self):
        inventory_form = Form(self.inventory_1)
        inventory_form.company_id = self.company_2
        self.assertFalse(inventory_form.product_ids)

    def test_constrains(self):
        with self.assertRaises(UserError):
            self.inventory_1.company_id = self.company_2
        self.inventory_1.company_id = self.company
        with self.assertRaises(UserError):
            self.inventory_1.location_ids = [(6, 0, self.location_2.ids)]

    def test_create_inventory(self):
        # When creating an inventory without indicating the company,
        # it should default to the company associated to the location.
        self.template_1.company_id = False
        inventory = self.env['stock.inventory'].with_user(
            self.user).create({
                'name': 'test inventory',
                'product_ids': [(4, self.template_1.product_variant_id.id)],
                'location_ids': [(4, self.location_2.id)],
                'start_empty': False,
            })
        self.assertEquals(inventory.company_id, self.company_2)
