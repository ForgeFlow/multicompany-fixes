# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from ..tests.test_account_chart_template_consistency import \
    TestAccountChartTemplate
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestAccountInvoice(TestAccountChartTemplate):

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        account_user_group = self.env.ref('account.group_account_user')
        account_manager_group = self.env.ref('account.group_account_manager')
        self.account_model = self.env['account.account']
        self.journal_model = self.env['account.journal']
        self.invoice_model = self.env['account.invoice']
        self.invoice_line_model = self.env['account.invoice.line']
        self.tax_model = self.env['account.tax']
        self.account_template_model = self.env['account.account.template']
        self.chart_template_model = self.env['account.chart.template']
        manager_account_test_group = self.create_full_access(
            ['account.invoice', 'account.account', 'account.journal',
             'res.partner'])

        self.company_2.parent_id = self.company.id

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

        self.chart.company_id = self.company
        self.chart_2.company_id = self.company_2

        self.partner = self.env['res.partner'].sudo(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company.id,
            'is_company': True,
        })
        self.account = self.account_model.sudo(self.user).create({
            'name': 'Account - Test',
            'code': 'test_cash',
            'user_type_id': self.user_type.id,
            'company_id': self.company.id,
        })
        self.cash_journal = self.journal_model.sudo(self.user).create({
            'name': 'Cash Journal 1 - Test',
            'code': 'test_cash_1',
            'type': 'cash',
            'company_id': self.company.id,
        })

        self.invoice = self.invoice_model.sudo(self.user).create({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'journal_id': self.cash_journal.id,
            'account_id': self.account.id,
        })
        self.tax_c1_cust = self.tax_model.create({
            'name': 'Tax c1 customer - Test',
            'amount': 10.0,
            'type_tax_use': 'sale',
            'company_id': self.company.id,
        })
        self.tax_c1_supp = self.tax_model.create({
            'name': 'Tax c1  - Test',
            'amount': 10.0,
            'type_tax_use': 'purchase',
            'company_id': self.company.id,
        })
        self.tax_c2_cust = self.tax_model.create({
            'name': 'Tax c2 customer  - Test',
            'amount': 20.0,
            'type_tax_use': 'sale',
            'company_id': self.company_2.id,
        })
        self.tax_c2_supp = self.tax_model.create({
            'name': 'Tax c2 supplier  - Test',
            'amount': 20.0,
            'type_tax_use': 'purchase',
            'company_id': self.company_2.id,
        })

        self.product_1 = self.env['product.product'].create({
            'name': 'Service product',
            'default_code': 'service_prod_1',
            'type': 'service',
            'categ_id': self.env.ref('product.product_category_all').id,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 10,
            'company_id': False,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        self.product_1.taxes_id |= self.tax_c1_cust
        self.product_1.taxes_id |= self.tax_c2_cust
        self.product_1.supplier_taxes_id |= self.tax_c1_supp
        self.product_1.supplier_taxes_id |= self.tax_c2_supp

        self.product_2 = self.env['product.product'].create({
            'name': 'Service product 2',
            'default_code': 'service_prod_2',
            'type': 'service',
            'categ_id': self.env.ref('product.product_category_all').id,
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': 10,
            'company_id': False,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })
        self.product_2.taxes_id |= self.tax_c1_cust
        self.product_2.taxes_id |= self.tax_c2_cust
        self.product_2.supplier_taxes_id |= self.tax_c1_supp
        self.product_2.supplier_taxes_id |= self.tax_c2_supp

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

    def test_invoice_onchange_01(self):
        invoice2 = self.invoice_model.sudo(self.user).new({
            'partner_id': self.partner.id,
            'company_id': self.company_2.id,
            'journal_id': self.cash_journal.id,
            'account_id': self.account.id,
        })
        invoice2._onchange_partner_id()
        invoice2._onchange_company_id()
        self.assertFalse(invoice2.partner_id)
        self.assertNotEqual(invoice2.journal_id, self.cash_journal)
        self.assertNotEqual(invoice2.account_id, self.account)

    def test_invoice_onchange_02(self):
        invoice = self.invoice_model.sudo(self.user).new({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'journal_id': self.cash_journal.id,
            'account_id': self.account.id,
        })
        invoice_line = self.invoice_line_model.sudo(self.user).new({
            'product_id': self.product_1.id,
            'company_id': self.company.id,
            'account_id': self.account.id,
            'price_unit': 1.0,
        })
        partner = self.env['res.partner'].sudo(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company_2.id,
            'is_company': True,
        })
        invoice.invoice_line_ids += invoice_line
        invoice_line.invoice_id = invoice
        invoice.company_id = self.company_2
        invoice.partner_id = partner
        invoice._onchange_company_id()
        self.assertEqual(invoice_line.invoice_line_tax_ids.company_id,
                         self.company_2)

    def test_invoice_line_1(self):
        self.invoice_line = self.invoice_line_model.sudo(self.user).create({
            'name': 'Line test',
            'company_id': self.company.id,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
            'price_unit': 1.0,
        })
        with self.assertRaises(ValidationError):
            self.invoice.company_id = self.company_2
        self.invoice.company_id = self.company
        with self.assertRaises(ValidationError):
            self.invoice_line.company_id = self.company_2

    def test_invoice_line_2(self):
        invoice_line = self.invoice_line_model.sudo(self.user).new({
            'product_id': self.product_1.id,
            'company_id': self.company.id,
            'account_id': self.account.id,
            'price_unit': 1.0,
        })
        invoice = self.invoice_model.sudo(self.user).new({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'journal_id': self.cash_journal.id,
            'account_id': self.account.id,
            'type': 'out_invoice',
        })
        invoice_line.invoice_id = invoice
        invoice.company_id = self.company_2
        invoice_line.product_id = self.product_2
        invoice_line._onchange_product_id()
        self.assertEqual(invoice_line.invoice_line_tax_ids.company_id,
                         self.company_2)

    def test_register_payments(self):
        self.invoice.state = 'open'
        self.rec_payment = self.env['account.register.payments'].\
            with_context(active_ids=[self.invoice.id]).sudo(self.user).create({
                'payment_type': 'inbound',
                'payment_method_id': self.env.ref(
                    'account.account_payment_method_manual_in').id,
                'amount': 0.0,
                'partner_id': self.partner.id,
                'journal_id': self.cash_journal.id,
                'company_id': self.company.id,
            })
        self.rec_payment.company_id = self.company_2
        self.rec_payment.company_id = self.company
        self.bank_journal = self.journal_model.sudo(self.user).create({
            'name': 'Bank Journal 1 - Test',
            'code': 'test_bank_1',
            'type': 'bank',
            'company_id': self.company_2.id,
        })
        self.rec_payment.journal_id = self.bank_journal
