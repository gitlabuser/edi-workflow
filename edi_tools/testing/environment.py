import erppeek

client = erppeek.Client('http://localhost:8069', 'openerpdev3', 'admin', 'admin')

def before_all(context):
	context.client = client