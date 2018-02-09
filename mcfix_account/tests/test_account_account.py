# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

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

        self.user = self.env['res.users'].sudo(self.env.user).with_context(
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
             'company_ids': [(4, self.company.id)],
             })

        self.user_type = self.env.ref('account.data_account_type_liquidity')

        self.tax = self.tax_model.sudo(self.user).create({
            'name': 'Tax - Test',
            'amount': 0.0,
            'company_id': self.company.id,
        })
        self.account = self.account_model.sudo(self.user).create({
            'name': 'Account - Test',
            'code': 'test_cash',
            'user_type_id': self.user_type.id,
            'company_id': self.company.id,
        })
        self.tax.account_id = self.account

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
        self.account._cache.update(
            self.account._convert_to_cache(
                {'company_id': self.company_2.id}, update=True))
        self.account._onchange_company_id()
        self.assertNotIn(self.tax, self.account.tax_ids)

    def test_constrains(self):
        tax_2 = self.tax_model.sudo(self.user).create({
            'name': 'Tax - Test',
            'amount': 0.0,
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            self.account.company_id = self.company_2
        self.account.company_id = self.company
        with self.assertRaises(ValidationError):
            tax_2.account_id = self.account
        with self.assertRaises(ValidationError):
            self.account.tax_ids |= tax_2
