from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc

class edi_tools_edi_wizard_archive_incoming(osv.TransientModel):
    _name = 'edi.tools.edi.wizard.archive.incoming'
    _description = 'Archive EDI Documents'

    ''' edi.tools.edi.wizard.archive.incoming:archive()
        --------------------------------------------------
        This method is used by the EDI wizard to push
        multiple documents to the workflow "archived" state.
        ---------------------------------------------------- '''
    def archive(self, cr, uid, ids, context=None):
        # Get the selected documents
        # --------------------------
        ids = context.get('active_ids',[])
        if not ids:
            raise osv.except_osv(_('Warning!'), _("You did not provide any documents to archive!"))

        # Push each document to archived
        # ------------------------------
        wf_service = netsvc.LocalService("workflow")
        for document in self.pool.get('edi.tools.edi.document.incoming').browse(cr, uid, ids, context):
            if document.state in ['new','ready','processed','in_error']:
                wf_service.trg_validate(uid, 'edi.tools.edi.document.incoming', document.id, 'button_to_archived', cr)

        return {'type': 'ir.actions.act_window_close'}

