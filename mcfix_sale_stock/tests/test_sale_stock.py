# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.mcfix_sale.tests.test_sale_order import TestSaleOrderMC
from odoo.exceptions import ValidationError


class TestSaleStockOrderMC(TestSaleOrderMC):

    def setUp(self):
        super(TestSaleStockOrderMC, self).setUp()
        self.sale_order_3 = self._create_sale_order(self.company_2,
                                                    self.product2,
                                                    self.tax_2,
                                                    self.partner_2,
                                                    self.team_2,
                                                    self.user_3)

    def test_sale_stock_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', self.company.id)], limit=1)
        with self.assertRaises(ValidationError):
            self.sale_order_3.\
                write({'warehouse_id': warehouse.id})
