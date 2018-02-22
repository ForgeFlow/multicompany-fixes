# © 2016-17 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency \
    import TestAccountChartTemplate
from odoo.exceptions import ValidationError


class TestPurchaseOrderConsistency(TestAccountChartTemplate):

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def setUp(self):
        super(TestPurchaseOrderConsistency, self).setUp()
        self.res_users_model = self.env['res.users']
        self.account_model = self.env['account.account']

        # User
        self.user = self.env['res.users'].create({
            'name': 'Daisy User',
            'login': 'user',
            'email': 'd.u@example.com',
            'signature': '--\nDaisy',
            'notification_type': 'email',
            'company_id': self.company_2.id,
            'company_ids': [(4, self.company_2.id)]
        })

        # Products
        self.uom_unit = self.env.ref('product.product_uom_unit')
        self.product_model = self.env['product.product']

        self.product1 = self.product_model.create({
            'name': 'Product A',
            'uom_id': self.uom_unit.id,
            'lst_price': 1000,
            'uom_po_id': self.uom_unit.id,
            'company_id': False,
        })

        self.product2 = self.product_model.create({
            'name': 'Product B',
            'uom_id': self.uom_unit.id,
            'lst_price': 3000,
            'uom_po_id': self.uom_unit.id,
            'taxes_id': False,
            'supplier_taxes_id': False,
        })

        self.product2.write({'responsible_id': self.user.id,
                             'company_id': self.company_2.id})

        # Account
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.cash_account_id = self.account_model.create({
            'name': 'Cash 1 - Test',
            'code': 'test_cash_1',
            'user_type_id': user_type.id,
            'company_id': self.company.id,
        })

        # Create records for both companies
        self.partner_1 = self._create_partners(self.company)
        self.partner_2 = self._create_partners(self.company_2)

        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_fiscal_position(self.company)
        self.fiscal_position_2 = self._create_fiscal_position(self.company_2)

        self.payment_terms_1 = self._create_payment_terms(self.company)
        self.payment_terms_2 = self._create_payment_terms(self.company_2)

        self.purchase1 = self.with_context(
            company_id=self.company.id)._create_purchase(
            self.company,
            self.product1,
            self.tax_1,
            self.partner_1
        )

        self.purchase1.button_confirm()
        self._create_invoice(self.purchase1, self.partner_1,
                             self.cash_account_id)

    def _create_purchase(self, company, product, tax, partner):
        """ Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        line_values = {
            'name': product.name,
            'product_id': product.id,
            'product_qty': 100,
            'product_uom': product.uom_id.id,
            'price_unit': 50,
            'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        }
        lines.append((0, 0, line_values))
        purchase = self.env['purchase.order'].create({
            'partner_id': partner.id,
            'order_line': lines,
            'company_id': company.id,
        })
        return purchase

    def _create_invoice(self, purchase, partner, account):
        """ Create a vendor invoice for the purchase order."""
        invoice_vals = {
            'purchase_id': purchase.id,
            'partner_id': partner.id,
            'account_id': account.id,
            'company_id': purchase.company_id.id,
            'type': 'in_invoice',
        }
        purchase_context = {
            'active_id': purchase.id,
            'active_ids': purchase.ids,
            'active_model': 'purchase.order',
            'company_id': purchase.company_id.id,
        }
        self.env['account.invoice'].with_context(purchase_context).\
            create(invoice_vals)
        return True

    def _create_partners(self, company):
        """ Create a Partner """
        partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'company_id': company.id,
            'customer': True,
        })
        return partner

    def _create_tax(self, company):
        tax = self.env['account.tax'].create({
            'name': 'Test Tax',
            'company_id': company.id,
            'amount': 3.3,
        })
        return tax

    def _create_fiscal_position(self, company):
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'Test Fiscal Position',
            'company_id': company.id,
        })
        return fiscal_position

    def _create_payment_terms(self, company):
        terms = self.env['account.payment.term'].create({
            'name': 'Test payment Terms',
            'company_id': company.id,
        })
        return terms

    def test_purchase_order_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(ValidationError):
            self.purchase1.\
                write({'partner_id': self.partner_2.id})
        with self.assertRaises(ValidationError):
            self.purchase1.\
                write({'payment_term_id': self.payment_terms_2.id})
        with self.assertRaises(ValidationError):
            self.purchase1.\
                write({'fiscal_position_id': self.fiscal_position_2.id})
        with self.assertRaises(ValidationError):
            self.purchase1.order_line.\
                write({'taxes_id': [(6, 0, [self.tax_2.id])]})
        with self.assertRaises(ValidationError):
            self.purchase1.order_line.\
                write({'product_id': self.product2.id})
