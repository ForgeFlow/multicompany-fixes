# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase

_logger = logging.getLogger(__name__)


class TestProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        employees_group = cls.env.ref("base.group_user")
        manager_product_test_group = cls.create_full_access(
            [
                "product.pricelist",
                "product.pricelist.item",
                "product.supplierinfo",
                "product.template",
                "product.product",
                "ir.property",
                "res.partner",
            ]
        )
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
                        (6, 0, [employees_group.id, manager_product_test_group.id])
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id), (4, cls.company_2.id)],
                }
            )
        )
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dunit = cls.env["uom.uom"].create(
            {
                "name": "DeciUnit",
                "category_id": cls.uom_unit.category_id.id,
                "factor_inv": 0.1,
                "factor": 10.0,
                "uom_type": "smaller",
                "rounding": 0.001,
            }
        )

    @classmethod
    def create_full_access(cls, list_of_models):
        manager_product_test_group = (
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
                access.group_id = manager_product_test_group
        return manager_product_test_group

    def test_template(self):
        template_1 = (
            self.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "Test",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_unit.id,
                    "company_id": self.company_2.id,
                }
            )
        )
        self.assertEqual(template_1.product_variant_id.company_id, self.company_2)
        template_1.company_id = self.company
        self.assertEqual(template_1.product_variant_id.company_id, self.company)
        product_1 = (
            self.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Test 1",
                    "type": "consu",
                    "uom_id": self.uom_dunit.id,
                    "uom_po_id": self.uom_dunit.id,
                    "product_tmpl_id": template_1.id,
                    "company_id": self.company.id,
                }
            )
        )
        product_1.company_id = self.company_2
        self.assertEqual(template_1.company_id, self.company_2)
        self.assertEqual(product_1.company_id, self.company_2)
        template_1.company_id = self.company
        self.assertEqual(product_1.company_id, self.company)

    def test_product(self):
        template_1 = (
            self.env["product.template"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_unit.id,
                    "company_id": self.company.id,
                }
            )
        )
        product_1 = (
            self.env["product.product"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test 1",
                    "type": "consu",
                    "uom_id": self.uom_dunit.id,
                    "uom_po_id": self.uom_dunit.id,
                    "company_id": self.company_2.id,
                }
            )
        )
        product_1.product_tmpl_id = template_1
        self.assertEqual(product_1.company_id, self.company)

    def test_constrains_supplier_info(self):
        """Check constrains methods"""

        template_1 = (
            self.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "Test Product",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_unit.id,
                    "company_id": False,
                }
            )
        )
        partner_1 = (
            self.env["res.partner"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test Partner",
                    "company_id": self.company.id,
                    "is_company": True,
                }
            )
        )
        supplier_1 = (
            self.env["product.supplierinfo"]
            .with_user(self.user)
            .create({"name": partner_1.id, "product_tmpl_id": template_1.id})
        )
        with self.assertRaises(UserError):
            partner_1.company_id = self.company_2
        template_1.company_id = self.company
        partner_1.company_id = self.company
        with self.assertRaises(UserError):
            supplier_1.company_id = self.company_2
        with self.assertRaises(UserError):
            template_1.company_id = self.company_2
        partner_1.company_id = False
        with self.assertRaises(UserError):
            supplier_1.sudo().company_id = self.company_2
            # The sudo is because there exists an ir_rule for access

    def test_constrains_pricelist(self):
        """Check constrains methods"""

        template_1 = (
            self.env["product.template"]
            .sudo()
            .create(
                {
                    "name": "Test Template",
                    "uom_id": self.uom_unit.id,
                    "uom_po_id": self.uom_unit.id,
                    "company_id": False,
                }
            )
        )
        pricelist_1 = (
            self.env["product.pricelist"]
            .with_user(self.user)
            .create({"name": "Test Pricelist", "company_id": self.company.id})
        )
        pricelist_item_1 = (
            self.env["product.pricelist.item"]
            .with_user(self.user)
            .create(
                {
                    "name": "Test Pricelist Item",
                    "product_tmpl_id": template_1.id,
                    "applied_on": "1_product",
                    "pricelist_id": pricelist_1.id,
                }
            )
        )
        product_1 = (
            self.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Test Product",
                    "type": "consu",
                    "uom_id": self.uom_dunit.id,
                    "uom_po_id": self.uom_dunit.id,
                    "company_id": self.company_2.id,
                }
            )
        )
        with self.assertRaises(UserError):
            template_1.company_id = self.company_2
        template_1.company_id = self.company
        with self.assertRaises(UserError):
            pricelist_item_1.company_id = self.company_2
        pricelist_item_1.sudo().company_id = self.company
        with self.assertRaises(UserError):
            pricelist_item_1.sudo().write(
                {"product_id": product_1.id, "applied_on": "0_product_variant"}
            )
