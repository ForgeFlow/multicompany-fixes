# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountAssetMC(TransactionCase):

    def setUp(self):
        super(TestAccountAssetMC, self).setUp()
        self.res_users_model = self.env['res.users']
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']

        # Company
        self.company = self.env.ref('base.main_company')

        self.company_2 = self.env['res.company'].\
            create({'name': 'Company 2',
                    'parent_id': self.company.id})

        self.cash_journal = self._create_journal(self.company)

        self._create_asset(self.company)

    def _create_journal(self, company):

        self.journal_id = self.env['account.journal'].\
            search([('type', '=', 'general'),
                    ('id', '!=',
                     self.company.currency_exchange_journal_id.id)],
                   limit=1)
        self.xfa_account_id = self.env['account.account'].\
            search([('user_type_id', '=', self.env.
                     ref('account.data_account_type_fixed_assets').id)],
                    limit=1)
        if not self.xfa_account_id:
            self.xfa_account_id = self.env['account.account'].\
                search([('user_type_id', '=', self.env.
                         ref('account.data_account_type_current_assets').id)],
                       limit=1)
        # Create expense account
        user_type = self.env.ref('account.data_account_type_expenses')
        self.expense_account_id = self.account_model.create({
            'name': 'Expense - Test',
            'code': 'test_expense',
            'user_type_id': user_type.id,
            'company_id': self.company.id,
        })
        self.expense_account_id_2 = self.account_model.create({
            'name': 'Expense - Test',
            'code': 'test_expense',
            'user_type_id': user_type.id,
            'company_id': self.company_2.id,
        })

        # Create a cash account
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.cash_account_id = self.account_model.create({
            'name': 'Cash 1 - Test',
            'code': 'test_cash_1',
            'user_type_id': user_type.id,
            'company_id': company.id,
        })

        # Create a journal for cash account
        cash_journal = self.journal_model.create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash_1',
            'type': 'cash',
            'company_id': company.id,
            'default_debit_account_id': self.cash_account_id.id,
            'default_credit_account_id': self.cash_account_id.id,
        })
        return cash_journal

    def _create_asset(self, company):
        self.asset_category = self.env['account.asset.category'].create({
                'journal_id': self.journal_id.id,
                'name': 'Hardware',
                'method_number': 3,
                'company_id': company.id,
                'account_asset_id': self.xfa_account_id.id,
                'account_depreciation_id': self.xfa_account_id.id,
                'account_depreciation_expense_id': self.expense_account_id.id,
            })
        self.xfa_account_id.company_id = self.company_2
        self.journal_id.company_id = self.company_2
        self.asset_category_2 = self.env['account.asset.category'].create({
                'journal_id': self.journal_id.id,
                'name': 'Cars',
                'method_number': 5,
                'company_id': self.company_2.id,
                'account_asset_id': self.xfa_account_id.id,
                'account_depreciation_id': self.xfa_account_id.id,
                'account_depreciation_expense_id': self.expense_account_id_2.id,
            })

        self.asset_asset = self.env['account.asset.asset'].create({
                'salvage_value': 2000.0,
                'state': 'open',
                'method_period': 12,
                'method_number': 5,
                'name': "Laptops",
                'value': 12000.0,
                'company_id': company.id,
                'category_id': self.asset_category.id,
            })

    def test_account_asset_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(ValidationError):
            self.asset_asset.\
                write({'category_id': self.asset_category_2.id})
