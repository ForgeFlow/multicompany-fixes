# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestPaymentAcquirer(TransactionCase):

    def setUp(self):
        super(TestPaymentAcquirer, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.journal_model = self.env['account.journal']
        self.payment_acquirer_model = self.env['payment.acquirer']
        manager_account_test_group = self.create_full_access(
            ['account.move', 'account.journal', 'account.account',
             'res.partner'])
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
                                   manager_account_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.bank_journal = self.journal_model.sudo(self.user).create({
            'name': 'Bank Journal 1 - Test',
            'code': 'test_bank_1',
            'type': 'bank',
            'company_id': self.company.id,
        })

        self.view_template = self.env['ir.ui.view'].\
            search([('name', '=', 'default_acquirer_button')])

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
        self.payment_acquirer = self.payment_acquirer_model.sudo().\
            new({
                'name': 'Payment Acquirer 1 - Test',
                'journal_id': self.bank_journal.id,
                'company_id': self.company_2.id,
                'view_template_id': self.view_template.id,
            })
        self.payment_acquirer._onchange_company_id()
        self.assertFalse(self.payment_acquirer.journal_id)

    def test_constrains(self):
        self.payment_acquirer = self.payment_acquirer_model.sudo().\
            create({
                'name': 'Payment Acquirer 1 - Test',
                'journal_id': self.bank_journal.id,
                'company_id': self.company.id,
                'view_template_id': self.view_template.id,
            })
        with self.assertRaises(ValidationError):
            self.payment_acquirer.company_id = self.company_2
        self.payment_acquirer.company_id = self.company
        with self.assertRaises(ValidationError):
            self.payment_acquirer.journal_id.company_id = self.company_2
