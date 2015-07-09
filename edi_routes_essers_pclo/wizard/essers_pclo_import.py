import base64
import time, datetime
import csv, StringIO
from itertools import groupby

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools

import logging

_logger = logging.getLogger(__name__)

class essers_pclo_import(osv.osv_memory):
    _name = 'essers.pclo.import'
    _description = 'Import Essers PCLO File'
    _columns = {
        'pclo_data': fields.binary('PCLO File', required=True),
        'pclo_fname': fields.char('PCLO Filename', size=128, required=True),
        'deliver': fields.boolean('Deliver'),
        'note': fields.text('Log'),
    }

    _defaults = {
        'pclo_fname': 'pclo.csv',
        'deliver': False,
    }

    def pclo_parsing(self, cr, uid, ids, context=None, batch=False, pclofile=None, pclofilename=None):
        if context is None:
            context = {}

        data = self.browse(cr, uid, ids)[0]
        try:
            pclofile = unicode(base64.decodestring(data.pclo_data))
            pclofilename = data.pclo_fname
            execute_deliver = data.deliver
        except:
            raise osv.except_osv(_('Error'), _('Wizard in incorrect state. Please hit the Cancel button'))
            return {}

        pick_out_db = self.pool.get('stock.picking')

        content = pick_out_db.cleanup_pclo_file(pclofile)
        content = self.preprocess_content(cr, uid, content)
        if pick_out_db.edi_import_essers_pclo(self, cr, uid, content, execute_deliver=execute_deliver, context=context):
            return {'type': 'ir.actions.act_window_close'}
        else:
            return {}
