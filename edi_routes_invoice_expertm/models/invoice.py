import copy
import datetime
import json

from openerp import api, _
from openerp.osv import osv
from openerp.addons.edi import EDIMixin
from openerp.addons.edi_tools.models.exceptions import EdiValidationError

import re
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import xmltodict

class account_invoice(osv.Model, EDIMixin):
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.model
    def valid_for_edi_export_invoice_expertm(self, record):
        if record.state != 'open':
            return True
        return True

    @api.multi
    def send_edi_export_invoice_expertm(self, partner_id):
        valid_invoices = self.filtered(self.valid_for_edi_export_invoice_expertm)
        invalid_invoices = [p for p in self if p not in valid_invoices]
        if invalid_invoices:
            raise except_orm(_('Invalid pickings in selection!'), _('The following pickings are invalid, please remove from selection. %s') % (map(lambda record: record.name, invalid_invoices)))

        content = valid_invoices.edi_export_invoice_expertm(edi_struct=None)
        result = self.env['edi.tools.edi.document.outgoing'].create_from_content('expertm', content, partner_id.id, 'account.invoice', 'send_edi_export_invoice_expertm', type='XML')
        if not result:
            raise except_orm(_('EDI creation failed!', _('EDI processing failed for the following invoice %s') % (invoice.name)))

        return result

    @api.cr_uid_ids_context
    def edi_export_invoice_expertm(self, cr, uid, ids, edi_struct=None, context=None):
        root = ET.Element("ImportExpMPlus")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

        inv_db = self.pool.get('account.invoice')

        invoices = inv_db.browse(cr, uid, ids, context=context)
        invoice = next(iter(invoices), None)

        sales = ET.SubElement(root, "Sales")
        sale = ET.SubElement(sales, "Sale")
        for invoice in invoices:
            sale = ET.SubElement(sales, "Sale")
            total_done = False
            numbers = re.findall('\d+', invoice.number)
            invoice_type = '10'
            if invoice.type == 'out_refund':
                invoice_type = '30'
            if invoice.partner_id.parent_id:
                ET.SubElement(sale, "Customer_Prime").text = invoice.partner_id.parent_id.expertm_reference
            else:
                ET.SubElement(sale, "Customer_Prime").text = invoice.partner_id.expertm_reference

            ET.SubElement(sale, "CurrencyCode").text   = invoice.currency_id.name
            ET.SubElement(sale, "DocType").text        = invoice_type
            ET.SubElement(sale, "DocNumber").text      = ''.join(numbers)
            ET.SubElement(sale, "DocDate").text        = datetime.datetime.strptime(invoice.date_invoice, "%Y-%m-%d").strftime("%d/%m/%Y")
            ET.SubElement(sale, "DueDate").text        = datetime.datetime.strptime(invoice.date_due, "%Y-%m-%d").strftime("%d/%m/%Y")
            ET.SubElement(sale, "OurRef").text         = invoice.name
            ET.SubElement(sale, "Amount").text         = ('%.2f' % invoice.amount_total).replace('.',',')
            ET.SubElement(sale, "Status").text         = '0'

            details = ET.SubElement(sale, "Details")
            for line in invoice.move_id.line_id:

                if invoice.account_id.code == line.account_id.code and total_done:
                    continue

                detail = ET.SubElement(details, "Detail")
                anal = ET.SubElement(detail, "Analytics1")
                anal = ET.SubElement(anal, "Analytic")

                if invoice.account_id.code == line.account_id.code:

                    total_done = True
                    ET.SubElement(detail, "Amount").text  = ('%.2f' % invoice.amount_total).replace('.',',')
                    ET.SubElement(anal, "Amount").text    = ('%.2f' % invoice.amount_total).replace('.',',')
                    if invoice.type == 'out_refund':
                        ET.SubElement(detail, "DebCre").text  = '-1'
                    else:
                        ET.SubElement(detail, "DebCre").text  = '1'
                else:

                    if line.debit != 0:
                        ET.SubElement(detail, "Amount").text  = ('%.2f' % line.debit).replace('.',',')
                        ET.SubElement(anal, "Amount").text    = ('%.2f' % line.debit).replace('.',',')
                        ET.SubElement(detail, "DebCre").text  = '1'
                    else:
                        ET.SubElement(detail, "Amount").text  = ('%.2f' % line.credit).replace('.',',')
                        ET.SubElement(anal, "Amount").text    = ('%.2f' % line.credit).replace('.',',')
                        ET.SubElement(detail, "DebCre").text  = '-1'

                ET.SubElement(detail, "Account").text = line.account_id.code

                if line.tax_code_id:
                    ET.SubElement(detail, "Ventil").text  = line.tax_code_id.ventil_code
                    ET.SubElement(detail, "VAT1").text    = line.tax_code_id.code
                else:
                    ET.SubElement(detail, "Ventil").text  = '0'
        #return consolidated XML result
        return root

# class account_invoice_line(osv.Model):
#
#     _name = "account.invoice.line"
#     _inherit = "account.invoice.line"
#
#     def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
#
#         result = super(account_invoice_line,self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context, company_id)
#         if not partner_id or not product:
#             return result
#
#         prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
#         if type == 'out_refund':
#             backup = result['value']['account_id']
#             result['value']['account_id'] = prod.property_account_expense.id
#             if not result['value']['account_id']:
#                 result['value']['account_id'] = prod.categ_id.refund_account.id
#             if not result['value']['account_id']:
#                 result['value']['account_id'] = backup
#
#         fpos_db = self.pool.get('account.fiscal.position')
#         fpos = fposition_id and fpos_db.browse(cr, uid, fposition_id, context=context) or False
#         result['value']['account_id'] = fpos_db.map_account(cr, uid, fpos, result['value']['account_id'])
#         return result
