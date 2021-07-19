# Copyright 2016-17 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import time

from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency import (
    TestAccountChartTemplate,
)


class TestPurchaseOrderConsistency(TestAccountChartTemplate):
    @classmethod
    def with_context(cls, *args, **kwargs):
        context = dict(args[0] if args else cls.env.context, **kwargs)
        cls.env = cls.env(context=context)
        return cls

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.account_model = cls.env["account.account"]
        cls.journal_model = cls.env["account.journal"]

        # User
        cls.user = cls.env["res.users"].create(
            {
                "name": "Daisy User",
                "login": "user",
                "email": "d.u@example.com",
                "signature": "--\nDaisy",
                "notification_type": "email",
                "company_id": cls.company_2.id,
                "company_ids": [(4, cls.company_2.id)],
            }
        )

        # Products
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_model = cls.env["product.product"]

        cls.product1 = cls.product_model.create(
            {
                "name": "Product A",
                "uom_id": cls.uom_unit.id,
                "lst_price": 1000,
                "uom_po_id": cls.uom_unit.id,
                "company_id": False,
            }
        )

        cls.product2 = cls.product_model.create(
            {
                "name": "Product B",
                "uom_id": cls.uom_unit.id,
                "lst_price": 3000,
                "uom_po_id": cls.uom_unit.id,
                "taxes_id": False,
                "supplier_taxes_id": False,
            }
        )

        cls.product2.write(
            {"responsible_id": cls.user.id, "company_id": cls.company_2.id}
        )

        # Account
        user_type = cls.env.ref("account.data_account_type_liquidity")
        cls.cash_account_id = cls.account_model.create(
            {
                "name": "Cash 1 - Test",
                "code": "test_cash_1",
                "user_type_id": user_type.id,
                "company_id": cls.company.id,
            }
        )

        cls.cash_journal = (
            cls.journal_model.with_user(cls.user)
            .sudo()
            .create(
                {
                    "name": "Cash Journal 1 - Test",
                    "code": "test_cash_1",
                    "type": "cash",
                    "company_id": cls.company.id,
                }
            )
        )
        cls.purchase_journal = (
            cls.journal_model.with_user(cls.user)
            .sudo()
            .create(
                {
                    "name": "Cash Journal 1 - Test",
                    "code": "purchase_cash_1",
                    "type": "purchase",
                    "company_id": cls.company.id,
                }
            )
        )

        # Create records for both companies
        cls.partner_1 = cls._create_partners(cls.company)
        cls.partner_2 = cls._create_partners(cls.company_2)

        cls.tax_1 = cls._create_tax(cls.company)
        cls.tax_2 = cls._create_tax(cls.company_2)

        cls.fiscal_position_1 = cls._create_fiscal_position(cls.company)
        cls.fiscal_position_2 = cls._create_fiscal_position(cls.company_2)

        cls.payment_terms_1 = cls._create_payment_terms(cls.company)
        cls.payment_terms_2 = cls._create_payment_terms(cls.company_2)

        cls.purchase1 = cls.with_context(company_id=cls.company.id)._create_purchase(
            cls.company, cls.product1, cls.tax_1, cls.partner_1
        )

        cls.purchase1.button_confirm()
        cls.invoice = cls._create_invoice(
            cls.purchase1, cls.partner_1, cls.purchase_journal, cls.cash_account_id
        )

    @classmethod
    def _create_purchase(cls, company, product, tax, partner):
        """ Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        line_values = {
            "name": product.name,
            "product_id": product.id,
            "product_qty": 100,
            "product_uom": product.uom_id.id,
            "price_unit": 50,
            "date_planned": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        }
        lines.append((0, 0, line_values))
        purchase = cls.env["purchase.order"].create(
            {"partner_id": partner.id, "order_line": lines, "company_id": company.id}
        )
        return purchase

    @classmethod
    def _create_invoice(cls, purchase, partner, journal, account):
        """ Create a vendor invoice for the purchase order."""
        invoice_vals = {
            "purchase_id": purchase.id,
            "partner_id": partner.id,
            "company_id": purchase.company_id.id,
            "journal_id": journal.id,
            "type": "in_invoice",
        }
        purchase_context = {
            "active_id": purchase.id,
            "active_ids": purchase.ids,
            "active_model": "purchase.order",
            "company_id": purchase.company_id.id,
        }
        return (
            cls.env["account.move"].with_context(purchase_context).create(invoice_vals)
        )

    @classmethod
    def _create_partners(cls, company):
        """ Create a Partner """
        partner = cls.env["res.partner"].create(
            {"name": "Test partner", "company_id": company.id}
        )
        return partner

    @classmethod
    def _create_tax(cls, company):
        tax = cls.env["account.tax"].create(
            {"name": "Test Tax", "company_id": company.id, "amount": 3.3}
        )
        return tax

    @classmethod
    def _create_fiscal_position(cls, company):
        fiscal_position = cls.env["account.fiscal.position"].create(
            {"name": "Test Fiscal Position", "company_id": company.id}
        )
        return fiscal_position

    @classmethod
    def _create_payment_terms(cls, company):
        terms = cls.env["account.payment.term"].create(
            {"name": "Test payment Terms", "company_id": company.id}
        )
        return terms

    def test_purchase_order_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(UserError):
            self.purchase1.write({"partner_id": self.partner_2.id})
        with self.assertRaises(UserError):
            self.purchase1.write({"payment_term_id": self.payment_terms_2.id})
        with self.assertRaises(UserError):
            self.purchase1.write({"fiscal_position_id": self.fiscal_position_2.id})
        with self.assertRaises(UserError):
            self.purchase1.order_line.write({"taxes_id": [(6, 0, [self.tax_2.id])]})
        with self.assertRaises(UserError):
            self.purchase1.order_line.write({"product_id": self.product2.id})
        self.assertEqual(self.purchase1.company_id, self.invoice.company_id)
