# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.multicompany_property_base.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def setUp(self):
        super().setUp()
        self.analytic_account_model = self.env["account.analytic.account"]
        self.an_acc_1 = self.analytic_account_model.create(
            {"name": "Analytic Account 1"}
        )
        self.an_acc_2 = self.analytic_account_model.create(
            {"name": "Analytic Account 2"}
        )
        self.an_acc_3 = self.analytic_account_model.create(
            {"name": "Analytic Account 3"}
        )
        self.an_acc_4 = self.analytic_account_model.create(
            {"name": "Analytic Account 4"}
        )

    def test_partner(self):
        res = super().test_partner()
        self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        ).property_analytic_account_id = self.an_acc_1
        self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_2
        ).property_analytic_account_id = self.an_acc_2
        self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        ).property_supplier_analytic_account_id = self.an_acc_3
        self.partner.property_ids.filtered(
            lambda r: r.company_id == self.company_2
        ).property_supplier_analytic_account_id = self.an_acc_4
        self.assertEqual(
            self.partner.with_company(self.company_1.id).property_analytic_account_id,
            self.an_acc_1,
        )
        self.assertEqual(
            self.partner.with_company(self.company_2.id).property_analytic_account_id,
            self.an_acc_2,
        )
        self.assertEqual(
            self.partner.with_company(
                self.company_1.id
            ).property_supplier_analytic_account_id,
            self.an_acc_3,
        )
        self.assertEqual(
            self.partner.with_company(
                self.company_2.id
            ).property_supplier_analytic_account_id,
            self.an_acc_4,
        )
        return res
