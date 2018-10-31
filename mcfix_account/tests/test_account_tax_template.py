# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestAccountTaxTemplate(TransactionCase):

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def _chart_of_accounts_create(self, company, chart):
        _logger.debug('Creating chart of account')
        self.env.user.write({
            'company_ids': [(4, company.id)],
            'company_id': company.id,
        })
        self.with_context(
            company_id=company.id, force_company=company.id)
        wizard = self.env['wizard.multi.charts.accounts'].create({
            'company_id': company.id,
            'chart_template_id': chart.id,
            'code_digits': 6,
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': chart.transfer_account_id.id,
        })
        wizard.onchange_chart_template_id()
        wizard.execute()
        return True

    def setUp(self):
        super(TestAccountTaxTemplate, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.tax_template_model = self.env['account.tax.template']
        ir_model_data = self.env['ir.model.data']
        manager_account_test_group = self.create_full_access(
            ['account.account.template', 'account.chart.template',
             'account.tax.template'])
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

        self.chart = self.env['account.chart.template'].search([], limit=1)
        self._chart_of_accounts_create(self.company, self.chart)
        account_template = self.env['account.account.template'].create({
            'name': 'Test 1',
            'code': 'Code_test',
            'user_type_id': self.user_type.id,
        })
        self.env['ir.model.data'].create({
            'name': account_template.name,
            'module': 'account',
            'model': 'account.account.template',
            'res_id': account_template.id,
            'noupdate': 0,
        })
        self.chart_2 = self.env['account.chart.template'].create({
            'name': 'Test Chart',
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': account_template.id,
        })

        account_template_data = ir_model_data.create(
            {'name': 'test_template',
             'model': 'account.account.template',
             'module': 'account',
             'res_id': account_template.id,
             })

        account_template.chart_template_id = self.chart_2
        self.chart_2.tax_template_ids |= self.chart.tax_template_ids

        self._chart_of_accounts_create(self.company_2, self.chart_2)

        self.chart.company_id = self.company
        self.chart_2.company_id = self.company_2

        self.tax_template = self.tax_template_model.sudo(self.user).create({
            'name': 'Tax Template 1 - Test',
            'amount': 0.0,
            'chart_template_id': self.chart.id,
            'company_id': self.company.id,
        })
        self.child_tax_1 = self.tax_template_model.sudo(self.user).create({
            'name': 'Child Tax Template 1 - Test',
            'amount': 0.0,
            'chart_template_id': self.chart.id,
            'company_id': self.company.id,
        })

        del account_template_data

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
        self.tax_template.children_tax_ids |= self.child_tax_1
        self.assertEqual(self.tax_template.chart_template_id, self.chart)
        self.tax_template._cache.update(
            self.tax_template._convert_to_cache(
                {'company_id': self.company_2.id}, update=True))
        self.tax_template._onchange_company_id()
        self.assertEqual(self.tax_template.chart_template_id, self.chart_2)

    def test_constrains(self):
        with self.assertRaises(ValidationError):
            self.tax_template.company_id = self.company_2
        with self.assertRaises(ValidationError):
            self.tax_template.children_tax_ids |= self.child_tax_1
        self.tax_template.company_id = self.company
        with self.assertRaises(ValidationError):
            self.chart.company_id = self.company_2
