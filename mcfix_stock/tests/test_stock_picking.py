# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        stock_user_group = self.env.ref('stock.group_stock_user')
        stock_manager_group = self.env.ref('stock.group_stock_manager')
        self.picking_model = self.env['stock.picking']
        self.move_model = self.env['stock.move']
        self.location_model = self.env['stock.location']
        manager_stock_test_group = self.create_full_access(
            ['stock.picking', 'stock.move', 'stock.location'])
        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
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
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.uom_dunit = self.env['product.uom'].create({
            'name': 'DeciUnit',
            'category_id': self.uom_unit.category_id.id,
            'factor_inv': 0.1,
            'factor': 10.0,
            'uom_type': 'smaller',
            'rounding': 0.001})
        sequence = self.env['ir.sequence'].create({
            'name': 'test sequence picking type',
        })
        self.pick_in = self.env['stock.picking.type'].sudo(self.user).create({
            'name': 'Type in test',
            'code': 'incoming',
            'sequence_id': sequence.id,
            'warehouse_id': self.env['stock.warehouse'].search(
                [('company_id', '=', self.company.id)], limit=1).id
        })
        location_1 = self.env['stock.location'].sudo(self.user).create({
            'name': 'test location Customer',
            'usage': 'customer',
            'company_id': self.company.id,
        })
        self.pick_in.default_location_dest_id = location_1
        location_2 = self.env['stock.location'].sudo(self.user).create({
            'name': 'test location Supplier',
            'usage': 'supplier',
            'company_id': False,
        })
        self.partner = self.env['res.partner'].sudo(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company.id,
            'is_company': True,
        })
        self.picking_1 = self.env['stock.picking'].sudo(self.user).create({
            'location_id': location_2.id,
            'location_dest_id': self.pick_in.default_location_dest_id.id,
            'partner_id': self.partner.id,
            'picking_type_id': self.pick_in.id,
            'company_id': self.company.id,
        })
        template_1 = self.env['product.template'].sudo().create({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company.id,
            'supplier_taxes_id': False,
            'taxes_id': False,
        })
        self.move_1 = self.env['stock.move'].sudo(self.user).create({
            'name': 'test move',
            'picking_id': self.picking_1.id,
            'product_id': template_1.product_variant_id.id,
            'company_id': self.picking_1.company_id.id,
            'product_uom': template_1.product_variant_id.uom_po_id.id,
            'location_id': self.picking_1.location_id.id,
            'location_dest_id': self.picking_1.location_dest_id.id,
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
        self.picking_1.move_lines |= self.move_1
        self.picking_1._cache.update(
            self.picking_1._convert_to_cache(
                {'company_id': self.company_2.id}, update=True))
        self.picking_1._onchange_company_id()
        self.assertTrue(self.picking_1.location_id)

    def test_constrains(self):
        self.picking_1.move_lines |= self.move_1
        with self.assertRaises(ValidationError):
            self.picking_1.company_id = self.company_2
        self.picking_1.company_id = self.company
        with self.assertRaises(ValidationError):
            self.move_1.company_id = self.company_2
