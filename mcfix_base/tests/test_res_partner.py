# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestResPartner(SavepointCase):
    @classmethod
    def with_context(cls, *args, **kwargs):
        context = dict(args[0] if args else cls.env.context, **kwargs)
        cls.env = cls.env(context=context)
        return cls

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employees_group = cls.env.ref("base.group_user")
        cls.partner_manager_group = cls.env.ref("base.group_partner_manager")
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Test company 2", "parent_id": cls.company.id}
        )
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
                        (6, 0, [cls.employees_group.id, cls.partner_manager_group.id])
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )

    def test_constrains(self):
        """Check contrains methods"""

        partner_1 = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {"name": "Test 1", "company_id": self.company.id, "is_company": True}
            )
        )
        partner_2 = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test 2",
                    "company_id": self.company_2.id,
                    "is_company": False,
                }
            )
        )
        partner_3 = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test 3",
                    "company_id": self.company_2.id,
                    "is_company": False,
                }
            )
        )
        with self.assertRaises(UserError):
            partner_1.child_ids = [(4, partner_2.id)]
        with self.assertRaises(UserError):
            partner_2.parent_id = partner_1
        partner_2.parent_id = False
        partner_1.company_id = self.company_2
        partner_2.parent_id = partner_1
        partner_3.parent_id = partner_2
        partner_2.parent_id = False
        self.assertEqual(partner_3.commercial_partner_id, partner_2)

    def test_user_partner_company(self):
        self.assertFalse(self.user.partner_id.company_id)
        self.user.company_id = self.company_2
        self.assertFalse(self.user.partner_id.company_id)
