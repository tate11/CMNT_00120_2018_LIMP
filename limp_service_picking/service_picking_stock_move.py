# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
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
"""new model between stock_move and service_picking"""

from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _

class service_picking_stock_move(osv.osv):
    """new model between stock_move and service_picking"""

    _name = "service.picking.stock.move"
    _description = "Model between stock_move and analytic_account"
    _rec_name = "move_id"

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Manager', required=True, states={'second':[('readonly',True)]}),
        'location_id': fields.many2one('stock.location', 'Location', required=True, states={'second':[('readonly',True)]}),
        'product_id': fields.many2one('product.product', 'Product', required=True, states={'second':[('readonly',True)]}),
        'product_qty': fields.float('Quantity', required=True, digits_compute=dp.get_precision('Product UoM'), states={'second':[('readonly',True)]}),
        'move_id': fields.many2one('stock.move', 'Move', readonly=True),
        'service_picking_id': fields.many2one('stock.service.picking', 'Service picking'),
        'state': fields.selection([('first', 'First'), ('second', 'Second')], 'State', readonly=True)
    }

    _defaults = {
        'product_qty': 1.0,
        'state': 'first',
        'employee_id': lambda s, c, u, ctx: ctx.get('employee_id', False) or s.pool.get('hr.employee').search(c, u, [('user_id', '=', u)]) and s.pool.get('hr.employee').search(c, u, [('user_id', '=', u)])[0] or False,
        'location_id': lambda s, c, u, ctx: ctx.get('employee_id', False) and s.pool.get('hr.employee').browse(c, u, ctx['employee_id']).location_id and s.pool.get('hr.employee').browse(c, u, ctx['employee_id']).location_id.id or s.pool.get('hr.employee').search(c, u, [('user_id', '=', u)]) and s.pool.get('hr.employee').browse(c, u, s.pool.get('hr.employee').search(c, u, [('user_id', '=', u)])[0]).location_id and s.pool.get('hr.employee').browse(c, u, s.pool.get('hr.employee').search(c, u, [('user_id', '=', u)])[0]).location_id.id or False,
    }

    def create(self, cr, uid, vals, context=None):
        """creates stock_move and add cost in analytic_account"""
        if context is None: context = {}

        id = super(service_picking_stock_move, self).create(cr, uid, vals)

        obj_id = self.browse(cr, uid, id)

        if not obj_id.employee_id.location_id:
            raise osv.except_osv(_('Error'), _('Employee must have an associated location !'))
        if not obj_id.employee_id.company_id:
            raise osv.except_osv(_('Error'), _('Employee must have an associated company !'))
        if not obj_id.employee_id.company_id.partner_id.property_stock_customer or obj_id.employee_id.company_id.partner_id.property_stock_customer.usage != 'customer':
            raise osv.except_osv(_('Error'), _('Company must have set an output customer location in its partner form !'))
        if not obj_id.service_picking_id.analytic_acc_id:
            raise osv.except_osv(_('Error'), _('It should cover the analytical mind. But, you can not target the corresponding movements !'))

        move_id = self.pool.get('stock.move').create(cr, uid, {'product_id': obj_id.product_id.id,
                                                    'product_qty': obj_id.product_qty,
                                                    'product_uom': obj_id.product_id.uom_id.id,
                                                    'origin': obj_id.service_picking_id.analytic_acc_id.name,
                                                    'location_id': obj_id.location_id.id,
                                                    'location_dest_id': obj_id.employee_id.company_id.partner_id.property_stock_customer.id,
                                                    'name': obj_id.service_picking_id.analytic_acc_id.name + u": Out " + obj_id.product_id.name,
                                                    'company_id': obj_id.employee_id.company_id.id,
                                                    'partner_id': obj_id.employee_id.company_id.partner_id.id})

        move_obj = self.pool.get('stock.move').browse(cr, uid, move_id)
        move_obj.action_confirm()
        move_obj.force_assign()
        move_obj.action_done()

        journal_ids = self.pool.get('account.analytic.journal').search(cr, uid, [('name', '=', 'Material')])
        if not journal_ids:
            raise osv.except_osv(_('Error'), _("Cannot find analytic journal 'Material'!"))

        a = obj_id.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = obj_id.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Bad Configuration !'),
                        _('No product and product category expense property account defined on the related product.\nFill these on product form.'))

        self.pool.get('account.analytic.line').create(cr, uid, {
                                                        'amount': -(obj_id.product_id.standard_price * obj_id.product_qty),
                                                        'name': obj_id.service_picking_id.analytic_acc_id.name + u": Out " + obj_id.product_id.name,
                                                        'company_id': obj_id.employee_id.company_id.id,
                                                        'product_id': obj_id.product_id.id,
                                                        'journal_id': journal_ids[0],
                                                        'account_id': obj_id.service_picking_id.analytic_acc_id.id,
                                                        'general_account_id': a
                                                })

        self.write(cr, uid, [id], {'state': 'second', 'move_id': move_id})
        
        return id

    def unlink(self, cr, uid, ids, context=None):
        """Avoid delete an analytic entry"""
        raise osv.except_osv(_('Error !'), _('Cannot delete any record.'))

service_picking_stock_move()
