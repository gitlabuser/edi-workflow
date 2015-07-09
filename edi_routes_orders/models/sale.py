import datetime
import json

from openerp.osv import osv
from openerp.addons.edi import EDIMixin
from openerp.tools.translate import _
from openerp.addons.edi_tools.models.exceptions import EdiValidationError


class sale_order(osv.Model, EDIMixin):
    _name = "sale.order"
    _inherit = "sale.order"

    def edi_import_orders_d96a_validator(self, cr, uid, ids, context):
        edi_db = self.pool.get('edi.tools.edi.document.incoming')
        document = edi_db.browse(cr, uid, ids, context)

        try:
            data = json.loads(document.content)
            if not data:
                raise EdiValidationError('EDI Document is empty.')
        except Exception:
            raise EdiValidationError('Content is not valid JSON.')

        # Does this document have the correct root name?
        if not 'message' in data:
            raise EdiValidationError('Could not find field: message.')
        data = data['message']

        # Validate the document reference
        if not 'docnum' in data:
            raise EdiValidationError('Could not find field: docnum.')

        order_ids = self.search(cr, uid, [('client_order_ref', '=', data['docnum']), ('state', '!=', 'cancelled')])
        if order_ids:
            order = self.browse(cr, uid, order_ids)[0]
            raise EdiValidationError("Sales order %s exists for this reference" % (order.name,))

        # Validate the sender
        if not 'sender' in data:
            raise EdiValidationError('Could not find field: sender.')

        # Validate all the partners
        found_by = False
        found_dp = False
        found_iv = False
        if not 'partys' in data:
            raise EdiValidationError('Could not find field: partys.')
        try:
            data['partys'] = data['partys'][0]['party']
        except Exception:
            raise EdiValidationError('Erroneous structure for table: partys.')
        if len(data['partys']) == 0:
            raise EdiValidationError('Content of table partys is empty. ')

        partner_db = self.pool.get('res.partner')
        for party in data['partys']:
            if not 'qual' in party:
                raise EdiValidationError('Could not find field: qual (partner).')
            if not 'gln' in party:
                raise EdiValidationError('Could not find field: gln (partner).')
            pids = partner_db.search(cr, uid, [('ref', '=', party['gln'])])
            if not pids:
                raise EdiValidationError('Could not resolve partner {!s}.'.format(party['gln']))
            if party['qual'] == 'BY':
                found_by = True
            elif party['qual'] == 'DP':
                found_dp = True
        if not found_by or not found_dp:
            raise EdiValidationError('Couldnt find all required partners BY,DP.')

        # Validate all the line items
        if not 'lines' in data:
            raise EdiValidationError('Could not find field: lines.')
        try:
            data['lines'] = data['lines'][0]['line']
        except Exception:
            raise EdiValidationError('Erroneous structure for table: lines.')
        if len(data['lines']) == 0:
            raise EdiValidationError('Content of table lines is empty. ')

        product = self.pool.get('product.product')
        for line in data['lines']:
            if not 'ordqua' in line:
                raise EdiValidationError('Could not find field: ordqua (line).')
            if line['ordqua'] < 1:
                raise EdiValidationError('Ordqua (line) should be larger than 0.')
            if not 'gtin' in line:
                raise EdiValidationError('Could not find field: gtin (line).')
            pids = product.search(cr, uid, [('ean13', '=', line['gtin'])])
            if not pids:
                raise EdiValidationError('Could not resolve product {!s}.'.format(line['gtin']))

        # Validate timing information
        if not 'deldtm' in data:
            raise EdiValidationError('Could not find field: deldtm.')
        if not 'docdtm' in data:
            raise EdiValidationError('Could not find field: docdtm.')

        # If we get all the way to here, the document is valid
        return True

    def receive_edi_import_orders_d96a(self, cr, uid, ids, context=None):
        edi_db = self.pool.get('edi.tools.edi.document.incoming')
        document = edi_db.browse(cr, uid, ids, context)
        return self.edi_import_orders_d96a(cr, uid, document, context=context)

    def edi_import_orders_d96a(self, cr, uid, document, context=None):
        data = json.loads(document.content)
        data = data['message']
        data['partys'] = data['partys'][0]['party']
        data['lines'] = data['lines'][0]['line']
        name = self.create_sale_order(cr, uid, data, context)
        if not name:
            raise except_orm(_('No sales order created!'), _('Something went wrong while creating the sales order.'))
        edi_db = self.pool.get('edi.tools.edi.document.incoming')
        edi_db.message_post(cr, uid, document.id, body='Sale order {!s} created'.format(name))
        return True

    def create_sale_order(self, cr, uid, data, context):
        # Prepare the call to create a sale order
        param = {}
        param['origin'] = data['docnum']
        param['message_follower_ids'] = False
        param['categ_ids'] = False
        param['picking_policy'] = 'one'
        param['order_policy'] = 'picking'
        param['carrier_id'] = False
        param['invoice_quantity'] = 'order'
        param['client_order_ref'] = data['docnum']
        param['requested_date'] = data['deldtm'][:4] + '-' + data['deldtm'][4:-2] + '-' + data['deldtm'][6:]
        param['message_ids'] = False
        param['note'] = False
        param['project_id'] = False
        param['incoterm'] = False
        param['section_id'] = False

        # Enter all partner data
        partner_db = self.pool.get('res.partner')
        fiscal_pos = False

        for party in data['partys']:
            if party['qual'] == 'BY':
                pids = partner_db.search(cr, uid, [('ref', '=', party['gln'])])
                buyer = partner_db.browse(cr, uid, pids, context)[0]
                param['partner_id'] = buyer.id
                param['user_id'] = buyer.user_id.id
                param['fiscal_position'] = buyer.property_account_position.id
                param['payment_term'] = buyer.property_payment_term.id
                param['pricelist_id'] = buyer.property_product_pricelist.id
                fiscal_pos = self.pool.get('account.fiscal.position').browse(cr, uid, buyer.property_account_position.id) or False

            if party['qual'] == 'IV':
                pids = partner_db.search(cr, uid, [('ref', '=', party['gln'])])
                iv = partner_db.browse(cr, uid, pids, context)[0]
                param['partner_invoice_id'] = iv.id

            if party['qual'] == 'DP':
                pids = partner_db.search(cr, uid, [('ref', '=', party['gln'])])
                dp = partner_db.browse(cr, uid, pids, context)[0]
                param['partner_shipping_id'] = dp.id

        # if IV partner is not present invoice partner is
        #  - parent of BY or
        #  - BY
        if not param.get('partner_invoice_id', None):
            buyer = partner_db.browse(cr, uid, param['partner_id'], context)
            param['partner_invoice_id'] = buyer.id
            if buyer.parent_id:
                param['partner_invoice_id'] = buyer.parent_id.id

        if 'partner_shipping_id' not in param:
            param['partner_shipping_id'] = param['partner_id']
        if 'user_id' not in param:
            param['user_id'] = uid
        elif not param['user_id']:
            param['user_id'] = uid

        # Create the line items
        product_db = self.pool.get('product.product')
        pricelist_db = self.pool.get('product.pricelist')
        param['order_line'] = []
        for line in data['lines']:

            pids = product_db.search(cr, uid, [('ean13', '=', line['gtin'])])
            prod = product_db.browse(cr, uid, pids, context)[0]

            detail = {}
            detail['property_ids'] = False
            detail['product_uos_qty'] = line['ordqua']
            detail['product_id'] = prod.id
            detail['product_uom'] = prod.uom_id.id

            # If the price is given from the file, use that
            # Otherwise, use the price from the pricelist
            if 'price' in line:
                detail['price_unit'] = line['price']
            else:
                detail['price_unit'] = pricelist_db.price_get(cr, uid, [param['pricelist_id']], prod.id, 1, brico.id)[param['pricelist_id']]

            detail['product_uom_qty'] = line['ordqua']
            detail['customer_product_code'] = False
            detail['name'] = prod.name
            detail['delay'] = False
            detail['discount'] = False
            detail['address_allotment_id'] = False
            detail['th_weight'] = prod.weight * float(line['ordqua'])
            detail['product_uos'] = False
            detail['type'] = 'make_to_stock'
            detail['product_packaging'] = False

            # Tax swapping calculations     u'tax_id': [[6,False, [1,3] ]],
            detail['tax_id'] = False
            if prod.taxes_id:
                detail['tax_id'] = [[6, False, []]]
                if fiscal_pos:
                    new_taxes = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscal_pos, prod.taxes_id)
                    if new_taxes:
                        detail['tax_id'][0][2] = new_taxes
                    else:
                        for tax in prod.taxes_id:
                            detail['tax_id'][0][2].append(tax.id)
                else:
                    for tax in prod.taxes_id:
                        detail['tax_id'][0][2].append(tax.id)

            order_line = []
            order_line.extend([0])
            order_line.extend([False])
            order_line.append(detail)
            param['order_line'].append(order_line)

        # Actually create the sale order
        sid = self.create(cr, uid, param, context=None)
        so = self.browse(cr, uid, [sid], context)[0]
        return so.name

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        result = super(sale_order, self)._get_date_planned(cr, uid, order, line, start_date, context)
        if order.requested_date:
            result = order.requested_date
        return result
