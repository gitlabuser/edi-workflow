from openerp.osv import osv, fields

import logging
import os

_logger = logging.getLogger(__name__)

class edi_partner(osv.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'edi_relevant' : fields.boolean('EDI Relevant'),
        'edi_flows': fields.one2many('edi.tools.edi.partnerflow', 'partnerflow_id', 'EDI Flows', readonly=False),
    }

    def create(self, cr, uid, vals, context=None):
        ''' Make sure all required EDI directories are created '''
        new_id = super(edi_partner, self).create(cr, uid, vals, context=context)
        self.maintain_edi_directories(cr, uid, [new_id], context)
        self.update_partner_overview_file(cr, uid, context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        ''' Make sure all required EDI directories are created '''
        result = super(edi_partner, self).write(cr, uid, ids, vals, context=context)
        self.maintain_edi_directories(cr, uid, ids, context)
        self.update_partner_overview_file(cr, uid, context)
        return result

    def maintain_edi_directories(self, cr, uid, ids, context=None):
        ''' This method creates all EDI directories for a given set of partners.
        A root folder based on the partner_id is created, with a set of sub
        folders for all the EDI flows he is subscried to. '''

        _logger.debug('Maintaining the EDI directories')
        _logger.debug('The present working directory is: {!s}'.format(os.getcwd()))

        # Only process partners that are EDI relevant
        for partner in self.browse(cr, uid, ids, context=context):
            if not partner.edi_relevant:
                continue
            _logger.debug("Processing partner %d (%s)", partner.id, partner.name)

            # Find and/or create the root directory for this partner
            edi_directory = self.pool.get('ir.values').get_defaults_dict(cr, uid, 'edi.tools.config.settings')['edi_root_directory']
            root_path = os.path.join(os.sep, edi_directory, cr.dbname, str(partner.id))
            if not os.path.exists(root_path):
                _logger.debug('Required directory missing, attempting to create: {!s}'.format(root_path))
                os.makedirs(root_path)

            # Loop over all the EDI Flows this partner is subscribed to
            # and make sure all the necessary sub folders exist.
            for flow in partner.edi_flows:
                sub_path = os.path.join(root_path, str(flow.flow_id.id))
                if not os.path.exists(sub_path):
                    _logger.debug('Required directory missing, attempting to create: {!s}'.format(sub_path))
                    os.makedirs(sub_path)

                # Create folders to help the system keep track
                if flow.flow_id.direction == 'in':
                    _logger.debug("Creating directories imported and archived for incoming edi documents")
                    if not os.path.exists(os.path.join(sub_path, 'imported')): os.makedirs(os.path.join(sub_path, 'imported'))
                    if not os.path.exists(os.path.join(sub_path, 'archived')): os.makedirs(os.path.join(sub_path, 'archived'))

    def update_partner_overview_file(self, cr, uid, context):
        ''' This method creates a file for eachin the root EDI directory to give a matching
        list of partner_id's with their current corresponding names for easier
        lookups. '''

        _logger.debug('Updating the EDI partner overview file')
        _logger.debug('The present working directory is: {!s}'.format(os.getcwd()))

        # Find all active EDI partners
        partner_db = self.pool.get('res.partner')
        pids = partner_db.search(cr, uid, [('edi_relevant', '=', True)])
        if not pids:
            return True

        # Loop over each partner and create a simple.debug list
        partners = partner_db.browse(cr, uid, pids, None)
        content = ""
        for partner in partners:
            content += str(partner.id) + " " + partner.name + "\n"

            for flow in partner.edi_flows:
                content += "\t" + str(flow.flow_id.id) + " " + flow.flow_id.name + "\n"

        # Write this.debug to a helper file
        edi_directory = self.pool.get('ir.values').get_defaults_dict(cr, uid, 'edi.tools.config.settings')['edi_root_directory']
        if not os.path.exists(os.path.join(edi_directory, cr.dbname)): os.makedirs(os.path.join(edi_directory, cr.dbname))
        file_path = os.path.join(edi_directory, cr.dbname, "partners.edi")
        _logger.debug('Attempting to look up the partner file at: {!s}'.format(file_path))
        f = open(file_path ,"w")
        f.write(content)
        f.close()

    def listen_to_edi_flow(self, cr, uid, partner_id, flow_id):
        ''' This method adds an EDI flow to a partner '''
        if not partner_id or not flow_id: return False

        partner = self.browse(cr, uid, partner_id)
        exists = [flow for flow in partner.edi_flows if flow.flow_id.id == flow_id]
        if exists:
            vals = {'edi_flows': [[1, exists[0].id, {'partnerflow_active': True, 'flow_id': flow_id}]]}
            return self.write(cr, uid, [partner_id], vals)
        else:
            vals = {'edi_flows': [[0, False, {'partnerflow_active': True, 'flow_id': flow_id}]]}
            return self.write(cr, uid, [partner_id], vals)


    def is_listening_to_flow(self, cr, uid, partner_id, flow_id):
        ''' This method checks wether or not a partner
        is listening to a given flow. '''
        if not partner_id or not flow_id: return False

        partner = self.browse(cr, uid, partner_id)
        if not partner.edi_relevant: return False
        exists = next(flow for flow in partner.edi_flows if flow.flow_id.id == flow_id)
        if exists and exists.partnerflow_active:
            return True
        return False