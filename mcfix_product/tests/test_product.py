# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestProduct(TransactionCase):

    def setUp(self):
        super(TestProduct, self).setUp()
        employees_group = self.env.ref('base.group_user')
        manager_product_test_group = self.create_full_access(
            ['product.price.history', 'product.template', 'product.product',
             'ir.property'])
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
                                   manager_product_test_group.id])],
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

    def create_full_access(self, list_of_models):
        manager_product_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_product_test'
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
                access.group_id = manager_product_test_group
        return manager_product_test_group

    def test_template(self):
        template_1 = self.env['product.template'].sudo().create({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company_2.id,
        })
        self.assertEqual(
            template_1.product_variant_id.company_id, self.company_2)
        template_1.company_id = self.company
        self.assertEqual(
            template_1.product_variant_id.company_id, self.company)
        product_1 = self.env['product.product'].sudo().create(
            {'name': 'Test 1',
             'type': 'consu',
             'uom_id': self.uom_dunit.id,
             'uom_po_id': self.uom_dunit.id,
             'product_tmpl_id': template_1.id,
             'company_id': self.company.id,
             })
        product_1.company_id = self.company_2
        self.assertEqual(template_1.company_id, self.company_2)
        self.assertEqual(product_1.company_id, self.company_2)
        template_1.company_id = self.company
        self.assertEqual(product_1.company_id, self.company)

    def test_product(self):
        template_1 = self.env['product.template'].sudo(self.user).create({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company.id,
        })
        product_1 = self.env['product.product'].sudo(self.user).create(
            {'name': 'Test 1',
             'type': 'consu',
             'uom_id': self.uom_dunit.id,
             'uom_po_id': self.uom_dunit.id,
             'company_id': self.company_2.id,
             })
        product_1.product_tmpl_id = template_1
        self.assertEqual(product_1.company_id, self.company)

    def test_product_price(self):
        product_1 = self.env['product.product'].sudo(self.user).create(
            {'name': 'Test 1',
             'type': 'consu',
             'uom_id': self.uom_dunit.id,
             'uom_po_id': self.uom_dunit.id,
             'company_id': self.company_2.id,
             'standard_price': 23.0,
             })
        product_history = self.env['product.price.history'].search(
            [('product_id', '=', product_1.id),
             ('company_id', '=', self.company_2.id)], limit=1)
        self.assertEqual(len(product_history), 1)
