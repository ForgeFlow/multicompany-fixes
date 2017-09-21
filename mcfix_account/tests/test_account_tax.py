# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.tests.account_test_users import AccountTestUsers


class TestAccountInvoiceMC(AccountTestUsers):

    def setUp(self):
        super(TestAccountInvoiceMC, self).setUp()

    def test_name_get(self):
        """ Test that in multi-company the taxes get the correct name """
        pass

    def test_change_company_in_tax_for_invoices(self):
        """ Test impact of changing company in a tax used in invoice"""
        pass

    def test_change_company_in_tax_for_moves(self):
        """ Test impact of changing company in an account move line with
        taxes """
        pass

    def test_change_company_in_tax_for_child_tax(self):
        """ Test impact of changing company in an tax that has child taxes """
        pass

    def test_change_company_in_tax_for_fiscal_position(self):
        """ Test impact of changing company on a tax that is assigned to
        fiscal position """
        pass
