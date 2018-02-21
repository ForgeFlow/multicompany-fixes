# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestAccountAssetCategory(TransactionCase):

    def setUp(self):
        super(TestAccountAssetCategory, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']
        self.category_model = self.env['account.asset.category']
        manager_account_test_group = self.create_full_access(
            ['account.asset.category'])
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

        self.account = self.account_model.sudo(self.user).create({
            'name': 'Account - Test',
            'code': 'test_account',
            'user_type_id': self.user_type.id,
            'company_id': self.company.id,
        })

        self.cash_journal = self.journal_model.sudo(self.user).create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash',
            'type': 'cash',
            'company_id': self.company.id,
        })

        self.asset_category = self.category_model.sudo(self.user).create({
            'name': 'Asset Category - Test',
            'journal_id': self.cash_journal.id,
            'account_asset_id': self.account.id,
            'account_depreciation_id': self.account.id,
            'account_depreciation_expense_id': self.account.id,
            'company_id': self.company.id,
        })

    def create_full_access(self, list_of_models):
        manager_account_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_asset_test'
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
        self.asset_category._cache.update(
            self.asset_category._convert_to_cache(
                {'company_id': self.company_2.id}, update=True))
        self.asset_category._onchange_company_id()
        self.assertFalse(self.asset_category.journal_id)

    def test_constrains(self):
        self.cash_journal_2 = self.journal_model.sudo(self.user).create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash',
            'type': 'cash',
            'company_id': self.company_2.id,
        })
        with self.assertRaises(ValidationError):
            self.asset_category.company_id = self.company_2
        self.asset_category.company_id = self.company
        with self.assertRaises(ValidationError):
            self.asset_category.journal_id = self.cash_journal_2
