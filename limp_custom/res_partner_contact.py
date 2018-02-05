# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields

class res_partner_contact(models.Model):

    _inherit = "res.partner.contact"

    _columns = {
        'first_name': fields.char('First Name', size=64, required=True),
        'address': fields.related('job_ids','address_id',type='many2one',relation='res.partner',string='Address'),
        'colege_num': fields.char('Colege number', size=64)
    }

    def name_get(self, cr, user, ids, context=None):
        if not len(ids):
            return []
        res = []
        for contact in self.browse(cr, user, ids, context=context):
            _contact = ""
            if contact.title:
                _contact += "%s "%(contact.title.name)
            _contact += contact.first_name or ""
            if contact.name and contact.first_name:
                _contact += " "
            _contact += contact.name or ""
            res.append((contact.id, _contact))
        return res


res_partner_contact()
