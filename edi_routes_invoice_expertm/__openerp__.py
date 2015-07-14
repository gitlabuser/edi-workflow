{
    'name': 'edi_routes_invoice_expertm',
    'summary': 'Send Invoices to Expert/M XML using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'description': "Expert/M EDI integration",
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'sequence': 9,
    'depends': [
        'edi_tools',
        'edi_account_enable',
        'account',
    ],
    'data': [
        'data/config.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
