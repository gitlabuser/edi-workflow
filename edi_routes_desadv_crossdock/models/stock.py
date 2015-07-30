import copy
import datetime
from itertools import groupby
import json
import logging

from openerp import api, _
from openerp.osv import osv, fields
from openerp.exceptions import except_orm
from openerp.addons.edi import EDIMixin

_logger = logging.getLogger(__name__)

DESADV_PARTY = {
    'qual': '',
    'gln': '',
}

DESADV = {
    'message': {
        #'desadv_naam': '',        #desadv_naam
        'berichtdatum': '',  # system date/time
        'orderdatum': '',  # SO date
        'pakbonnummer': '',  # stock.picking.out:name
        'leverplandatum': '',  # stock.picking.out:min_date
        'despatchdtm': '',  # stock.picking.out:date_done
        'klantreferentie': '',  # stock.picking.out:order_reference
        'partys': {'party': []},  # partner details
        'cpss': {  # line items
            'cps': [],
        },
    },
}


class stock_picking(osv.Model, EDIMixin):
    _inherit = "stock.picking"

    def _get_desadv_cps_segment(self):
        cps = {
            'pacs': {"pac": []},
            'lines': {"line": []},
        }
        return cps

    def _get_desadv_cps_pac_segment(self):
        cps = {
            'pacs': {"pac": []},
        }
        return cps

    @api.model
    def valid_for_edi_export_desadv_crossdock(self, record):
        if record.state != 'done':
            return False
        return True

    @api.multi
    def send_edi_export_desadv_crossdock(self, partner_id):
        valid_pickings = self.filtered(self.valid_for_edi_export_desadv_crossdock)
        invalid_pickings = [p for p in self if p not in valid_pickings]
        if invalid_pickings:
            raise except_orm(_('Invalid pickings in selection!'), _('The following pickings are invalid, please remove from selection. %s') % (map(lambda record: record.name, invalid_pickings)))

        if len(set([p.desadv_name for p in valid_pickings])) > 1:
            raise except_orm(_('Invalid selection!'), _('The pickings you selected contain different desadv_name attribute values, please change the selection. %s') % (map(lambda record: (record.name, record.desadv_name), valid_pickings)))

        content = valid_pickings.edi_export_desadv_crossdock(edi_struct=None)
        result = self.env['edi.tools.edi.document.outgoing'].create_from_content(valid_pickings[0].desadv_name or picking.name, content, partner_id.id, 'stock.picking', 'send_edi_export_desadv_crossdock')
        if not result:
            raise except_orm(_('EDI creation failed!', _('EDI processing failed for the following picking %s') % (picking.name)))

        return True

    @api.cr_uid_ids_context
    def edi_export_desadv_crossdock(self, cr, uid, ids, edi_struct=None, context=None):
        edi_doc = copy.deepcopy(dict(DESADV))

        partner_db = self.pool.get('res.partner')
        order_db = self.pool.get('sale.order')
        company_db = self.pool.get('res.company')
        product_db = self.pool.get('product.product')
        pick_db = self.pool.get('stock.picking')

        # For header params we take the first delivery
        deliveries = pick_db.browse(cr, uid, ids, context=context)
        delivery = next(iter(deliveries), None)
        _logger.debug("Header info taken from delivery %d (%s)", delivery.id, delivery.name)

        co_id = company_db.search(cr, uid, [])[0]
        so_id = order_db.search(cr, uid, [('name', '=', delivery.origin)])
        if not so_id:
            raise osv.except_osv(_('Warning!'), _("Could not find matching sales order for an item in your selection!"))

        order = order_db.browse(cr, uid, so_id, context)[0]
        company = company_db.browse(cr, uid, co_id, context)
        now = datetime.datetime.now()

        # Basic header fields
        d = datetime.datetime.strptime(delivery.min_date, "%Y-%m-%d %H:%M:%S")
        d_ship = datetime.datetime.strptime(delivery.min_date, "%Y-%m-%d %H:%M:%S")
        d_order = datetime.datetime.strptime(order.date_order, "%Y-%m-%d %H:%M:%S")
        edi_doc['message']['pakbonnummer'] = delivery.desadv_name
        edi_doc['message']['leverplandatum'] = d.strftime("%Y%m%d%H%M%S")
        edi_doc['message']['despatchdtm'] = d_ship.strftime("%Y%m%d")
        edi_doc['message']['berichtdatum'] = now.strftime("%Y%m%d%H%M%S")
        edi_doc['message']['klantreferentie'] = delivery.order_reference
        edi_doc['message']['orderdatum'] = d_order.strftime("%Y%m%d")

        if company:
            partner = partner_db.browse(cr, uid, company.partner_id.id, context)
            if partner and partner.ref:
                partner_doc = copy.deepcopy(dict(DESADV_PARTY))
                partner_doc['qual'] = 'SU'
                partner_doc['gln'] = partner.ref
                edi_doc['message']['partys']['party'].append(partner_doc)
                partner_doc = copy.deepcopy(dict(DESADV_PARTY))
                partner_doc['qual'] = 'SH'
                partner_doc['gln'] = partner.ref
                edi_doc['message']['partys']['party'].append(partner_doc)

        partner = partner_db.browse(cr, uid, delivery.partner_id.id, context)
        if partner and partner.ref:
            partner_doc = copy.deepcopy(dict(DESADV_PARTY))
            partner_doc['qual'] = 'DP'
            partner_doc['gln'] = partner.ref
            edi_doc['message']['partys']['party'].append(partner_doc)

        # Get trackings from all delivery lines without duplicates
        trackings = []
        for delivery in deliveries:
            for operation in delivery.pack_operation_ids:
                if operation.result_package_id:
                    trackings.append(operation.result_package_id)
                else:
                    raise osv.except_osv(_('Warning!'), _("There is a line without SSCC number (pack) {!s}").format(line))
        trackings = set(trackings)  # remove duplicates

        def find_root(element):
            if element.parent_id:
                return find_root(element.parent_id)
            else:
                return element

        # find all root trackings
        tracking_roots = map(find_root, trackings)
        tracking_roots = set(tracking_roots)

        def traverse(node, parent_node=None):
            yield node, parent_node
            for child in node.children_ids:
                for r1, r2 in traverse(child, node):
                    yield r1, r2

        def _build_cps_for_tracking(tracking, parent_cps_counter=None, line_counter=1):
            cps_segment = {
                "line": cps_counter,
                "pacs": {
                    "pac": []
                },
                "lines": {
                    "line": []
                }
            }
            if parent_cps_counter:
                cps_segment["subline"] = parent_cps_counter

            # only one tracking per cps segment
            tracking_segment = {}
            tracking_segment["iso"] = tracking.ul_id.type  # pallet | box
            tracking_segment["sscc"] = tracking.name
            tracking_segment["qua"] = 1
            tracking_segment["brutweight"] = tracking.weight
            cps_segment["pacs"]["pac"].append(tracking_segment)

            for quant in tracking.quant_ids:
                line_segment = {}
                product = product_db.browse(cr, uid, quant.product_id.id, context)
                so_ids = order_db.search(cr, uid, [('name', '=', quant.history_ids[0].picking_id[0].origin)]) #was origin, nog available on quant
                order = order_db.browse(cr, uid, so_ids, context)
                dtm = datetime.datetime.strptime(order.date_order, "%Y-%m-%d %H:%M:%S")
                line_segment["num"] = line_counter
                line_segment["gtin"] = product.ean13
                line_segment["delqua"] = int(quant.qty)
                line_segment["ucgln"] = order.partner_id.ref
                line_segment["ucorder"] = order.origin
                line_segment["ucorderdate"] = dtm.strftime("%Y%m%d")
                cps_segment["lines"]["line"].append(line_segment)
                line_counter += 1

            if not cps_segment["lines"]["line"]:
                cps_segment.pop("lines")
            return cps_segment, line_counter

        number_of_pallets = 0
        weight_of_pallets = 0
        cps_counter = 1
        line_counter = 1

        # create a root element to hold everything together
        header_cps_segment = {
            "line": cps_counter,
            "pacs": {
                "pac": []
            }
        }
        # append to the edi document
        edi_doc["message"]["cpss"]["cps"].append(header_cps_segment)
        cps_counter += 1

        cps_dictionary = {}
        for tracking in tracking_roots:
            for node, parent_node in traverse(tracking):
                if parent_node:
                    cps_segment, line_counter = _build_cps_for_tracking(node, cps_dictionary[parent_node.id]["line"], line_counter=line_counter)
                else:
                    cps_segment, line_counter = _build_cps_for_tracking(node, 1, line_counter=line_counter)
                cps_dictionary[node.id] = cps_segment
                edi_doc["message"]["cpss"]["cps"].append(cps_segment)
                cps_counter += 1

        # iterate over all cps segments to calculate pallet weight and count
        for cps in edi_doc["message"]["cpss"]["cps"]:
            if not cps["pacs"]["pac"]:
                continue
            pac = cps["pacs"]["pac"][0]
            if pac["iso"] == 'pallet':
                number_of_pallets += 1
                weight_of_pallets += pac["brutweight"]

        # add total weight of pallets and count of pallets to the first segment
        header_cps_segment["pacs"]["pac"].append({
            "totbrutweight": int(weight_of_pallets),
            "qua": int(number_of_pallets),
            "iso": "pallet"
        })

        return edi_doc
