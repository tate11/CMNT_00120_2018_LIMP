# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea Servicios Tecnológicos
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


class analytic_balance_by_department(models.TransientModel):
    _name = "analytic.balance.by.department.wzd"

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear', required=True),
        'delegation_id': fields.many2one('res.delegation', 'Delegation'),
        'privacy': fields.selection([('public', 'Public'), ('private', 'Private')], 'Privacy'),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None: context = {}

        data = self.read(cr, uid, ids[0], [])
        data.update({'ids': ids})

        return {'type': 'ir.actions.report.xml',
                 'report_name': 'analytic_balance_by_department_xls',
                 'datas': data }

analytic_balance_by_department()
