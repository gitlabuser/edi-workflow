{
    'name': 'edi_routes_desadv_crossdock',
    'summary': 'Edifact DESADV (tailored for crossdocking) communication using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_routes_desadv',
        'stock_packaging_weight',
    ],
    'data': [
        'data/config.xml',
    ],
    'installable': True,
    'auto_install': False,
}
