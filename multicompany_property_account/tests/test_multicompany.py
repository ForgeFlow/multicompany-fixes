# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.multicompany_property_product.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def create_company(self, name):
        company = super().create_company(name)
        chart_template_id = self.env["account.chart.template"].search([], limit=1)
        if not company.chart_template_id:
            self.env.user.write(
                {"company_ids": [(4, company.id)], "company_id": company.id}
            )
            chart_template_id.try_loading()
        return company

    def test_partner(self):
        super().test_partner()
        account = self.env["account.account"].search(
            [
                ("deprecated", "=", False),
                ("internal_type", "=", "payable"),
                ("company_id", "=", self.company_1.id),
            ],
            limit=1,
        )
        self.assertTrue(account)
        prop = self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        )
        prop.write({"property_account_payable_id": account.id})
        self.assertEqual(
            self.partner.with_company(self.company_1).property_account_payable_id,
            account,
        )
        self.assertEqual(
            self.partner.with_company(self.company_1).property_account_payable_id,
            prop.property_account_payable_id,
        )

    def test_product_category(self):
        super().test_product_category()
        account = self.env["account.account"].search(
            [("deprecated", "=", False), ("company_id", "=", self.company_1.id)],
            limit=1,
        )
        self.assertTrue(account)
        prop = self.category.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        )
        prop.write({"property_account_income_categ_id": account.id})
        self.assertEqual(
            self.category.with_company(self.company_1).property_account_income_categ_id,
            account,
        )
        self.assertEqual(
            self.category.with_company(self.company_1).property_account_income_categ_id,
            prop.property_account_income_categ_id,
        )

    def test_product_template(self):
        super().test_product_template()
        account = self.env["account.account"].search(
            [("deprecated", "=", False), ("company_id", "=", self.company_1.id)],
            limit=1,
        )
        self.assertTrue(account)
        prop = self.product_template.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        )
        prop.write({"property_account_income_id": account.id})
        self.assertEqual(
            self.product_template.with_company(
                self.company_1
            ).property_account_income_id,
            account,
        )
        self.assertEqual(
            self.product_template.with_company(
                self.company_1
            ).property_account_income_id,
            prop.property_account_income_id,
        )

    def test_sync_partner_child_commercial_fields(self):
        """
        When a value for a property is edited and the field is part of the commercial
        fields stated in Odoo standard, also sync the fields to it's children contacts.
        Using `property_payment_term_id` as the field in the test but it could be any
        other company dependent + commercial field.
        """
        comm_fields = self.env["res.partner"]._commercial_fields()
        self.assertTrue("property_payment_term_id" in comm_fields)
        self.env.companies = self.company_1 + self.company_2
        parent_c1_prop = self.partner.property_ids.filtered(
            lambda p: p.company_id == self.company_1
        )
        parent_c2_prop = self.partner.property_ids.filtered(
            lambda p: p.company_id == self.company_2
        )
        self.partner.write(
            {
                "property_ids": [
                    [
                        1,
                        parent_c1_prop.id,
                        {"property_payment_term_id": self.payment_term_1.id},
                    ],
                    [
                        1,
                        parent_c2_prop.id,
                        {"property_payment_term_id": self.payment_term_2.id},
                    ],
                ]
            }
        )
        self.assertEqual(
            self.partner.with_context(
                force_company=self.company_1.id
            ).property_payment_term_id,
            self.payment_term_1,
        )
        self.assertEqual(
            self.partner.with_context(
                force_company=self.company_2.id
            ).property_payment_term_id,
            self.payment_term_2,
        )
        self.assertEqual(
            self.child.with_context(
                force_company=self.company_1.id
            ).property_payment_term_id,
            self.payment_term_1,
        )
        self.assertEqual(
            self.child.with_context(
                force_company=self.company_2.id
            ).property_payment_term_id,
            self.payment_term_2,
        )
