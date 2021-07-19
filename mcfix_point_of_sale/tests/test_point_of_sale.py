# Copyright 2018 Creu Blanca
# Copyright 2018 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency import (
    TestAccountChartTemplate,
)

_logger = logging.getLogger(__name__)


class TestPointOfSale(TestAccountChartTemplate):
    @classmethod
    def with_context(cls, *args, **kwargs):
        context = dict(args[0] if args else cls.env.context, **kwargs)
        cls.env = cls.env(context=context)
        return cls

    @classmethod
    def setUpClass(cls):
        super(TestPointOfSale, cls).setUpClass()
        employees_group = cls.env.ref("base.group_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        pos_manager_group = cls.env.ref("point_of_sale.group_pos_manager")
        cls.pos_model = cls.env["pos.order"]
        cls.journal_model = cls.env["account.journal"]

        manager_pos_test_group = cls.create_full_access(
            [
                "pos.order",
                "pos.order.line",
                "product.pricelist",
                "product.pricelist.item",
                "account.journal",
                "account.move",
                "account.move.line",
                "account.reconcile.model",
                "account.payment",
                "account.asset.category",
            ]
        )
        cls.env.user.company_id = cls.company
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
                                pos_manager_group.id,
                                multi_company_group.id,
                                manager_pos_test_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )

        cls.pricelist = (
            cls.env["product.pricelist"]
            .with_user(cls.user)
            .create(
                {
                    "name": "Pricelist Test",
                    "currency_id": cls.env.ref("base.EUR").id,
                    "company_id": cls.company.id,
                }
            )
        )

        cls.sale_journal = cls.journal_model.with_user(cls.user).create(
            {
                "name": "Sale Journal 1 - Test",
                "code": "test_sale_1",
                "type": "sale",
                "company_id": cls.company.id,
            }
        )
        vals = (
            cls.env["pos.config"]
            .with_context(company_id=cls.company.id)
            .default_get(
                [
                    "journal_id",
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                ]
            )
        )
        vals["name"] = "Config Test"
        vals["company_id"] = cls.company.id
        cls.pos_config = cls.env["pos.config"].create(vals)
        cls.income_account = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "INC1",
                "name": "Income",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            }
        )

        cls.led_lamp = cls.env.ref("point_of_sale.led_lamp")
        cls.whiteboard_pen = cls.env.ref("point_of_sale.whiteboard_pen")
        cls.newspaper_rack = cls.env.ref("point_of_sale.newspaper_rack")

        cls.newspaper_rack.categ_id.with_context(
            force_company=cls.company.id
        ).property_account_income_categ_id = cls.env["account.account"].create(
            {
                "company_id": cls.company.id,
                "code": "INCOME",
                "name": "Income",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            }
        )

        cls.cash_payment_method = cls.pos_config.payment_method_ids.filtered(
            lambda pm: pm.name == "Cash"
        )
        cls.bank_payment_method = cls.pos_config.payment_method_ids.filtered(
            lambda pm: pm.name == "Bank"
        )
        account = cls.company.account_default_pos_receivable_account_id
        cls.credit_payment_method = cls.env["pos.payment.method"].create(
            {
                "name": "Credit",
                "receivable_account_id": account.id,
                "split_transactions": True,
            }
        )
        cls.pos_config.payment_method_ids |= cls.credit_payment_method

    @classmethod
    def create_product(cls, name):
        return cls.env["product.product"].create({"name": name, "type": "consu"})

    @classmethod
    def create_full_access(cls, list_of_models):
        manager_pos_test_group = (
            cls.env["res.groups"].sudo().create({"name": "group_manager_pos_test"})
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
                access.group_id = manager_pos_test_group
        return manager_pos_test_group

    @classmethod
    def create_company(cls, name, parent_id=False):
        dict_company = {
            "name": name,
            "parent_id": parent_id,
        }
        return dict_company

    def test_pos_config_create(self):
        vals = (
            self.env["pos.config"]
            .with_context(company_id=self.company.id)
            .default_get(
                [
                    "journal_id",
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                ]
            )
        )
        vals["name"] = "Config Test"
        vals["company_id"] = self.company.id
        pos_config = self.env["pos.config"].with_user(self.user).create(vals)
        self.assertEquals(pos_config.sequence_id.company_id, pos_config.company_id)
        self.assertEquals(pos_config.sequence_line_id.company_id, pos_config.company_id)

    def test_pos_config_onchange(self):
        vals = (
            self.env["pos.config"]
            .with_context(company_id=self.company.id)
            .default_get(
                [
                    "journal_id",
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                ]
            )
        )
        vals["name"] = "Config Test"
        vals["company_id"] = self.company.id
        vals["journal_id"] = self.sale_journal.id
        pos_config = self.env["pos.config"].with_user(self.user).new(vals)
        pos_config.company_id = self.company_2
        pos_config._onchange_company_id()
        self.assertNotEquals(pos_config.journal_id, self.sale_journal)
        self.assertNotEquals(pos_config.journal_id.company_id, self.company)

    def test_constrains(self):
        pos_session = (
            self.env["pos.session"]
            .with_user(self.user)
            .create({"user_id": self.user.id, "config_id": self.pos_config.id})
        )
        pos_1 = self.pos_model.with_user(self.user).create(
            {
                "name": "Pos - Test",
                "pricelist_id": self.pricelist.id,
                "company_id": self.company.id,
                "session_id": pos_session.id,
                "amount_tax": 0,
                "amount_total": 0,
                "amount_paid": 0,
                "amount_return": 0,
            }
        )
        with self.assertRaises(UserError):
            pos_1.company_id = self.company_2
            pass

    def test_pos_session_create(self):
        company_3 = self.env["res.company"].create({"name": "C3"})
        self._chart_of_accounts_create(company_3, self.chart, self._get_templates())
        self.env["account.journal"].create(
            {
                "name": "Cash Journal - c3",
                "code": "CJ3",
                "type": "cash",
                "company_id": company_3.id,
            }
        )
        sale_journal = self.env["account.journal"].create(
            {
                "name": "Sale Journal - c3",
                "code": "SJ3",
                "type": "sale",
                "company_id": company_3.id,
            }
        )
        vals = (
            self.env["pos.config"]
            .with_context(company_id=company_3.id)
            .default_get(
                [
                    "journal_id",
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                ]
            )
        )
        vals["name"] = "Config Test"
        vals["journal_id"] = sale_journal.id
        vals["company_id"] = company_3.id
        account = company_3.account_default_pos_receivable_account_id
        vals["payment_method_ids"] = [
            (
                0,
                0,
                {
                    "name": "payment method",
                    "receivable_account_id": account.id,
                    "company_id": company_3.id,
                },
            )
        ]
        pos_config = self.env["pos.config"].create(vals)
        # I click on create a new session button
        pos_config.open_session_cb()
        self.assertEquals(len(pos_config.journal_id), 1)
        with self.assertRaises(UserError):
            pos_config.company_id = self.company_2

    def test_create_from_ui(self):
        """
        Simulation of sales coming from the interface,
        even after closing the session
        """

        def compute_tax(product, price, qty=1, taxes=None):
            if not taxes:
                taxes = product.taxes_id.filtered(
                    lambda t: t.company_id.id == self.env.company.id
                )
            currency = self.pos_config.pricelist_id.currency_id
            res = taxes.compute_all(price, currency, qty, product=product)
            untax = res["total_excluded"]
            return untax, sum(tax.get("amount", 0.0) for tax in res["taxes"])

        # I click on create a new session button
        self.pos_config.open_session_cb()

        current_session = self.pos_config.current_session_id
        num_starting_orders = len(current_session.order_ids)

        untax, atax = compute_tax(self.led_lamp, 0.9)
        carrot_order = {
            "data": {
                "amount_paid": untax + atax,
                "amount_return": 0,
                "amount_tax": atax,
                "amount_total": untax + atax,
                "creation_date": fields.Datetime.to_string(fields.Datetime.now()),
                "fiscal_position_id": False,
                "pricelist_id": self.pos_config.available_pricelist_ids[0].id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "discount": 0,
                            "id": 42,
                            "pack_lot_ids": [],
                            "price_unit": 0.9,
                            "product_id": self.led_lamp.id,
                            "price_subtotal": 0.9,
                            "price_subtotal_incl": 1.04,
                            "qty": 1,
                            "tax_ids": [
                                (
                                    6,
                                    0,
                                    self.led_lamp.taxes_id.filtered(
                                        lambda r: r.company_id
                                        == self.pos_config.company_id
                                    ).ids,
                                )
                            ],
                        },
                    ]
                ],
                "name": "Order 00042-003-0014",
                "partner_id": False,
                "pos_session_id": current_session.id,
                "sequence_number": 2,
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "amount": untax + atax,
                            "name": fields.Datetime.now(),
                            "payment_method_id": self.cash_payment_method.id,
                        },
                    ]
                ],
                "uid": "00042-003-0014",
                "user_id": self.env.uid,
            },
            "id": "00042-003-0014",
            "to_invoice": False,
        }

        untax, atax = compute_tax(self.whiteboard_pen, 1.2)
        zucchini_order = {
            "data": {
                "amount_paid": untax + atax,
                "amount_return": 0,
                "amount_tax": atax,
                "amount_total": untax + atax,
                "creation_date": fields.Datetime.to_string(fields.Datetime.now()),
                "fiscal_position_id": False,
                "pricelist_id": self.pos_config.available_pricelist_ids[0].id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "discount": 0,
                            "id": 3,
                            "pack_lot_ids": [],
                            "price_unit": 1.2,
                            "product_id": self.whiteboard_pen.id,
                            "price_subtotal": 1.2,
                            "price_subtotal_incl": 1.38,
                            "qty": 1,
                            "tax_ids": [
                                (
                                    6,
                                    0,
                                    self.whiteboard_pen.taxes_id.filtered(
                                        lambda r: r.company_id
                                        == self.pos_config.company_id
                                    ).ids,
                                )
                            ],
                        },
                    ]
                ],
                "name": "Order 00043-003-0014",
                "partner_id": False,
                "pos_session_id": current_session.id,
                "sequence_number": self.pos_config.journal_id.id,
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "amount": untax + atax,
                            "name": fields.Datetime.now(),
                            "payment_method_id": self.credit_payment_method.id,
                        },
                    ]
                ],
                "uid": "00043-003-0014",
                "user_id": self.env.uid,
            },
            "id": "00043-003-0014",
            "to_invoice": False,
        }

        untax, atax = compute_tax(self.newspaper_rack, 1.28)
        newspaper_rack_order = {
            "data": {
                "amount_paid": untax + atax,
                "amount_return": 0,
                "amount_tax": atax,
                "amount_total": untax + atax,
                "creation_date": fields.Datetime.to_string(fields.Datetime.now()),
                "fiscal_position_id": False,
                "pricelist_id": self.pos_config.available_pricelist_ids[0].id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "discount": 0,
                            "id": 3,
                            "pack_lot_ids": [],
                            "price_unit": 1.28,
                            "product_id": self.newspaper_rack.id,
                            "price_subtotal": 1.28,
                            "price_subtotal_incl": 1.47,
                            "qty": 1,
                            "tax_ids": [
                                [
                                    6,
                                    False,
                                    self.newspaper_rack.taxes_id.filtered(
                                        lambda r: r.company_id
                                        == self.pos_config.company_id
                                    ).ids,
                                ]
                            ],
                        },
                    ]
                ],
                "name": "Order 00044-003-0014",
                "partner_id": False,
                "pos_session_id": current_session.id,
                "sequence_number": self.pos_config.journal_id.id,
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "amount": untax + atax,
                            "name": fields.Datetime.now(),
                            "payment_method_id": self.bank_payment_method.id,
                        },
                    ]
                ],
                "uid": "00044-003-0014",
                "user_id": self.env.uid,
            },
            "id": "00044-003-0014",
            "to_invoice": False,
        }

        # I create an order on an open session
        self.pos_model.create_from_ui([carrot_order])
        self.assertEqual(
            num_starting_orders + 1,
            len(current_session.order_ids),
            "Submitted order not encoded",
        )

        # I close the session
        current_session.action_pos_session_closing_control()
        self.assertEqual(
            current_session.state, "closed", "Session was not properly closed"
        )
        self.assertFalse(
            self.pos_config.current_session_id,
            "Current session not properly recomputed",
        )

        # I keep selling after the session is closed
        with mute_logger("odoo.addons.point_of_sale.models.pos_order"):
            self.pos_model.create_from_ui([zucchini_order, newspaper_rack_order])
        rescue_session = self.env["pos.session"].search(
            [
                ("config_id", "=", self.pos_config.id),
                ("state", "=", "opened"),
                ("rescue", "=", True),
            ]
        )
        self.assertEqual(
            len(rescue_session),
            1,
            "One (and only one) rescue session should " "be created for orphan orders",
        )
        self.assertIn(
            "(RESCUE FOR %s)" % current_session.name,
            rescue_session.name,
            "Rescue session is not linked to the previous one",
        )
        self.assertEqual(
            len(rescue_session.order_ids),
            2,
            "Rescue session does not contain both orders",
        )

        # I close the rescue session
        rescue_session.action_pos_session_closing_control()
        self.assertEqual(
            rescue_session.state, "closed", "Rescue session was not properly closed"
        )
