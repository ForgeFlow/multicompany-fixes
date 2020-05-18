# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAnalytic(TransactionCase):

    def setUp(self):
        super(TestAnalytic, self).setUp()
        employees_group = self.env.ref('base.group_user')
        analytic_accounting_group = \
            self.env.ref('analytic.group_analytic_accounting')
        manager_account_test_group = self.create_full_access(
            ['account.analytic.account', 'account.analytic.line',
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

        self.user = self.env['res.users'].with_user(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   analytic_accounting_group.id,
                                   manager_account_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.partner_1 = self.env['res.partner'].with_user(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company.id,
            'is_company': True,
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

    def test_analytic_account(self):
        analytic_1 = self.env['account.analytic.account'].with_user(self.user).new({
            'name': 'Test Analytic',
            'partner_id': self.partner_1.id,
            'company_id': self.company_2.id,
        })
        analytic_1._onchange_company_id()
        self.assertNotEqual(analytic_1.partner_id, self.partner_1)
