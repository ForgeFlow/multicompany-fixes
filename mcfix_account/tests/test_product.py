# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestProduct(TransactionCase):

    def setUp(self):
        super(TestProduct, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        manager_product_test_group = self.create_full_access(
            ['product.price.history', 'product.template', 'product.product'])
        self.tax_model = self.env['account.tax']
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
                                   multi_company_group.id,
                                   account_user_group.id,
                                   account_manager_group.id,
                                   manager_product_test_group.id])],
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

        self.tax = self.tax_model.sudo(self.user).create({
            'name': 'Tax 1 - Test',
            'amount': 0.0,
            'company_id': self.company.id,
        })

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
            'company_id': self.company.id,
            'supplier_taxes_id': False,
            'taxes_id': False,
        })
        template_1.taxes_id |= self.tax
        self.tax_2 = self.tax_model.sudo(self.user).create({
            'name': 'Tax 2 - Test',
            'amount': 0.0,
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            template_1.taxes_id |= self.tax_2
        for tax in template_1.taxes_id:
            with self.assertRaises(ValidationError):
                tax.company_id = self.company_2
            tax.company_id = self.company
        template_2 = self.env['product.template'].sudo().new({
            'name': 'Test',
            'uom_id': self.uom_unit.id,
            'uom_po_id': self.uom_unit.id,
            'company_id': self.company_2.id,
            'supplier_taxes_id': [self.tax.id],
            'taxes_id': [self.tax_2.id],
        })
        template_2._onchange_company_id()
        self.assertEqual(len(template_2.taxes_id), 0)
        self.assertEqual(len(template_2.supplier_taxes_id), 0)

    def test_product(self):
        product_1 = self.env['product.product'].sudo().create(
            {'name': 'Test 1',
             'type': 'consu',
             'uom_id': self.uom_dunit.id,
             'uom_po_id': self.uom_dunit.id,
             'company_id': self.company.id,
             'supplier_taxes_id': False,
             'taxes_id': False,
             })
        product_1.taxes_id |= self.tax
        self.tax_2 = self.tax_model.sudo(self.user).create({
            'name': 'Tax 2 - Test',
            'amount': 0.0,
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            product_1.taxes_id |= self.tax_2
        for tax in product_1.taxes_id:
            with self.assertRaises(ValidationError):
                tax.company_id = self.company_2
            tax.company_id = self.company
        with self.assertRaises(ValidationError):
            product_1.company_id = self.company_2
