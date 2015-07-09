{
    'name': 'edi_routes_desadv',
    'summary': 'Edifact DESADV communication using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_tools',
        'edi_stock_enable',
        'stock',
        'sale_stock_reference_chainer',
    ],
    'data': [
        'views/stock_view.xml',
        'wizard/delivery_out.xml',
    ],
    'installable': True,
    'auto_install': False,
}
