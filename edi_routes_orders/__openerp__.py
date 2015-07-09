{
    'name': 'edi_routes_orders',
    'summary': 'Edifact ORDERS communication using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_tools',
        'sale',
    ],
    'data': [
        'data/config.xml',
    ],
    'installable': True,
    'auto_install': False,
}
