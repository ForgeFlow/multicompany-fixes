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

    def _chart_of_accounts_create(self, company):
        _logger.debug('Creating chart of account')
        self.chart = self.env['account.chart.template'].search([], limit=1)
        self.env.user.write({
            'company_ids': [(4, company.id)],
            'company_id': company.id,
        })
        self.with_context(
            company_id=company.id, force_company=company.id)
        wizard = self.env['wizard.multi.charts.accounts'].create({
            'company_id': company.id,
            'chart_template_id': self.chart.id,
            'code_digits': 6,
            'currency_id': self.env.ref('base.EUR').id,
            'transfer_account_id': self.chart.transfer_account_id.id,
        })
        wizard.onchange_chart_template_id()
        wizard.execute()
        return True

    def setUp(self):
        super(TestAccountChartTemplate, self).setUp()
        self.env.ref('base.group_multi_company').write({
            'users': [(4, self.env.uid)],
        })
        # Create company 1
        self.company = self.env['res.company'].create({
            'name': 'Test company 1',
        })
        # Create chart
        self._chart_of_accounts_create(self.company)

        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
        })
        # Create chart
        self._chart_of_accounts_create(self.company_2)
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
