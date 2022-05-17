{
    'name': 'Multi Company Account Invoice Supplier Self Invoice',
    'version': '11.0.1.0.0',
    'summary': 'Account fixes',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    'license': 'LGPL-3',
    'depends': ['mcfix_account', 'account_invoice_supplier_self_invoice'],
    'data': [
        'views/report_self_invoice.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
