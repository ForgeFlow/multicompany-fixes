# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestStockMove(TransactionCase):

    def setUp(self):
        super(TestStockMove, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        stock_user_group = self.env.ref('stock.group_stock_user')
        stock_manager_group = self.env.ref('stock.group_stock_manager')
        self.move_model = self.env['stock.move']
        self.location_model = self.env['stock.location']
        manager_stock_test_group = self.create_full_access(
            ['stock.move', 'stock.location'])
        self.company = self.env['res.company'].with_context(
            bypass_company_validation=True
        ).create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].with_context(
            bypass_company_validation=True
        ).create({
            'name': 'Test company 2',
            'parent_id': self.company.id,
        })
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   stock_user_group.id,
                                   stock_manager_group.id,
                                   multi_company_group.id,
                                   manager_stock_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.uom_dunit = self.env['uom.uom'].create({
            'name': 'DeciUnit',
            'category_id': self.uom_unit.category_id.id,
            'factor_inv': 0.1,
            'factor': 10.0,
            'uom_type': 'smaller',
            'rounding': 0.001})

        location_1 = self.env['stock.location'].sudo(self.user).create({
            'name': 'test location Customer',
            'usage': 'customer',
            'company_id': self.company.id,
        })
        location_2 = self.env['stock.location'].sudo(self.user).create({
            'name': 'test location Supplier',
            'usage': 'supplier',
            'company_id': False,
        })
        template_1 = self.env['product.template'].sudo().create({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company.id,
        })
        self.move_1 = self.env['stock.move'].sudo(self.user).create({
            'name': 'test move',
            'product_id': template_1.product_variant_id.id,
            'location_id': location_1.id,
            'location_dest_id': location_2.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 10.0,
            'company_id': self.company.id,
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
        self.move_1._cache.update(
            self.move_1._convert_to_cache(
                {'company_id': self.company_2.id}, update=True))
        self.move_1._onchange_company_id()
        self.assertFalse(self.move_1.location_id)

    def test_constrains(self):
        with self.assertRaises(ValidationError):
            self.move_1.company_id = self.company_2
        self.move_1.company_id = self.company
        self.move_1.product_id.company_id = self.company_2
        self.move_1.location_id.company_id = False
        self.move_1.company_id = self.company_2
