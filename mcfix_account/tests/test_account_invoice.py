# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError

from ..tests.test_account_chart_template_consistency import TestAccountChartTemplate

_logger = logging.getLogger(__name__)


class TestAccountInvoice(TestAccountChartTemplate):
    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        employees_group = cls.env.ref("base.group_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        account_user_group = cls.env.ref("account.group_account_user")
        account_manager_group = cls.env.ref("account.group_account_manager")
        cls.account_model = cls.env["account.account"]
        cls.journal_model = cls.env["account.journal"]
        cls.invoice_model = cls.env["account.move"]
        cls.invoice_line_model = cls.env["account.move.line"]
        cls.tax_model = cls.env["account.tax"]
        cls.account_template_model = cls.env["account.account.template"]
        cls.chart_template_model = cls.env["account.chart.template"]
        manager_account_test_group = cls.create_full_access(
            ["account.move", "account.account", "account.journal", "res.partner"]
        )

        cls.company_2.parent_id = cls.company.id

        cls.env.user.company_ids += cls.company
        cls.env.user.company_ids += cls.company_2

        cls.user = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                employees_group.id,
                                account_user_group.id,
                                account_manager_group.id,
                                multi_company_group.id,
                                manager_account_test_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )

        cls.user_type = cls.env.ref("account.data_account_type_liquidity")

        cls.partner = (
            cls.env["res.partner"]
            .with_user(cls.user)
            .create(
                {
                    "name": "Partner Test",
                    "company_id": cls.company.id,
                    "is_company": True,
                }
            )
        )
        cls.account = cls.account_model.with_user(cls.user).create(
            {
                "name": "Account - Test",
                "code": "test_cash",
                "user_type_id": cls.user_type.id,
                "company_id": cls.company.id,
            }
        )
        cls.cash_journal = cls.journal_model.with_user(cls.user).create(
            {
                "name": "Cash Journal 1 - Test",
                "code": "test_cash_1",
                "type": "cash",
                "company_id": cls.company.id,
            }
        )
        cls.sale_journal = cls.journal_model.with_user(cls.user).create(
            {
                "name": "Sale Journal 1 - Test",
                "code": "test_sale_1",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )

        cls.invoice = cls.invoice_model.with_user(cls.user).create(
            {
                "partner_id": cls.partner.id,
                "company_id": cls.company.id,
                "journal_id": cls.sale_journal.id,
                "type": "out_invoice",
            }
        )
        cls.tax_c1_cust = cls.tax_model.create(
            {
                "name": "Tax c1 customer - Test",
                "amount": 10.0,
                "type_tax_use": "sale",
                "company_id": cls.company.id,
            }
        )
        cls.tax_c1_supp = cls.tax_model.create(
            {
                "name": "Tax c1  - Test",
                "amount": 10.0,
                "type_tax_use": "purchase",
                "company_id": cls.company.id,
            }
        )
        cls.tax_c2_cust = cls.tax_model.create(
            {
                "name": "Tax c2 customer  - Test",
                "amount": 20.0,
                "type_tax_use": "sale",
                "company_id": cls.company_2.id,
            }
        )
        cls.tax_c2_supp = cls.tax_model.create(
            {
                "name": "Tax c2 supplier  - Test",
                "amount": 20.0,
                "type_tax_use": "purchase",
                "company_id": cls.company_2.id,
            }
        )

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Service product",
                "default_code": "service_prod_1",
                "type": "service",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "sale_ok": True,
                "purchase_ok": False,
                "list_price": 10,
                "company_id": False,
                "taxes_id": [(6, 0, (cls.tax_c1_cust | cls.tax_c2_cust).ids)],
                "supplier_taxes_id": [(6, 0, (cls.tax_c1_supp | cls.tax_c2_supp).ids)],
            }
        )

        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Service product 2",
                "default_code": "service_prod_2",
                "type": "service",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "sale_ok": True,
                "purchase_ok": False,
                "list_price": 10,
                "company_id": False,
                "taxes_id": False,
                "supplier_taxes_id": False,
            }
        )
        cls.product_2.taxes_id |= cls.tax_c1_cust
        cls.product_2.taxes_id |= cls.tax_c2_cust
        cls.product_2.supplier_taxes_id |= cls.tax_c1_supp
        cls.product_2.supplier_taxes_id |= cls.tax_c2_supp

    @classmethod
    def create_full_access(cls, list_of_models):
        manager_account_test_group = (
            cls.env["res.groups"].sudo().create({"name": "group_manager_product_test"})
        )
        for model in list_of_models:
            model_id = cls.env["ir.model"].sudo().search([("model", "=", model)])
            if model_id:
                access = (
                    cls.env["ir.model.access"]
                    .sudo()
                    .create(
                        {
                            "name": "full_access_%s" % model.replace(".", "_"),
                            "model_id": model_id.id,
                            "perm_read": True,
                            "perm_write": True,
                            "perm_create": True,
                            "perm_unlink": True,
                        }
                    )
                )
                access.group_id = manager_account_test_group
        return manager_account_test_group

    def test_invoice_onchange_01(self):
        invoice2 = self.invoice_model.with_user(self.user).new(
            {
                "partner_id": self.partner.id,
                "company_id": self.company_2.id,
                "journal_id": self.cash_journal.id,
                "type": "out_invoice",
            }
        )
        invoice2._onchange_partner_id()
        # invoice2._onchange_company_id()
        # self.assertFalse(invoice2.partner_id)
        # self.assertNotEqual(invoice2.journal_id, self.cash_journal)
        # self.assertNotEqual(invoice2.account_id, self.account)

    def test_invoice_onchange_02(self):
        invoice = self.invoice_model.with_user(self.user).new(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "type": "out_invoice",
                "journal_id": self.cash_journal.id,
            }
        )
        invoice_line = self.invoice_line_model.with_user(self.user).new(
            {
                "product_id": self.product_1.id,
                "company_id": self.company.id,
                "account_id": self.account.id,
                "price_unit": 1.0,
            }
        )
        partner = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {
                    "name": "Partner Test",
                    "company_id": self.company_2.id,
                    "is_company": True,
                }
            )
        )
        invoice.invoice_line_ids += invoice_line
        invoice_line.move_id = invoice
        invoice.company_id = self.company_2
        invoice.partner_id = partner
        # invoice._onchange_company_id()
        # self.assertEqual(
        #     invoice_line.mapped('tax_ids.company_id'),
        #     self.company_2
        # )

    def test_invoice_line_1(self):
        self.invoice_line = self.invoice_line_model.with_user(self.user).create(
            {
                "name": "Line test",
                "company_id": self.company.id,
                "account_id": self.account.id,
                "move_id": self.invoice.id,
                "price_unit": 1.0,
            }
        )
        with self.assertRaises(UserError):
            self.invoice.company_id = self.company_2
        self.invoice.company_id = self.company
        with self.assertRaises(UserError):
            self.invoice_line.company_id = self.company_2

    def test_invoice_line_2(self):
        invoice_line = self.invoice_line_model.with_user(self.user).new(
            {
                "product_id": self.product_1.id,
                "company_id": self.company.id,
                "account_id": self.account.id,
                "price_unit": 1.0,
            }
        )
        invoice = self.invoice_model.with_user(self.user).new(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
                "journal_id": self.cash_journal.id,
                "type": "out_invoice",
            }
        )
        invoice_line.move_id = invoice
        invoice.company_id = self.company_2
        invoice_line.product_id = self.product_2
        invoice_line._onchange_product_id()
        self.assertEqual(invoice_line.tax_ids.company_id, self.company_2)

    def test_register_payments(self):
        self.invoice.state = "posted"
        self.invoice.invoice_payment_state = "not_paid"
        self.rec_payment = (
            self.env["account.payment.register"]
            .with_context(active_ids=[self.invoice.id])
            .with_user(self.user)
            .create(
                {
                    "payment_method_id": self.env.ref(
                        "account.account_payment_method_manual_in"
                    ).id,
                    "journal_id": self.cash_journal.id,
                }
            )
        )
        self.rec_payment.company_id = self.company_2
        self.rec_payment.company_id = self.company
        self.bank_journal = self.journal_model.with_user(self.user).create(
            {
                "name": "Bank Journal 1 - Test",
                "code": "test_bank_1",
                "type": "bank",
                "company_id": self.company_2.id,
            }
        )
        self.rec_payment.journal_id = self.bank_journal
