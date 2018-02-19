# © 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAccountChartTemplate(TransactionCase):

    def with_context(self, *args, **kwargs):
        context = dict(args[0] if args else self.env.context, **kwargs)
        self.env = self.env(context=context)
        return self

    def _get_templates(self):
        ir_model_data = self.env['ir.model.data']

        account_template_data_1 = ir_model_data.search(
            [('name', '=', 'transfer_account_id')], limit=1)
        account_template_data_2 = ir_model_data.search(
            [('name', '=', 'conf_a_recv')], limit=1)
        account_template_data_3 = ir_model_data.search(
            [('name', '=', 'conf_a_pay')], limit=1)

        account_template_1 = self.env['account.account.template'].browse(
            [account_template_data_1.res_id])
        account_template_2 = self.env['account.account.template'].browse(
            [account_template_data_2.res_id])
        account_template_3 = self.env['account.account.template'].browse(
            [account_template_data_3.res_id])

        tax_template_data_1 = ir_model_data.search(
            [('name', '=', 'sale_tax_template')], limit=1)
        tax_template_data_2 = ir_model_data.search(
            [('name', '=', 'purchase_tax_template')], limit=1)

        account_tax_template_1 = self.env['account.tax.template'].browse(
            [tax_template_data_1.res_id])
        account_tax_template_2 = self.env['account.tax.template'].browse(
            [tax_template_data_2.res_id])

        res = [account_template_1, account_template_2, account_template_3,
               account_tax_template_1, account_tax_template_2]
        return res

    def _chart_of_accounts_create(self, company, chart, templates):
        _logger.debug('Creating chart of account')

        templates[0].chart_template_id = chart
        templates[1].chart_template_id = chart
        templates[2].chart_template_id = chart

        if templates[3].company_id:
            templates[3].company_id = False
        if templates[4].company_id:
            templates[4].company_id = False

        chart.tax_template_ids |= templates[3]
        chart.tax_template_ids |= templates[4]

        self.env.user.write({
            'company_ids': [(4, company.id)],
            'company_id': company.id,
        })
        self.with_context(
            company_id=company.id, force_company=company.id)
        wizard = self.env['wizard.multi.charts.accounts'].create({
            'company_id': company.id,
            'chart_template_id': chart.id,
            'code_digits': 6,
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': chart.transfer_account_id.id,
            'sale_tax_id': chart.tax_template_ids.filtered(
                lambda t: t.type_tax_use == 'sale').id,
            'purchase_tax_id': chart.tax_template_ids.filtered(
                lambda t: t.type_tax_use == 'purchase').id,
        })
        wizard.onchange_chart_template_id()
        wizard.execute()
        return True

    def setUp(self):
        super(TestAccountChartTemplate, self).setUp()
        self.env.ref('base.group_multi_company').write({
            'users': [(4, self.env.uid)],
        })
        # Create companies
        self.company = self.env['res.company'].create({
            'name': 'Test company 1',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
        })
        # Create charts
        templates = self._get_templates()

        self.chart = self.env['account.chart.template'].create({
            'name': 'Test Chart',
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': templates[0].id,
            'property_account_receivable_id': templates[1].id,
            'property_account_payable_id': templates[2].id,
        })

        self._chart_of_accounts_create(self.company, self.chart, templates)

        self.chart_2 = self.env['account.chart.template'].create({
            'name': 'Test Chart 2',
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': templates[0].id,
            'property_account_receivable_id': templates[1].id,
            'property_account_payable_id': templates[2].id,
        })

        self._chart_of_accounts_create(self.company_2, self.chart_2, templates)

        self.main_partner = self._create_partner()

    def _create_partner(self):
        return self.env['res.partner'].create({
            'name': 'Acme, Inc.',
            'country_id': self.env.ref('base.us').id,
            'company_id': False,
        })

    def test_tax_template(self):
        """Check that the tax templates have no company"""
        tax_templates = self.env['account.tax.template'].search(
            [('company_id', '!=', False)])
        self.assertEqual(len(tax_templates), 0)
