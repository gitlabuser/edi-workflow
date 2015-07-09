from openerp import models, fields, api, _

class edi_tools_edi_wizard_outgoing_route_desadv(models.TransientModel):
    _name = 'edi.tools.edi.wizard.outgoing.route.desadv'
    _inherit = 'edi.tools.edi.wizard.outgoing'

    desadv_name = fields.Char('DESADV name', size=64)

    @api.multi
    def send(self):
        self._check_partner_allowed(self.flow_id, self.partner_id)
        records = self.env[self.flow_id.model].browse(self._context.get('active_ids',[]))
        records.write({'desadv_name': self.desadv_name})
        super(edi_tools_edi_wizard_outgoing_route_desadv, self).send()
