# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TestMCfixAccountBudget(TransactionCase):

    def setUp(self):
        super(TestMCfixAccountBudget, self).setUp()

        # Company
        self.company = self.env.ref('base.main_company')

        self.company_2 = self.env['res.company'].\
            create({'name': 'Company 2'})

        self.group_mc = self.env.ref('base.group_multi_company')
        self.user1 = self._create_user(self.company, 'user_1')
        self.user2 = self._create_user(self.company_2, 'user_2')

        self.analytic_account = self.\
            _create_analytic_account(self.company,
                                     'Analytic Account for Test')
        self.analytic_account_2 = self.\
            _create_analytic_account(self.company_2,
                                     'Analytic Account for Test2')

        self.budget_position = self._create_budget_position(self.company,
                                                            'test_account')
        self.budget_position_2 = self._create_budget_position(self.company_2,
                                                              'test_account_2')

        self.budget = self._create_budget(self.company, self.user1,
                                          self.budget_position,
                                          self.analytic_account)
        self.budget_2 = self._create_budget(self.company_2, self.user2,
                                            self.budget_position_2,
                                            self.analytic_account_2)

    def _create_analytic_account(self, company, name):
        analytic_account = self.env['account.analytic.account'].create({
            'name': name,
            'company_id': company.id
            })
        return analytic_account

    def _create_user(self, company, login):

        user = self.env['res.users'].create({
            'name': 'User 1',
            'login': login,
            'email': 'sample@example.com',
            'signature': '--\nSample',
            'notify_email': 'always',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, [self.group_mc.id])],
        })
        return user

    def _create_budget_position(self, company, code):
        user_type_id = self.env.ref('account.data_account_type_revenue')
        tag_id = self.env.ref('account.account_tag_operating')

        account_rev = self.env['account.account'].create({
            'code': code,
            'company_id': company.id,
            'name': 'Budget - MCfix Test Revenue Account',
            'user_type_id': user_type_id.id,
            'tag_ids': [(4, tag_id.id, 0)]
        })

        buget_post = self.env['account.budget.post'].create({
            'name': 'MCfix Sales',
            'account_ids': [(4, account_rev.id, 0)],
            'company_id': company.id,
        })
        return buget_post

    def _create_budget(self, company, user, budget_position, analytic_account):

        crossovered_budget = self.env['crossovered.budget'].create({
            'name': 'test budget name',
            'date_from': '2014-01-01',
            'date_to': '2014-12-31',
            'company_id': company.id,
            'creating_user_id': user.id,
        })

        self.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': crossovered_budget.id,
            'general_budget_id': budget_position.id,
            'analytic_account_id': analytic_account.id,
            'date_from': '2014-01-01',
            'date_to': '2014-12-31',
            'planned_amount': -364,
        })

        return crossovered_budget

    def test_mcfix_account_budget(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(ValidationError):
            self.budget.write({'creating_user_id': self.user2.id})
        with self.assertRaises(ValidationError):
            self.budget.crossovered_budget_line.\
                write({'general_budget_id': self.budget_position_2.id})
        with self.assertRaises(ValidationError):
            self.budget.crossovered_budget_line.\
                write({'analytic_account_id': self.analytic_account_2.id})
