# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestAccountAccount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        employees_group = cls.env.ref("base.group_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        account_user_group = cls.env.ref("account.group_account_user")
        account_manager_group = cls.env.ref("account.group_account_manager")
        cls.account_model = cls.env["account.account"]
        cls.tax_model = cls.env["account.tax"]
        manager_account_test_group = cls.create_full_access(["account.account"])
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
                        (
                            6,
                            0,
                            [
                                employees_group.id,
                                account_user_group.id,
                                account_manager_group.id,
                                multi_company_group.id,
                                manager_account_test_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )

        cls.user_type = cls.env.ref("account.data_account_type_liquidity")

        cls.account = cls.account_model.with_user(cls.user).create(
            {
                "name": "Account - Test",
                "code": "test_cash",
                "user_type_id": cls.user_type.id,
                "company_id": cls.company.id,
            }
        )

        cls.tax = cls.tax_model.with_user(cls.user).create(
            {
                "name": "Tax - Test",
                "amount": 0.0,
                "company_id": cls.company.id,
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account.id,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "tax",
                            "account_id": cls.account.id,
                        },
                    ),
                ],
            }
        )

    @classmethod
    def create_full_access(cls, list_of_models):
        manager_account_test_group = (
            cls.env["res.groups"].sudo().create({"name": "group_manager_product_test"})
        )
        for model in list_of_models:
            model_id = cls.env["ir.model"].sudo().search([("model", "=", model)])
            if model_id:
                access = (
                    cls.env["ir.model.access"]
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
        self.account.tax_ids |= self.tax
        self.assertIn(self.tax, self.account.tax_ids)
        with self.assertRaises(ValidationError):
            self.account.company_id = self.company_2
            self.assertNotIn(self.tax, self.account.tax_ids)

    def test_constrains(self):
        tax_2 = self.tax_model.with_user(self.user).create(
            {"name": "Tax - Test", "amount": 0.0, "company_id": self.company_2.id}
        )
        with self.assertRaises(ValidationError):
            self.account.company_id = self.company_2
        self.account.company_id = self.company
        with self.assertRaises(UserError):
            tax_2.write(
                {
                    "invoice_repartition_line_ids": [
                        (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                        (
                            0,
                            0,
                            {
                                "factor_percent": 100,
                                "repartition_type": "tax",
                                "account_id": self.account.id,
                            },
                        ),
                    ],
                    "refund_repartition_line_ids": [
                        (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                        (
                            0,
                            0,
                            {
                                "factor_percent": 100,
                                "repartition_type": "tax",
                                "account_id": self.account.id,
                            },
                        ),
                    ],
                }
            )
        with self.assertRaises(UserError):
            self.account.tax_ids |= tax_2
