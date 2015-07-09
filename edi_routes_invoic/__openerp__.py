{
    'name': 'edi_routes_invoic',
    'summary': 'Edifact INVOIC communication using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_tools',
        'edi_account_enable',
        'edi_routes_desadv',
        'account',
    ],
    'data': [
        'data/config.xml',
    ],
    'installable': True,
    'auto_install': False,
}
