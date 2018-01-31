# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestAccountCompanyConfig(TransactionCase):
    def setUp(self):
        super(TestAccountCompanyConfig, self).setUp()
        self.company = self.browse_ref('base.main_company')

    def test_company(self):
        purchase_tax = self.env['account.tax'].search([
            ('type_tax_use', 'in', ('purchase', 'all')),
            ('company_id', '=', self.company.id),
            ('id', 'not in', self.company.default_purchase_tax_id.ids),
        ], limit=1)
        sale_tax = self.env['account.tax'].search([
            ('type_tax_use', 'in', ('purchase', 'all')),
            ('company_id', '=', self.company.id),
            ('id', 'not in', self.company.default_sale_tax_id.ids),
        ], limit=1)
        self.company.write({
            'default_purchase_tax_id': purchase_tax.id,
            'default_sale_tax_id': sale_tax.id,
        })
        self.assertEqual(self.company.default_purchase_tax_id, purchase_tax)
        self.assertEqual(self.company.default_sale_tax_id, sale_tax)
