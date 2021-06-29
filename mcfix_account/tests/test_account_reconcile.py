# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAccountReconcile(TransactionCase):
    def setUp(self):
        super(TestAccountReconcile, self).setUp()
        employees_group = self.env.ref("base.group_user")
        multi_company_group = self.env.ref("base.group_multi_company")
        account_user_group = self.env.ref("account.group_account_user")
        account_manager_group = self.env.ref("account.group_account_manager")
        self.account_model = self.env["account.account"]
        self.reconcile_model = self.env["account.reconcile.model"]
        manager_account_test_group = self.create_full_access(
            ["account.reconcile.model"]
        )
        self.company = self.env["res.company"].create({"name": "Test company"})
        self.company_2 = self.env["res.company"].create(
            {"name": "Test company 2", "parent_id": self.company.id}
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
                                account_user_group.id,
                                multi_company_group.id,
                                account_manager_group.id,
                                manager_account_test_group.id,
                            ],
                        )
                    ],
                    "company_id": self.company.id,
                    "company_ids": [(4, self.company.id), (4, self.company_2.id)],
                }
            )
        )

        self.user_type = self.env.ref("account.data_account_type_liquidity")

        self.account = self.account_model.with_user(self.user).create(
            {
                "name": "Account - Test",
                "code": "test_cash",
                "user_type_id": self.user_type.id,
                "company_id": self.company.id,
            }
        )

    def create_full_access(self, list_of_models):
        manager_account_test_group = (
            self.env["res.groups"].sudo().create({"name": "group_manager_product_test"})
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
                access.group_id = manager_account_test_group
        return manager_account_test_group

    def test_onchanges(self):
        self.reconcile = self.reconcile_model.with_user(self.user).new(
            {
                "name": "Reconcile - Test",
                "company_id": self.company_2.id,
                "account_id": self.account.id,
            }
        )
        self.reconcile._onchange_company_id()
        self.assertFalse(self.reconcile.account_id)

    def test_constrains(self):
        self.reconcile = self.reconcile_model.with_user(self.user).create(
            {
                "name": "Reconcile - Test",
                "company_id": self.company.id,
                "account_id": self.account.id,
            }
        )
        with self.assertRaises(UserError):
            self.reconcile.company_id = self.company_2
