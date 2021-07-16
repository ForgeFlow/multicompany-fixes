# Copyright 2016 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form

from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency import (
    TestAccountChartTemplate,
)


class TestSaleOrderConsistency(TestAccountChartTemplate):
    def setUp(self):
        super(TestSaleOrderConsistency, self).setUp()

        # Products
        self.product1 = self.env.ref("product.product_product_7")
        uom_unit = self.env.ref("uom.product_uom_unit")
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
        self.product2 = self.env["product.product"].create(dict_product)

        # Multi-company access rights
        group_manager = self.env.ref("sales_team.group_sale_manager")
        group_user = self.env.ref("sales_team.group_sale_salesman")
        group_mc = self.env.ref("base.group_multi_company")
        self.manager = (
            self.env["res.users"]
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
        self.manager.write({"groups_id": [(4, group_mc.id)]})
        self.user = (
            self.env["res.users"]
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
        self.user.write(
            {"groups_id": [(4, group_mc.id)], "company_ids": [(4, self.company_2.id)]}
        )
        self.user_2 = (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Daisy User 2",
                    "login": "user_2",
                    "email": "d.u@example.com",
                    "signature": "--\nDaisy",
                    "notification_type": "email",
                    "company_id": self.company_2.id,
                    "company_ids": [(4, self.company_2.id)],
                }
            )
        )
        self.user_3 = (
            self.env["res.users"]
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
        self.user_3.write({"company_ids": [(4, self.company_2.id)]})
        self.user_4 = (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Daisy User 4",
                    "login": "user_4",
                    "email": "d.u@example.com",
                    "signature": "--\nDaisy",
                    "notification_type": "email",
                    "company_id": self.company_2.id,
                    "company_ids": [(4, self.company_2.id)],
                    "groups_id": [(6, 0, [group_user.id, group_mc.id])],
                }
            )
        )

        if self.registry.get("stock.move") is not None:
            self.product2.write(
                {"responsible_id": self.user_2.id, "company_id": self.company_2.id}
            )
        else:
            self.product2.write({"company_id": self.company_2.id})

        # Create records for both companies
        self.partner_1 = self._create_partners(self.company)

        self.partner_2 = self._create_partners(self.company_2)

        self.crm_team_model = self.env["crm.team"]
        self.team_1 = self._create_crm_team(self.user.id, self.company)
        self.team_2 = self._create_crm_team(self.user_2.id, self.company_2)

        self.pricelist_1 = self._create_pricelist(self.company)
        self.pricelist_2 = self._create_pricelist(self.company_2)
        self.partner_1.with_context(
            force_company=self.company.id
        ).property_product_pricelist = self.pricelist_1
        self.partner_2.with_context(
            force_company=self.company.id
        ).property_product_pricelist = self.pricelist_2
        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_fiscal_position(self.company)
        self.fiscal_position_2 = self._create_fiscal_position(self.company_2)

        self.payment_terms_1 = self._create_payment_terms(self.company)
        self.payment_terms_2 = self._create_payment_terms(self.company_2)

        self.sale_order_1 = self._create_sale_order(
            self.company_2,
            self.product2,
            self.tax_2,
            self.partner_2,
            self.team_2,
            self.user_2,
        )
        self.sale_order_2 = self._create_sale_order(
            self.company,
            self.product1,
            self.tax_1,
            self.partner_1,
            self.team_1,
            self.user_3,
        )
        self.sale_order_3 = self._create_sale_order(
            self.company_2,
            self.product2,
            self.tax_2,
            self.partner_2,
            self.team_2,
            self.user_4,
        )

    def _create_partners(self, company):
        """Create a Partner"""
        partner = self.env["res.partner"].create(
            {"name": "Test partner", "company_id": company.id}
        )
        return partner

    def _create_crm_team(self, uid, company):
        """Create a crm team."""
        crm_team = self.crm_team_model.with_context(
            mail_create_nosubscribe=True
        ).create(
            {
                "name": "CRM team",
                "company_id": company.id,
                "favorite_user_ids": [(6, 0, [uid])],
            }
        )
        return crm_team

    def _create_pricelist(self, company):
        pricelist = self.env["product.pricelist"].create(
            {"name": "Test Pricelist", "company_id": company.id}
        )
        return pricelist

    def _create_tax(self, company):
        tax = self.env["account.tax"].create(
            {"name": "Test Tax", "company_id": company.id, "amount": 3.3}
        )
        return tax

    def _create_fiscal_position(self, company):
        fiscal_position = self.env["account.fiscal.position"].create(
            {"name": "Test Fiscal Position", "company_id": company.id}
        )
        return fiscal_position

    def _create_payment_terms(self, company):
        terms = self.env["account.payment.term"].create(
            {"name": "Test payment Terms", "company_id": company.id}
        )
        return terms

    def _create_sale_order(self, company, product, tax, partner, team, user):
        if self.registry.get("stock.move") is not None:
            sale = self.env["sale.order"].create(
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
                    # 'warehouse_id': self.env['stock.warehouse'].search(
                    #     [('company_id', '=', company.id)], limit=1).id
                }
            )
        else:
            sale = self.env["sale.order"].create(
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
