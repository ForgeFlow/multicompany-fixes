# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo.exceptions import ValidationError


class TestSaleOrderMC(TestSale):

    def setUp(self):
        super(TestSaleOrderMC, self).setUp()
        self.res_users_model = self.env['res.users']
        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })

        # Multi-company access rights
        group_user = self.env.ref('sales_team.group_sale_salesman')
        group_mc = self.env.ref('base.group_multi_company')
        self.manager.write({
            'groups_id': [(4, group_mc.id)]
        })
        self.user.write({
            'groups_id': [(4, group_mc.id)],
            'company_ids': [(4, self.company_2.id)]
        })
        self.user_2 = self.env['res.users'].create({
            'name': 'Daisy User',
            'login': 'user_2',
            'email': 'd.u@example.com',
            'signature': '--\nDaisy',
            'notify_email': 'always',
            'groups_id': [(6, 0, [group_user.id, group_mc.id])],
        })
        self.user_2.write({
            'company_ids': [(4, self.company_2.id)],
        })

        # Create records for both companies
        self.partner_1 = self._create_partner(self.company)
        self.partner_2 = self._create_partner(self.company_2)

        self.crm_team_model = self.env['crm.team']
        self.team_1 = self._create_crm_team(self.user.id, self.company)
        self.team_2 = self._create_crm_team(self.user_2.id, self.company_2)

        self.pricelist_1 = self._create_pricelist(self.company)
        self.pricelist_2 = self._create_pricelist(self.company_2)

        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_fiscal_position(self.company)
        self.fiscal_position_2 = self._create_fiscal_position(self.company_2)

        self.payment_terms_1 = self._create_payment_terms(self.company)
        self.payment_terms_2 = self._create_payment_terms(self.company_2)

        self.sale_order_1 = self._create_sale_order(self.company, self.team_1)
        self.sale_order_2 = self._create_sale_order(self.company_2,
                                                    self.team_2)

    def _create_partner(self, company):
        "Create a Partner"
        partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'company_id': company.id,
            'customer': True,
        })
        return partner

    def _create_crm_team(self, uid, company):
        """Create a crm team."""
        crm_team = self.crm_team_model.create({'name': 'CRM team',
                                          'company_id': company.id})
        return crm_team

    def _create_pricelist(self, company):
        pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'company_id': company.id,
        })
        return pricelist

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

    def _create_sale_order(self, company, team):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'company_id': company.id,
            'team_id': team.id,
#            'user_id': user.id,
        })
        return sale

    def test_sale_order_security(self):
        """ Test Security of Company Sale Order"""
        # User in company 1
        self.user.write({'company_id': self.company.id})
        so_ids = self.env['sale.order'].sudo(self.user).search([
            ('company_id', '=', self.company_2.id)
        ])
        self.assertEqual(so_ids, self.env['sale.order'],
                         "A user in company %s shouldn't be able "
                         "to see %s sales orders" % (self.user.company_id.name,
                                                     self.company_2.name))

    def test_sale_order_company_consistency(self):
        # Assertion on the constraints to ensure the consistency
        # on company dependent fields
        with self.assertRaises(ValidationError):
            self.sale_order_1.\
                write({'partner_id': self.partner_2.id})
#        with self.assertRaises(ValidationError):
#            self.sale_order_1.\
#                write({'payment_term_id': self.payment_term_2.id})
#        with self.assertRaises(ValidationError):
#            self.cash_journal.\
#                write({'company_id': self.company_2.id})
#        with self.assertRaises(ValidationError):
#            self.account_invoice.\
#                write({'journal_id': self.cash_journal.id})
