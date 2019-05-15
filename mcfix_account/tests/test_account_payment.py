# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestAccountPayment(TransactionCase):

    def setUp(self):
        super(TestAccountPayment, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.journal_model = self.env['account.journal']
        self.payment_model = self.env['account.payment']
        manager_account_test_group = self.create_full_access(
            ['account.payment', 'account.journal', 'res.partner'])
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
                                   multi_company_group.id,
                                   account_manager_group.id,
                                   manager_account_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.partner = self.env['res.partner'].sudo(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company.id,
            'is_company': True,
        })
        self.cash_journal = self.journal_model.sudo(self.user).create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash_1',
            'type': 'cash',
            'company_id': self.company.id,
        })
        self.payment = self.payment_model.sudo(self.user).create({
            'payment_type': 'inbound',
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_in').id,
            'amount': 0.0,
            'partner_id': self.partner.id,
            'journal_id': self.cash_journal.id,
            'company_id': self.company.id,
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

    def test_constrains(self):
        with self.assertRaises(ValidationError):
            self.payment.partner_id.company_id = self.company_2

        partner_2 = self.env['res.partner'].sudo(self.user).create({
            'name': 'Partner 2 Test',
            'company_id': self.company_2.id,
            'is_company': True,
        })
        with self.assertRaises(ValidationError):
            self.payment.partner_id = partner_2
