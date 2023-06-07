# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestMulticompanyProperty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company_1 = self.create_company("company 1")
        self.company_2 = self.create_company("company 2")
        self.partner = self.env["res.partner"].create(
            {"name": "Partner", "company_id": False}
        )
        self.child = self.env["res.partner"].create(
            {"name": "Child", "parent_id": self.partner.id}
        )
        self.payment_term_1 = self.env["account.payment.term"].create({"name": "PT 1"})
        self.payment_term_2 = self.env["account.payment.term"].create({"name": "PT 2"})

    def create_company(self, name):
        return self.env["res.company"].create({"name": name})

    def test_partner(self):
        self.partner.property_ids.invalidate_cache()
        self.assertTrue(self.partner.property_ids)
