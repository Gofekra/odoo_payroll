# -*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
#    Copyright (C) 2015 Savoir-faire Linux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    """Salary Rule"""

    _name = 'hr.salary.rule'
    _description = _(__doc__)

    name = fields.Char(
        'Name', required=True, readonly=False
    )
    code = fields.Char(
        'Code',
        size=64,
        required=True,
        help="The code of salary rules can be used as reference in "
        "computation of other rules. In that case, it is case sensitive."
    )
    sequence = fields.Integer(
        'Sequence',
        required=True,
        help='Use to arrange calculation sequence',
        select=True,
        default=5,
    )
    category_id = fields.Many2one(
        'hr.salary.rule.category',
        'Category',
        required=True
    )
    active = fields.Boolean(
        'Active',
        help="If the active field is set to false, it will allow "
        "you to hide the salary rule without removing it.",
        default=True,
    )
    appears_on_payslip = fields.Boolean(
        'Appears on Payslip',
        help="Used to display the salary rule on payslip.",
        default=True,
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=False,
        default=lambda self: self.env.user.company_id.id,
    )
    condition_select = fields.Selection(
        [
            ('none', 'Always True'),
            ('python', 'Python Expression'),
        ],
        "Condition Based on",
        required=True,
        default='none',
    )
    condition_python = fields.Text(
        'Python Condition',
        required=True,
        readonly=False,
        help="Applied this rule for calculation if condition is true. "
        "You can specify condition like basic > 1000.",
        default=' ',
    )
    amount_python_compute = fields.Text(
        'Python Code',
        required=True,
        default=' ',
    )
    note = fields.Text(
        'Description',
    )

    @api.multi
    def compute_rule(self, localdict):
        """
        :param localdict: dictionary containing the environement in which to
        compute the rule
        :return: returns a tuple build as the base/amount computed, the
        quantity and the rate
        :rtype: (float, float, float)
        """
        self.ensure_one()

        try:
            safe_eval(
                self.amount_python_compute,
                localdict, mode='exec', nocopy=True
            )
            return float(localdict['result'])
        except Exception:
            raise ValidationError(
                _('Wrong python code defined for salary rule %s (%s).') %
                (self.name, self.code))

    @api.multi
    def satisfy_condition(self, localdict):
        """
        :return: True if the given rule match the condition.
        False otherwise.
        """
        self.ensure_one()

        if self.condition_select == 'none':
            return True

        else:
            try:
                eval(
                    self.condition_python,
                    localdict, mode='exec', nocopy=True
                )
                return localdict.get('result', False)
            except:
                raise ValidationError(
                    _('Wrong python condition defined for salary '
                      'rule %s (%s).') %
                    (self.name, self.code))
