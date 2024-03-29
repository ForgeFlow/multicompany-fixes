# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase

_logger = logging.getLogger(__name__)


class TestStockLocation(TransactionCase):
    def setUp(self):
        super(TestStockLocation, self).setUp()
        employees_group = self.env.ref("base.group_user")
        multi_company_group = self.env.ref("base.group_multi_company")
        stock_user_group = self.env.ref("stock.group_stock_user")
        stock_manager_group = self.env.ref("stock.group_stock_manager")
        self.move_model = self.env["stock.move"]
        self.location_model = self.env["stock.location"]
        manager_stock_test_group = self.create_full_access(
            ["stock.move", "stock.location"]
        )
        self.company = (
            self.env["res.company"]
            .with_context(bypass_company_validation=True)
            .create({"name": "Test company"})
        )
        self.company_2 = (
            self.env["res.company"]
            .with_context(bypass_company_validation=True)
            .create({"name": "Test company 2", "parent_id": self.company.id})
        )
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = (
            self.env["res.users"]
            .with_user(self.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                employees_group.id,
                                stock_user_group.id,
                                stock_manager_group.id,
                                multi_company_group.id,
                                manager_stock_test_group.id,
                            ],
                        )
                    ],
                    "company_id": self.company.id,
                    "company_ids": [(4, self.company.id), (4, self.company_2.id)],
                }
            )
        )

        self.location_1 = (
            self.env["stock.location"]
            .with_user(self.user)
            .create({"name": "test location 1", "company_id": self.company.id})
        )
        self.location_2 = (
            self.env["stock.location"]
            .with_user(self.user)
            .create(
                {
                    "name": "test location 2",
                    "location_id": self.location_1.id,
                    "company_id": self.company.id,
                }
            )
        )
        self.location_3 = (
            self.env["stock.location"]
            .with_user(self.user)
            .create({"name": "test location 3", "company_id": self.company_2.id})
        )

    def create_full_access(self, list_of_models):
        manager_stock_test_group = (
            self.env["res.groups"].sudo().create({"name": "group_manager_stock_test"})
        )
        for model in list_of_models:
            model_id = self.env["ir.model"].sudo().search([("model", "=", model)])
            if model_id:
                access = (
                    self.env["ir.model.access"]
                    .sudo()
                    .create(
                        {
                            "name": "full_access_%s" % model.replace(".", "_"),
                            "model_id": model_id.id,
                            "perm_read": True,
                            "perm_write": True,
                            "perm_create": True,
                            "perm_unlink": True,
                        }
                    )
                )
                access.group_id = manager_stock_test_group
        return manager_stock_test_group

    def test_onchanges(self):
        with self.assertRaises(UserError):
            with Form(self.location_1) as location_form:
                location_form.company_id = self.company_2
        self.assertFalse(self.location_1.location_id)

    def test_constrains(self):
        with self.assertRaises(UserError):
            self.location_1.company_id = self.company_2
        with self.assertRaises(UserError):
            self.location_2.location_id = self.location_3

    def test_company_sublocation(self):
        with self.assertRaises(UserError):
            self.location_4 = (
                self.env["stock.location"]
                .with_user(self.user)
                .create(
                    {
                        "name": "test location 4",
                        "location_id": self.location_3.id,
                        "company_id": self.company.id,
                    }
                )
            )
