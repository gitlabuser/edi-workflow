import datetime
import xml.etree.cElementTree as ET


class EssersEdiBuilder(object):

    def build_e1bpdlvpartner_element(self, parent_element, sequence='', role='', name=''):
        element = ET.SubElement(parent_element, "E1BPDLVPARTNER")
        element.set('SEGMENT', '1')
        ET.SubElement(element, "ADDRESS_NO").text = sequence
        ET.SubElement(element, "PARTN_ROLE").text = role
        ET.SubElement(element, "PARTNER_NO").text = name

    def build_e1bpadr1_element(self, parent_element, sequence='', name='', city='', zipcode='', street1='', street2='', country='', language=''):
        element = ET.SubElement(parent_element, "E1BPADR1")
        element.set('SEGMENT', '1')
        ET.SubElement(element, "ADDR_NO").text = sequence
        ET.SubElement(element, "NAME").text = name
        ET.SubElement(element, "CITY").text = city
        ET.SubElement(element, "POSTL_COD1").text = zipcode
        ET.SubElement(element, "STREET").text = street1
        ET.SubElement(element, "STR_SUPPL1").text = street2
        ET.SubElement(element, "COUNTRY").text = country
        ET.SubElement(element, "LANGU").text = language or 'NL'

    def build_e1bpdlvdeadln_element(self, parent_element, number, delivery_date, date_zone):
        element = ET.SubElement(parent_element, "E1BPDLVDEADLN")
        element.set('SEGMENT', '1')
        ET.SubElement(element, "DELIV_NUMB").text = number
        ET.SubElement(element, "TIMETYPE").text = 'WSHDRLFDAT'
        ET.SubElement(element, "TIMESTAMP_UTC").text = datetime.datetime.strptime(delivery_date, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
        ET.SubElement(element, "TIMEZONE").text = date_zone

    def build_e1bptext_element(self, parent_element, param, row, field, value):
        element = ET.SubElement(parent_element, "E1BPEXT")
        element.set('SEGMENT', '1')
        ET.SubElement(element, "PARAM").text = param
        ET.SubElement(element, "ROW").text = row
        ET.SubElement(element, "FIELD").text = field
        ET.SubElement(element, "VALUE").text = value
