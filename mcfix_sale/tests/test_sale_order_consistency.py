# Copyright 2016 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form

from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency import (
    TestAccountChartTemplate,
)


class TestSaleOrderConsistency(TestAccountChartTemplate):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Products
        cls.product1 = cls.env.ref("product.product_product_7")
        uom_unit = cls.env.ref("uom.product_uom_unit")
        dict_product = {
            "name": "Product 2",
            "uom_id": uom_unit.id,
            "standard_price": 1799.0,
            "lst_price": 3000,
            "type": "consu",
            "uom_po_id": uom_unit.id,
            "taxes_id": False,
            "supplier_taxes_id": False,
            "company_id": False,
        }
        cls.product2 = cls.env["product.product"].create(dict_product)

        # Multi-company access rights
        group_manager = cls.env.ref("sales_team.group_sale_manager")
        group_user = cls.env.ref("sales_team.group_sale_salesman")
        group_mc = cls.env.ref("base.group_multi_company")
        cls.manager = (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Andrew Manager",
                    "login": "manager",
                    "email": "a.m@example.com",
                    "signature": "--\nAndreww",
                    "notification_type": "email",
                    "groups_id": [(6, 0, [group_manager.id])],
                }
            )
        )
        cls.manager.write({"groups_id": [(4, group_mc.id)]})
        cls.user = (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Mark User",
                    "login": "user",
                    "email": "m.u@example.com",
                    "signature": "--\nMark",
                    "notification_type": "email",
                    "groups_id": [(6, 0, [group_user.id])],
                }
            )
        )
        cls.user.write(
            {"groups_id": [(4, group_mc.id)], "company_ids": [(4, cls.company_2.id)]}
        )
        cls.user_2 = (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Daisy User 2",
                    "login": "user_2",
                    "email": "d.u@example.com",
                    "signature": "--\nDaisy",
                    "notification_type": "email",
                    "company_id": cls.company_2.id,
                    "company_ids": [(4, cls.company_2.id)],
                }
            )
        )
        cls.user_3 = (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Daisy User 3",
                    "login": "user_3",
                    "email": "d.u@example.com",
                    "signature": "--\nDaisy",
                    "notification_type": "email",
                    "groups_id": [(6, 0, [group_user.id, group_mc.id])],
                }
            )
        )
        cls.user_3.write({"company_ids": [(4, cls.company_2.id)]})
        cls.user_4 = (
            cls.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Daisy User 4",
                    "login": "user_4",
                    "email": "d.u@example.com",
                    "signature": "--\nDaisy",
                    "notification_type": "email",
                    "company_id": cls.company_2.id,
                    "company_ids": [(4, cls.company_2.id)],
                    "groups_id": [(6, 0, [group_user.id, group_mc.id])],
                }
            )
        )

        if cls.registry.get("stock.move") is not None:
            cls.product2.write(
                {"responsible_id": cls.user_2.id, "company_id": cls.company_2.id}
            )
        else:
            cls.product2.write({"company_id": cls.company_2.id})

        # Create records for both companies
        cls.partner_1 = cls._create_partners(cls.company)

        cls.partner_2 = cls._create_partners(cls.company_2)

        cls.crm_team_model = cls.env["crm.team"]
        cls.team_1 = cls._create_crm_team(cls.user.id, cls.company)
        cls.team_2 = cls._create_crm_team(cls.user_2.id, cls.company_2)

        cls.pricelist_1 = cls._create_pricelist(cls.company)
        cls.pricelist_2 = cls._create_pricelist(cls.company_2)
        cls.partner_1.with_context(
            force_company=cls.company.id
        ).property_product_pricelist = cls.pricelist_1
        cls.partner_2.with_context(
            force_company=cls.company.id
        ).property_product_pricelist = cls.pricelist_2
        cls.tax_1 = cls._create_tax(cls.company)
        cls.tax_2 = cls._create_tax(cls.company_2)

        cls.fiscal_position_1 = cls._create_fiscal_position(cls.company)
        cls.fiscal_position_2 = cls._create_fiscal_position(cls.company_2)

        cls.payment_terms_1 = cls._create_payment_terms(cls.company)
        cls.payment_terms_2 = cls._create_payment_terms(cls.company_2)

        cls.sale_order_1 = cls._create_sale_order(
            cls.company_2,
            cls.product2,
            cls.tax_2,
            cls.partner_2,
            cls.team_2,
            cls.user_2,
        )
        cls.sale_order_2 = cls._create_sale_order(
            cls.company, cls.product1, cls.tax_1, cls.partner_1, cls.team_1, cls.user_3,
        )
        cls.sale_order_3 = cls._create_sale_order(
            cls.company_2,
            cls.product2,
            cls.tax_2,
            cls.partner_2,
            cls.team_2,
            cls.user_4,
        )

    @classmethod
    def _create_partners(cls, company):
        """Create a Partner"""
        partner = cls.env["res.partner"].create(
            {"name": "Test partner", "company_id": company.id}
        )
        return partner

    @classmethod
    def _create_crm_team(cls, uid, company):
        """Create a crm team."""
        crm_team = cls.crm_team_model.with_context(mail_create_nosubscribe=True).create(
            {
                "name": "CRM team",
                "company_id": company.id,
                "favorite_user_ids": [(6, 0, [uid])],
            }
        )
        return crm_team

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
    def _create_sale_order(cls, company, product, tax, partner, team, user):
        if cls.registry.get("stock.move") is not None:
            sale = cls.env["sale.order"].create(
                {
                    "partner_id": partner.id,
                    "company_id": company.id,
                    "team_id": team.id,
                    "user_id": user.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "tax_id": [(6, 0, [tax.id])],
                                "name": "Sale Order Line",
                            },
                        )
                    ],
                    # 'warehouse_id': cls.env['stock.warehouse'].search(
                    #     [('company_id', '=', company.id)], limit=1).id
                }
            )
        else:
            sale = cls.env["sale.order"].create(
                {
                    "partner_id": partner.id,
                    "company_id": company.id,
                    "team_id": team.id,
                    "user_id": user.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "tax_id": [(6, 0, [tax.id])],
                                "name": "Sale Order Line",
                            },
                        )
                    ],
                }
            )
        return sale

    def test_sale_order_security(self):
        """ Test Security of Company Sale Order"""
        # User in company 1
        self.user.write(
            {"company_id": self.company.id, "company_ids": [(4, self.company.id)]}
        )
        so_ids = (
            self.env["sale.order"]
            .with_user(self.user)
            .search([("company_id", "=", self.company_2.id)])
        )
        self.assertEqual(
            so_ids,
            self.env["sale.order"],
            "A user in company %s shouldn't be able "
            "to see %s sales orders" % (self.user.company_id.name, self.company_2.name),
        )

    def test_sale_order_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(UserError):
            self.sale_order_2.write({"partner_id": self.partner_2.id})
        with self.assertRaises(UserError):
            self.sale_order_2.write({"payment_term_id": self.payment_terms_2.id})
        with self.assertRaises(UserError):
            self.sale_order_2.write({"team_id": self.team_2.id})
        with self.assertRaises(UserError):
            self.sale_order_2.write({"fiscal_position_id": self.fiscal_position_2.id})
        with self.assertRaises(UserError):
            self.sale_order_2.order_line.write({"tax_id": [(6, 0, [self.tax_2.id])]})
        with self.assertRaises(UserError):
            self.sale_order_2.order_line.write({"product_id": self.product2.id})

    def test_sale_order_invoice_consistency(self):
        self.sale_order_1.action_confirm()
        move = self.sale_order_1._create_invoices()
        move.partner_id.company_id = False
        self.assertTrue(move)
        form = Form(move)
        form.company_id = self.company
        with self.assertRaises(ValidationError):
            form.save()
