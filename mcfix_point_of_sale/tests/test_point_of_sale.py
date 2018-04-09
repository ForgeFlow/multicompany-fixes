# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging
from odoo.exceptions import ValidationError
from odoo import fields
from odoo.tools import mute_logger
from odoo.addons.mcfix_account.tests.test_account_chart_template_consistency \
    import TestAccountChartTemplate

_logger = logging.getLogger(__name__)


class TestPointOfSale(TestAccountChartTemplate):

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def setUp(self):
        super(TestPointOfSale, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        pos_manager_group = self.env.ref('point_of_sale.group_pos_manager')
        self.pos_model = self.env['pos.order']
        self.journal_model = self.env['account.journal']

        manager_pos_test_group = self.create_full_access(
            ['pos.order', 'pos.order.line', 'product.pricelist',
             'product.pricelist.item', 'account.journal', 'account.move',
             'account.move.line', 'account.reconcile.model',
             'account.payment', 'account.asset.category'])
        self.env.user.company_id = self.company
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   pos_manager_group.id,
                                   multi_company_group.id,
                                   manager_pos_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.pricelist = self.env['product.pricelist'].sudo(self.user).create({
            'name': 'Pricelist Test',
            'currency_id': self.env.ref('base.EUR').id,
            'company_id': self.company.id,
        })

        self.sale_journal = self.journal_model.sudo(self.user).create({
            'name': 'Sale Journal 1 - Test',
            'code': 'test_sale_1',
            'type': 'sale',
            'company_id': self.company.id,
        })

        self.pos_config = self.env['pos.config'].create({
            'name': 'Config Test',
            'company_id': self.company.id,
            'journal_id': self.sale_journal.id,
            'journal_ids': [(0, 0, {'name': 'Cash Journal - Test',
                                    'code': 'TSC',
                                    'type': 'cash',
                                    'company_id': self.company.id,
                                    'journal_user': True})],
        })

        self.income_account = self.env['account.account'].create({
            'company_id': self.company.id,
            'code': 'INC1',
            'name': 'Income',
            'user_type_id': self.env.ref(
                'account.data_account_type_revenue').id
        })

        self.fruits_vegetables = self.env.ref(
            'point_of_sale.fruits_vegetables')
        self.carotte = self.env.ref('point_of_sale.carotte')
        self.courgette = self.env.ref('point_of_sale.courgette')
        self.onions = self.env.ref('point_of_sale.Onions')

        self.carotte.categ_id.with_context(
            force_company=self.company.id
        ).property_account_income_categ_id = self.env[
            'account.account'].create({
                'company_id': self.company.id,
                'code': 'INCOME',
                'name': 'Income',
                'user_type_id': self.env.ref(
                    'account.data_account_type_revenue').id
            })

    def create_full_access(self, list_of_models):
        manager_pos_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_pos_test'
        })
        for model in list_of_models:
            model_id = self.env['ir.model'].sudo().search(
                [('model', '=', model)])
            if model_id:
                access = self.env['ir.model.access'].sudo().create({
                    'name': 'full_access_%s' % model.replace(".", "_"),
                    'model_id': model_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                })
                access.group_id = manager_pos_test_group
        return manager_pos_test_group

    def create_company(self, name, parent_id=False):
        dict_company = {
            'name': name,
            'parent_id': parent_id,
        }
        return dict_company

    def test_pos_config_create(self):
        pos_config = self.env['pos.config'].sudo(self.user).create({
            'name': 'Config Test',
            'company_id': self.company.id,
        })
        self.assertEquals(pos_config.sequence_id.company_id,
                          pos_config.company_id)
        self.assertEquals(pos_config.sequence_line_id.company_id,
                          pos_config.company_id)

    def test_pos_config_onchange(self):
        pos_config = self.env['pos.config'].sudo(self.user).new({
            'name': 'Config Test',
            'company_id': self.company.id,
            'journal_id': self.sale_journal.id,
            'journal_ids': [(0, 0, {'name': 'Cash Journal - Test',
                                    'code': 'TSC',
                                    'type': 'cash',
                                    'company_id': self.company.id,
                                    'journal_user': True})],
        })

        pos_config.company_id = self.company_2
        pos_config._onchange_company_id()
        self.assertNotEquals(pos_config.journal_id, self.sale_journal)
        for journal in pos_config.journal_ids:
            self.assertNotEquals(journal.company_id, self.company)

    def test_constrains(self):
        pos_session = self.env['pos.session'].sudo(self.user).create({
            'user_id': self.user.id,
            'config_id': self.pos_config.id,
        })
        pos_1 = self.pos_model.sudo(self.user).create({
            'name': 'Pos - Test',
            'pricelist_id': self.pricelist.id,
            'company_id': self.company.id,
            'session_id': pos_session.id,
        })
        with self.assertRaises(ValidationError):
            pos_1.company_id = self.company_2

    def test_create_from_ui(self):
        """
        Simulation of sales coming from the interface,
        even after closing the session
        """
        fromproduct = object()

        def compute_tax(product, price, taxes=fromproduct, qty=1):
            if taxes is fromproduct:
                taxes = product.taxes_id
            currency = self.pos_config.pricelist_id.currency_id
            taxes = taxes.compute_all(price, currency, qty,
                                      product=product)['taxes']
            untax = price * qty
            return untax, sum(tax.get('amount', 0.0) for tax in taxes)

        # I click on create a new session button
        self.pos_config.open_session_cb()

        current_session = self.pos_config.current_session_id
        num_starting_orders = len(current_session.order_ids)

        untax, atax = compute_tax(self.carotte, 0.9)
        carrot_order = {
            'data':
                {'amount_paid': untax + atax,
                 'amount_return': 0,
                 'amount_tax': atax,
                 'amount_total': untax + atax,
                 'creation_date': fields.Datetime.now(),
                 'fiscal_position_id': False,
                 'pricelist_id': self.pos_config.available_pricelist_ids[0].id,
                 'lines': [
                     [0, 0,
                      {'discount': 0,
                       'id': 42,
                       'pack_lot_ids': [],
                       'price_unit': 0.9,
                       'product_id': self.carotte.id,
                       'qty': 1,
                       'tax_ids': [(6, 0, self.carotte.taxes_id.ids)]}
                      ]
                 ],
                 'name': 'Order 00042-003-0014',
                 'partner_id': False,
                 'pos_session_id': current_session.id,
                 'sequence_number': 2,
                 'statement_ids': [
                     [0, 0,
                      {'account_id':
                       self.env.user.partner_id.with_context(
                           force_company=self.company.id
                       ).property_account_receivable_id.id,
                       'amount': untax + atax,
                       'journal_id': self.pos_config.journal_ids[0].id,
                       'name': fields.Datetime.now(),
                       'statement_id': current_session.statement_ids[0].id}]],
                 'uid': '00042-003-0014',
                 'user_id': self.env.uid
                 },
            'id': '00042-003-0014',
            'to_invoice': False}

        untax, atax = compute_tax(self.courgette, 1.2)
        zucchini_order = {
            'data':
                {'amount_paid': untax + atax,
                 'amount_return': 0,
                 'amount_tax': atax,
                 'amount_total': untax + atax,
                 'creation_date': fields.Datetime.now(),
                 'fiscal_position_id': False,
                 'pricelist_id': self.pos_config.available_pricelist_ids[0].id,
                 'lines': [
                     [0, 0,
                      {'discount': 0,
                       'id': 3,
                       'pack_lot_ids': [],
                       'price_unit': 1.2,
                       'product_id': self.courgette.id,
                       'qty': 1,
                       'tax_ids': [(6, 0, self.courgette.taxes_id.ids)]}]],
                 'name': 'Order 00043-003-0014',
                 'partner_id': False,
                 'pos_session_id': current_session.id,
                 'sequence_number': self.pos_config.journal_id.id,
                 'statement_ids': [
                     [0, 0,
                      {'account_id':
                       self.env.user.partner_id.with_context(
                           force_company=self.company.id
                       ).property_account_receivable_id.id,
                       'amount': untax + atax,
                       'journal_id': self.pos_config.journal_ids[0].id,
                       'name': fields.Datetime.now(),
                       'statement_id': current_session.statement_ids[0].id
                       }
                      ]
                 ],
                 'uid': '00043-003-0014',
                 'user_id': self.env.uid},
            'id': '00043-003-0014',
            'to_invoice': False}

        untax, atax = compute_tax(self.onions, 1.28)
        self.onions_order = {
            'data': {'amount_paid': untax + atax,
                     'amount_return': 0,
                     'amount_tax': atax,
                     'amount_total': untax + atax,
                     'creation_date': fields.Datetime.now(),
                     'fiscal_position_id': False,
                     'pricelist_id': self.pos_config.available_pricelist_ids[
                         0].id,
                     'lines': [
                         [0, 0,
                          {'discount': 0,
                           'id': 3,
                           'pack_lot_ids': [],
                           'price_unit': 1.28,
                           'product_id': self.onions.id,
                           'qty': 1,
                           'tax_ids': [[6, False,
                                        self.onions.taxes_id.ids]]
                           }
                          ]
                     ],
                     'name': 'Order 00044-003-0014',
                     'partner_id': False,
                     'pos_session_id': current_session.id,
                     'sequence_number': self.pos_config.journal_id.id,
                     'statement_ids': [
                         [0, 0,
                          {'account_id':
                           self.env.user.partner_id.with_context(
                               force_company=self.company.id
                           ).property_account_receivable_id.id,
                           'amount': untax + atax,
                           'journal_id': self.pos_config.journal_ids[0].id,
                           'name': fields.Datetime.now(),
                           'statement_id': current_session.statement_ids[0].id
                           }
                          ]
                     ],
                     'uid': '00044-003-0014',
                     'user_id': self.env.uid
                     },
            'id': '00044-003-0014',
            'to_invoice': False}

        # I create an order on an open session
        self.pos_model.create_from_ui([carrot_order])
        self.assertEqual(num_starting_orders + 1, len(
            current_session.order_ids), "Submitted order not encoded")

        # I resubmit the same order
        self.pos_model.create_from_ui([carrot_order])
        self.assertEqual(num_starting_orders + 1, len(
            current_session.order_ids), "Resubmitted order was not skipped")

        # I close the session
        current_session.action_pos_session_closing_control()
        self.assertEqual(current_session.state, 'closed',
                         "Session was not properly closed")
        self.assertFalse(self.pos_config.current_session_id,
                         "Current session not properly recomputed")

        # I keep selling after the session is closed
        with mute_logger('odoo.addons.point_of_sale.models.pos_order'):
            self.pos_model.create_from_ui([zucchini_order, self.onions_order])
        rescue_session = self.env['pos.session'].search([
            ('config_id', '=', self.pos_config.id),
            ('state', '=', 'opened'),
            ('rescue', '=', True)
        ])
        self.assertEqual(
            len(rescue_session), 1,
            "One (and only one) rescue session should "
            "be created for orphan orders")
        self.assertIn("(RESCUE FOR %s)" % current_session.name,
                      rescue_session.name,
                      "Rescue session is not linked to the previous one")
        self.assertEqual(len(rescue_session.order_ids), 2,
                         "Rescue session does not contain both orders")

        # I close the rescue session
        rescue_session.action_pos_session_closing_control()
        self.assertEqual(rescue_session.state, 'closed',
                         "Rescue session was not properly closed")
