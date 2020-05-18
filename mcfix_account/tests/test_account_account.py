# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TestAccountAccount(TransactionCase):

    def setUp(self):
        super(TestAccountAccount, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.account_model = self.env['account.account']
        self.tax_model = self.env['account.tax']
        manager_account_test_group = self.create_full_access(
            ['account.account'])
        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
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
                                   account_user_group.id,
                                   account_manager_group.id,
                                   multi_company_group.id,
                                   manager_account_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id), (4, self.company_2.id)],
             })

        self.user_type = self.env.ref('account.data_account_type_liquidity')

        self.account = self.account_model.with_user(self.user).create({
            'name': 'Account - Test',
            'code': 'test_cash',
            'user_type_id': self.user_type.id,
            'company_id': self.company.id,
        })

        self.tax = self.tax_model.with_user(self.user).create({
            'name': 'Tax - Test',
            'amount': 0.0,
            'company_id': self.company.id,
            'invoice_repartition_line_ids': [
                (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.account.id,
                }),
            ],
            'refund_repartition_line_ids': [
                (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                (0, 0, {
                    'factor_percent': 100,
                    'repartition_type': 'tax',
                    'account_id': self.account.id,
                }),
            ],
        })

    def create_full_access(self, list_of_models):
        manager_account_test_group = self.env['res.groups'].sudo().create({
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
                access.group_id = manager_account_test_group
        return manager_account_test_group

    def test_onchanges(self):
        self.account.tax_ids |= self.tax
        self.assertIn(self.tax, self.account.tax_ids)
        with self.assertRaises(ValidationError):
            self.account.company_id = self.company_2
            self.assertNotIn(self.tax, self.account.tax_ids)

    def test_constrains(self):
        tax_2 = self.tax_model.with_user(self.user).create({
            'name': 'Tax - Test',
            'amount': 0.0,
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            self.account.company_id = self.company_2
        self.account.company_id = self.company
        with self.assertRaises(UserError):
            tax_2.write({
                'invoice_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100,
                            'repartition_type': 'base'}),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': self.account.id,
                    }),
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100,
                            'repartition_type': 'base'}),
                    (0, 0, {
                        'factor_percent': 100,
                        'repartition_type': 'tax',
                        'account_id': self.account.id,
                    }),
                ],
            })
        with self.assertRaises(UserError):
            self.account.tax_ids |= tax_2
