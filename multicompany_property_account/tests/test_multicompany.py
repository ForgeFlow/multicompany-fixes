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
        res = super().test_partner()
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
        return res

    def test_product_category(self):
        res = super().test_product_category()
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
        return res

    def test_product_template(self):
        res = super().test_product_template()
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
        return res
