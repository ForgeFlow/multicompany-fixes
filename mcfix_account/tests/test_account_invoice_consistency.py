# Copyright 2016-17 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import UserError

from ..tests.test_account_chart_template_consistency import TestAccountChartTemplate


class TestAccountInvoiceConsistency(TestAccountChartTemplate):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceConsistency, cls).setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.account_model = cls.env["account.account"]
        cls.journal_model = cls.env["account.journal"]

        cls.journal_c1 = cls._create_journal("J1", cls.company)
        cls.journal_c2 = cls._create_journal("J2", cls.company_2)

        cls.pricelist_1 = cls._create_pricelist(cls.company)
        cls.pricelist_2 = cls._create_pricelist(cls.company_2)

        cls.tax_1 = cls._create_tax(cls.company)
        cls.tax_2 = cls._create_tax(cls.company_2)

        cls.fiscal_position_1 = cls._create_fiscal_position(cls.company)
        cls.fiscal_position_2 = cls._create_fiscal_position(cls.company_2)
        cls.main_partner.with_context(
            force_company=cls.company.id
        ).property_account_position_id = cls.fiscal_position_1
        cls.main_partner.with_context(
            force_company=cls.company_2.id
        ).property_account_position_id = cls.fiscal_position_2
        cls.partner_2 = cls.env["res.partner"].create(
            {"name": "Partner 2", "company_id": cls.company_2.id}
        )

        cls.payment_term_1 = cls._create_payment_terms(cls.company)
        cls.payment_term_2 = cls._create_payment_terms(cls.company_2)

        cls.account_invoice = cls._create_account_invoice(cls.company)

    @classmethod
    def _create_journal(cls, name, company):
        # Create a cash account
        # Create a journal for cash account
        cash_journal = cls.journal_model.create(
            {"name": name, "code": name, "type": "sale", "company_id": company.id}
        )
        return cash_journal

    @classmethod
    def _create_pricelist(cls, company):
        pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist", "company_id": company.id}
        )
        return pricelist

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

    @classmethod
    def _create_account_invoice(cls, company):
        invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.main_partner.id,
                "company_id": company.id,
                "fiscal_position_id": cls.fiscal_position_1.id,
                "invoice_payment_term_id": cls.payment_term_1.id,
                "journal_id": cls.journal_c1.id,
                "type": "out_invoice",
            }
        )
        return invoice

    def test_invoice_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # for company dependent fields
        with self.assertRaises(UserError):
            self.account_invoice.write(
                {"fiscal_position_id": self.fiscal_position_2.id}
            )
        with self.assertRaises(UserError):
            self.account_invoice.write(
                {"invoice_payment_term_id": self.payment_term_2.id}
            )
        with self.assertRaises(UserError):
            self.account_invoice.write({"journal_id": self.journal_c2.id})
        with self.assertRaises(UserError):
            self.account_invoice.write({"partner_id": self.partner_2.id})
