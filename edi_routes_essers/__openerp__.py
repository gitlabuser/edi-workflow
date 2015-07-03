{
    'name': 'edi_routes_essers',
    'summary': 'Send deliveries to Essers using the EDI framework',
    'version': '1.0',
    'category': 'EDI Tools',
    'author': 'Clubit BVBA',
    'website': 'http://www.clubit.be',
    'depends': [
        'edi_tools',
        'edi_stock_enable',
        'stock',
        'sale_stock_reference_chainer',
        'sale_stock_incoterm_chainer',
        'product_customerinfo',
        'delivery_instructions',
    ],
    'data': [
        'data/config.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
