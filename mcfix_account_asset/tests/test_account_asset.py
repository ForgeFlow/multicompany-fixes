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
            create({'name': 'Company 2'})

        self.accounts = self._create_account(self.company)
        self.accounts_2 = self._create_account(self.company_2)

        self.journal = self._create_journal(self.company)
        self.journal_2 = self._create_journal(self.company_2)

        self.assets = self._create_asset('Hardware', 3, 12000.0, 2000.0,
                                         'Laptops', self.company, self.journal,
                                         self.accounts)
        self.assets_2 = self._create_asset('Furniture', 1, 50000.0, 5000.0,
                                           'Chairs', self.company_2,
                                           self.journal_2, self.accounts_2)

    def _create_account(self, company):

        # Create Fixed Asset Account
        asset_type = self.env.ref('account.data_account_type_fixed_assets')
        xfa_account_id = self.account_model.create({
            'name': 'Asset - Test',
            'code': 'test_asset',
            'user_type_id': asset_type.id,
            'company_id': company.id,
        })

        # Create Expense account
        user_type = self.env.ref('account.data_account_type_expenses')
        expense_account_id = self.account_model.create({
            'name': 'Expense - Test',
            'code': 'test_expense',
            'user_type_id': user_type.id,
            'company_id': company.id,
        })
        return xfa_account_id, expense_account_id

    def _create_journal(self, company):

        # Create a Misc journal
        journal = self.journal_model.create({
            'name': 'Misc Journal 1 - Test',
            'code': 'test_misc_1',
            'type': 'general',
            'company_id': company.id,
        })
        return journal

    def _create_asset(self, categ_name, method_number, value, salvage_value,
                      asset_name, company, journal, accounts):
        xfa_account_id, expense_account_id = [account for account in accounts]
        asset_category = self.env['account.asset.category'].create({
            'journal_id': journal.id,
            'name': categ_name,
            'method_number': method_number,
            'company_id': company.id,
            'account_asset_id': xfa_account_id.id,
            'account_depreciation_id': xfa_account_id.id,
            'account_depreciation_expense_id': expense_account_id.id,
            })

        asset_asset = self.env['account.asset.asset'].create({
            'salvage_value': salvage_value,
            'state': 'open',
            'method_period': 12,
            'method_number': 5,
            'name': asset_name,
            'value': value,
            'company_id': company.id,
            'category_id': asset_category.id,
            })
        return asset_category, asset_asset

    def test_account_asset_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        xfa_account_id, expense_account_id = [account for account in
                                              self.accounts_2]
        asset_categ, asset_asset = [asset for asset in self.assets]
        asset_categ_2, asset_asset_2 = [asset for asset in self.assets_2]
        with self.assertRaises(ValidationError):
            asset_asset.write({'category_id': asset_categ_2.id})
        with self.assertRaises(ValidationError):
            asset_asset_2.write({'category_id': asset_categ.id})
        with self.assertRaises(ValidationError):
            asset_categ.write({'account_asset_id': xfa_account_id.id})
        with self.assertRaises(ValidationError):
            asset_categ.write({'account_depreciation_id': xfa_account_id.id})
        with self.assertRaises(ValidationError):
            asset_categ.write({'journal_id': self.journal_2.id})
        with self.assertRaises(ValidationError):
            asset_categ.write({'account_depreciation_expense_id':
                               expense_account_id.id})
