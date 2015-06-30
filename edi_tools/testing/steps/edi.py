from behave import *
from os.path import isfile, join
from os import removedirs, path
from shutil import rmtree


_partner_name = 'PartnerUT'
_root_path = '../../../../../EDI'





@given('partners have already been created')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    ids = partner_db.search([('name', '=', _partner_name)])
    partner_db.unlink(ids)
    for partner in ids:
        myPath = join(_root_path, 'openerpdev3', str(partner))
        assert os.path.exists(myPath)
        rmtree(myPath, True)




@given('an EDI relevant partner')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    ids = partner_db.search([('name', '=', _partner_name)])
    if not ids:
        partner_db.create({'name': _partner_name, 'edi_relevant' : True})
    pass


@then('a partner should have been created')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids

@then('the partner should be EDI relevant')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids
    partners = partner_db.browse(ids)
    assert partners
    assert [x for x in partners if x.edi_relevant]

@then('a folder should have been created')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids
    for partner in ids:
        myPath = join(_root_path, 'openerpdev3', str(partner))
        assert os.path.exists(myPath)






@when('this partner is assigned an incoming and outgoing flow')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    partnerflow_db = context.client.model('edi.tools.edi.partnerflow')
    flow_db = context.client.model('edi.tools.edi.flow')
    flow_in = flow_db.search([('name', '=', 'Delivery Order(in)')])[0]
    flow_out = flow_db.search([('name', '=', 'Delivery Order(out)')])[0]

    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids
    for partner in ids:
        partnerflow_db.create({'partnerflow_id': partner, 'flow_id': flow_in, 'partnerflow_active': True})
        partnerflow_db.create({'partnerflow_id': partner, 'flow_id': flow_out, 'partnerflow_active': True})
    partner_db.write(ids, {'street':'godver'})



@then('the flows should be assigned to the partner')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    flow_db = context.client.model('edi.tools.edi.flow')
    flow_in = flow_db.search([('name', '=', 'Delivery Order(in)')])[0]
    flow_out = flow_db.search([('name', '=', 'Delivery Order(out)')])[0]

    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids
    partners = partner_db.browse(ids)
    assert partners
    for partner in partners:
        assert [x for x in partner.edi_flows if x.flow_id.id == flow_in]
        assert [x for x in partner.edi_flows if x.flow_id.id == flow_out]


@then('the EDI folders should be created on the system')
def step_impl(context):
    partner_db = context.client.model('res.partner')
    flow_db = context.client.model('edi.tools.edi.flow')
    flow_in = flow_db.search([('name', '=', 'Delivery Order(in)')])[0]
    flow_out = flow_db.search([('name', '=', 'Delivery Order(out)')])[0]

    ids = partner_db.search([('name', '=', _partner_name)])
    assert ids
    partners = partner_db.browse(ids)
    assert partners
    for partner in partners:
        myPath = join(_root_path, 'openerpdev3', str(partner.id), str(flow_in))
        assert os.path.exists(myPath)
        myPath = join(_root_path, 'openerpdev3', str(partner.id), str(flow_in),'imported')
        assert os.path.exists(myPath)
        myPath = join(_root_path, 'openerpdev3', str(partner.id), str(flow_in), 'archived')
        assert os.path.exists(myPath)

        myPath = join(_root_path, 'openerpdev3', str(partner.id), str(flow_out))
        assert os.path.exists(myPath)
































