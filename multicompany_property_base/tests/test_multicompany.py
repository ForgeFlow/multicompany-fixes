# Copyright 2017 Creu Blanca
# Copyright 2017 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestMulticompanyProperty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_1 = cls.create_company("company 1")
        cls.company_2 = cls.create_company("company 2")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "company_id": False}
        )
        cls.child = cls.env["res.partner"].create(
            {"name": "Child", "parent_id": cls.partner.id}
        )
        if "account.payment.term" in cls.env:  # needs account installed
            cls.payment_term_1 = cls.env["account.payment.term"].create(
                {"name": "PT 1"}
            )
            cls.payment_term_2 = cls.env["account.payment.term"].create(
                {"name": "PT 2"}
            )

    @classmethod
    def create_company(cls, name):
        return cls.env["res.company"].create({"name": name})

    def test_partner(self):
        self.partner.property_ids.invalidate_cache()
        self.assertTrue(self.partner.property_ids)
