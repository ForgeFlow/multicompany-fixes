# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.tests.account_test_users import AccountTestUsers
from odoo.exceptions import ValidationError


class TestAccountJournalMC(AccountTestUsers):

    def setUp(self):
        super(TestAccountJournalMC, self).setUp()
        self.res_users_model = self.env['res.users']
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']

        # Company
        self.company_1 = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })

        self.cash_journal = self._create_journal(self.company_1)
        self.account_1 = self._create_account(self.company_1)
        self.account_2 = self._create_account(self.company_2)
        self.bank = self._create_bank()
        self.sequence_c2 = self.env['ir.sequence'].create({
            'name': 'test',
            'implementation': 'no_gap',
            'prefix': 'PR',
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
            'company_id': self.company_2.id,
        })

    def _create_account(self, company):
        user_type = self.env.ref('account.data_account_type_liquidity')
        return self.account_model.create({
            'name': 'Cash - Test',
            'code': 'test_cash',
            'user_type_id': user_type.id,
            'company_id': company.id,
        })

    def _create_journal(self, company):
        cash_journal = self.journal_model.create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash_1',
            'type': 'cash',
            'company_id': company.id,
        })
        return cash_journal

    def _create_bank(self):
        return self.env['res.bank'].create({
            'name': 'bank 1',
        })

    def test_journal_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields

        with self.assertRaises(ValidationError):
            self.cash_journal.write(
                {'default_debit_account_id': self.account_2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'default_credit_account_id': self.account_2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'profit_account_id': self.account_2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'loss_account_id': self.account_2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'sequence_id': self.sequence_c2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'refund_sequence_id': self.sequence_c2.id})

        with self.assertRaises(ValidationError):
            self.cash_journal.account_control_ids += self.account_2

        self.cash_journal.account_control_ids = False
        self.cash_journal.account_control_ids += self.account_1

        with self.assertRaises(ValidationError):
            self.cash_journal.write(
                {'company_id': self.company_2.id})

        # Assign a bank account on another company should raise an error
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0001',
            'bank_id': self.bank.id,
            'company_id': self.company_1.id,
            'currency_id': self.currency_euro.id,
            'partner_id': self.company_1.partner_id.id,
        })

        with self.assertRaises(ValidationError):
            self.journal_model.create({
                'name': 'Cash Journal 2 - Test',
                'code': 'test_cash_2',
                'type': 'cash',
                'company_id': self.company_2.id,
                'bank_account_id': bank_account.id,
            })

        # Changing the company on a journal should change that of the
        # associated sequence and accounts
        journal = self.journal_model.create({
            'name': 'Bank Journal 1 - Test',
            'code': 'test_bank_1',
            'type': 'bank',
            'company_id': self.company_1.id,
            'bank_acc_number': '0002',
            'bank_id': self.bank.id,
        })

        journal.company_id = self.company_2

        self.assertEquals(journal.sequence_id.company_id, self.company_2)
        self.assertEquals(journal.default_debit_account_id.company_id,
                          self.company_2)
        self.assertEquals(journal.default_credit_account_id.company_id,
                          self.company_2)
        self.assertEquals(journal.bank_account_id.company_id,
                          self.company_2)

        # Test that a user cannot change the company of the ir.sequence for a
        #  sequence that is already assigned to a journal that belongs to
        # another company
        with self.assertRaises(ValidationError):
            self.cash_journal.sequence_id.company_id = self.company_2
        with self.assertRaises(ValidationError):
            self.cash_journal.refund_sequence_id.company_id = self.company_2
