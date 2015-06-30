# -*- coding: utf-8 -*-
##############################################################################
#
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
#
##############################################################################
{
    'name': 'EDI Tools',
    'summary': 'General Purpose Toolbox',
    'version': '1.0',
    'category': 'Tools',
    'description': "EDI Toolbox basic functionalities",
    'author': 'Clubit',
    'website': 'http://www.clubit.be',
    'depends': ['base', 'mail'],
    'data': [
        'data/edi_schedulers.xml',
        'data/edi_workflow_incoming.xml',
        'security/security.xml',
        'views/edi_view.xml',
        'views/res_config.xml',
        'wizard/edi_wizard_ready.xml',
        'wizard/edi_wizard_archive_incoming.xml',
        'wizard/edi_wizard_outgoing.xml',
],
    'installable': True,
}