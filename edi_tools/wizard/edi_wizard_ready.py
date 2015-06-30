from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc

class edi_tools_edi_wizard_ready(osv.TransientModel):
    _name = 'edi.tools.edi.wizard.ready'
    _description = 'Mark EDI documents as ready'


    ''' edi.tools.edi.wizard.ready:ready()
        ------------------------------------------
        This method is used by the EDI wizard to push
        multiple documents to the workflow "ready" state.
        ------------------------------------------------- '''
    def ready(self, cr, uid, ids, context=None):

        # Get the selected documents
        # --------------------------
        ids = context.get('active_ids',[])
        if not ids:
            raise osv.except_osv(_('Warning!'), _("You did not provide any documents to process!"))

        # Push each document to ready
        # ---------------------------
        wf_service = netsvc.LocalService("workflow")
        for document in self.pool.get('edi.tools.edi.document.incoming').browse(cr, uid, ids, context):
            if document.state == 'new' or document.state == 'in_error':
                wf_service.trg_validate(uid, 'edi.tools.edi.document.incoming', document.id, 'button_to_ready', cr)
