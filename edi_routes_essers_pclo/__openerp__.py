{
    'name': 'edi_routes_essers_pclo',
    'summary': 'Essers PCLO communication using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_routes_essers',
    ],
    'data': [
        'data/config.xml',
        'data/product.xml',
        'wizard/essers_pclo_import.xml',
    ],
    'installable': True,
    'auto_install': False,
}
