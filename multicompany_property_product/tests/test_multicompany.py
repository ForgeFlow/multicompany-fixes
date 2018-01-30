# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.multicompany_property_base.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def setUp(self):
        super().setUp()
        self.product = self.env['product.product'].create({
            'name': 'Product Product',
            'company_id': False,
        })
        self.product_template = self.env['product.template'].create({
            'name': 'Product template',
            'company_id': False,
        })
        self.category = self.env['product.category'].create({
            'name': 'Category'
        })

    def test_product(self):
        self.assertTrue(self.product.property_ids)
        self.product.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        ).write({'standard_price': 10})
        self.product.property_ids.filtered(
            lambda r: r.company_id == self.company_2
        ).write({'standard_price': 20})
        self.assertEqual(
            self.product.with_context(
                force_company=self.company_1.id).standard_price,
            self.product.property_ids.filtered(
                lambda r: r.company_id == self.company_1
            ).standard_price)
        self.assertEqual(
            self.product.with_context(
                force_company=self.company_2.id).standard_price,
            self.product.property_ids.filtered(
                lambda r: r.company_id == self.company_2
            ).standard_price)

    def test_product_template(self):
        self.assertTrue(self.product_template.property_ids)
        self.product_template.property_ids.filtered(
            lambda r: r.company_id == self.company_1).standard_price = 10
        self.product_template.property_ids.filtered(
            lambda r: r.company_id == self.company_2).standard_price = 20
        self.assertEqual(
            self.product_template.with_context(
                force_company=self.company_1.id).standard_price,
            10)
        self.assertEqual(
            self.product_template.with_context(
                force_company=self.company_2.id).standard_price,
            20)

    def test_product_category(self):
        self.assertTrue(self.category.property_ids)
