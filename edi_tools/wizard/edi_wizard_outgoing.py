from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

class edi_tools_edi_wizard_outgoing(models.TransientModel):
    _name = 'edi.tools.edi.wizard.outgoing'

    @api.model
    def _default_flow(self):
        active_model = self._context.get('active_model')
        if not active_model: return False
        return self.env['edi.tools.edi.flow'].search([('model', '=', active_model)], limit=1)

    @api.model
    def _default_partner(self):
        active_model = self._context.get('active_model')
        if not active_model: return False
        flows = self.env['edi.tools.edi.flow'].search([('model', '=', active_model)], limit=1)
        partnerflow = self.env['edi.tools.edi.partnerflow'].search([('flow_id', 'in', flows.ids)], limit=1)
        if not partnerflow: return False
        return partnerflow.partnerflow_id

    flow_id = fields.Many2one('edi.tools.edi.flow', string='EDI Flow', required=True, default=_default_flow)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, default=_default_partner)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(edi_tools_edi_wizard_outgoing, self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if not context.get('active_model'): return res
        # limit flows based on the ones that are active
        partnerflows = self.env['edi.tools.edi.partnerflow'].search([('partnerflow_active', '=', True)])
        active_flows = [ep.flow_id for ep in partnerflows if ep.flow_id.model == context.get('active_model')]
        if not not active_flows: return res
        active_partners = [ep.partnerflow_id for ep in partnerflows if ep.flow_id in active_flows]
        # limit flows based on the model
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='flow_id']")
        for node in nodes:
            node.set('domain', '[("id", "in", '+ str(active_flows.ids)+')]')
        res['arch'] = etree.tostring(doc)
        if not active_partners: return res
        partners = self.env['res.partner'].search([('edi_flows', 'in', active_partners.ids)])
        nodes = doc.xpath("//field[@name='partner_id']")
        for node in nodes:
            node.set('domain', '[("id", "in", '+ str([p.id for p in partners])+')]')
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def send(self):
        self._check_partner_allowed(self.flow_id, self.partner_id)
        records = self.env[self.flow_id.model].browse(self._context.get('active_ids',[]))
        result = getattr(records, self.flow_id.method)(self.partner_id)
        if not result:
            raise except_orm(_('EDI creation failed!'), _('Something went wrong during processing of edi flow %s.') % (self.flow_id.name))
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def _check_partner_allowed(self, flow_id, partner_id):
        if not partner_id.edi_relevant:
            raise except_orm(_('Invalid Partner!'), _('The partner %s is not marked as EDI Relevant') % (partner_id.name))
        if flow_id not in [pf.flow_id for pf in partner_id.edi_flows if pf.partnerflow_active]:
            raise except_orm(_('Invalid Flow!'), _('The flow %s is not active for partner %s.') % (flow_id.name, partner_id.name))
        return True
