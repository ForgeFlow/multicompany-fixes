# © 2016-17 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from ..tests.test_account_chart_template_consistency import \
    TestAccountChartTemplate
from odoo.exceptions import ValidationError


class TestAccountJournalConsistency(TestAccountChartTemplate):

    def setUp(self):
        super(TestAccountJournalConsistency, self).setUp()
        self.res_users_model = self.env['res.users']
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']

        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })
        self.currency_euro = self.env.ref('base.EUR')
        self.cash_journal = self._create_journal(self.company)
        self.account_1 = self._create_account(self.company)
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
            self.cash_journal.\
                write({'profit_account_id': self.account_2.id})
        self.cash_journal.profit_account_id = False

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'loss_account_id': self.account_2.id})
        self.cash_journal.loss_account_id = False

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'default_debit_account_id': self.account_2.id})
        self.cash_journal.default_debit_account_id = False

        with self.assertRaises(ValidationError):
            self.cash_journal.\
                write({'default_credit_account_id': self.account_2.id})
        self.cash_journal.default_credit_account_id = False

        with self.assertRaises(ValidationError):
            self.cash_journal.account_control_ids += self.account_2
        self.cash_journal.account_control_ids = False

        self.cash_journal.account_control_ids += self.account_1

        with self.assertRaises(ValidationError):
            self.cash_journal.write(
                {'company_id': self.company_2.id})

        # Changing the company on a journal should change that of the
        # associated sequence and accounts
        journal = self.journal_model.create({
            'name': 'Bank Journal 1 - Test',
            'code': 'test_bank_1',
            'type': 'bank',
            'company_id': self.company.id,
            'bank_acc_number': '0001',
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
        # sequence that is already assigned to a journal that belongs to
        # another company
        with self.assertRaises(ValidationError):
            self.cash_journal.sequence_id.company_id = self.company

        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '0002',
            'bank_id': self.bank.id,
            'company_id': self.company.id,
            'currency_id': self.currency_euro.id,
            'partner_id': self.company.partner_id.id,
        })

        with self.assertRaises(ValidationError):
            journal.write({'bank_account_id': bank_account.id})
        journal.bank_account = False

        with self.assertRaises(ValidationError):
            self.journal_model.create({
                'name': 'Bank Journal 2 - Test',
                'code': 'test_bank_2',
                'type': 'bank',
                'company_id': self.company_2.id,
                'bank_account_id': bank_account.id,
            })

        # Test validation on refund sequence
        journal = self.journal_model.create({
            'name': 'Sale Journal 1 - Test',
            'code': 'test_sale_1',
            'type': 'sale',
            'company_id': self.company.id,
            'refund_sequence': True
        })
        with self.assertRaises(ValidationError):
            journal.refund_sequence_id.company_id = self.company_2
