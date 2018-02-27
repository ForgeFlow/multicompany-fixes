# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.mcfix_sale.tests.test_sale_order_consistency \
    import TestSaleOrderConsistency
from odoo.exceptions import ValidationError


class TestSaleStockOrderConsistency(TestSaleOrderConsistency):

    def setUp(self):
        super(TestSaleStockOrderConsistency, self).setUp()
        self.sale_order_4 = self._create_sale_order(
            self.company_2,
            self.product2,
            self.tax_2,
            self.partner_2,
            self.team_2,
            self.user_4
        )

    def test_sale_stock_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company.id)], limit=1)
        with self.assertRaises(ValidationError):
            self.sale_order_4.write({'warehouse_id': warehouse.id})
