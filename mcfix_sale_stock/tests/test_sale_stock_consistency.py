# Copyright 2016 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError

from odoo.addons.mcfix_sale.tests.test_sale_order_consistency import (
    TestSaleOrderConsistency,
)


class TestSaleStockOrderConsistency(TestSaleOrderConsistency):
    @classmethod
    def setUpClass(cls):
        super(TestSaleStockOrderConsistency, cls).setUpClass()
        cls.sale_order_4 = cls._create_sale_order(
            cls.company_2,
            cls.product2,
            cls.tax_2,
            cls.partner_2,
            cls.team_2,
            cls.user_4,
        )

    def test_sale_stock_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.company.id)], limit=1
        )
        with self.assertRaises(UserError):
            self.sale_order_4.write({"warehouse_id": warehouse.id})
