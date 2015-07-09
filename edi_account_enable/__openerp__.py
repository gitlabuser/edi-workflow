# -*- coding: utf-8 -*-
#    Author: Jan Vereecken
#    Copyright 2015 Clubit BVBA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

{'name': 'EDI for accounting',
 'summary': 'Enable sending EDI for accounting objects',
 'version': '0.1',
 'author': "Clubit BVBA",
 'category': 'Warehouse Management',
 'license': 'AGPL-3',
 'images': [],
 'depends': ['edi_tools','account'],
 'data': [
     'wizards/invoice.xml',
 ],
 'auto_install': False,
 'installable': True,
 }