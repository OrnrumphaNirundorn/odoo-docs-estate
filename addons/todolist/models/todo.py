from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TodoList(models.Model):
    _name = 'todolist'
    _description = 'Todo List'

    name = fields.Char('Title', required=True)
    tags_ids = fields.Many2many('todotags', string='Tags')

    start_date_time = fields.Datetime('Start Date', required=True)
    end_date_time = fields.Datetime('End Date', required=True)

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Complete'),
        ],
        default='draft'
    )

    line_ids = fields.One2many(
        'todolist.line',
        'todolist_id',
        string='Todo Items'
    )

    attendee_ids = fields.One2many(
        'todolist.attendee',
        'todolist_id',
        string='Attendees'
    )

    can_done = fields.Boolean(
        compute='_compute_can_done',
        store=True
    )

    # COMPUTE IS DONE
    @api.depends('line_ids.is_done', 'state')
    def _compute_can_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                rec.can_done = False
            elif not rec.line_ids:
                rec.can_done = False
            else:
                rec.can_done = all(line.is_done for line in rec.line_ids)

    # ACTIONS
    def action_progress(self):
        self.ensure_one()
        self.state = 'in_progress'

    def action_done(self):
        self.ensure_one()
        if not self.can_done:
            raise ValidationError(
                'All todo items must be completed before marking as Done.'
            )
        self.state = 'done'

    # CONSTRAINTS
    @api.constrains('start_date_time', 'end_date_time')
    def _check_date(self):
        for rec in self:
            if rec.start_date_time and rec.end_date_time:
                if rec.start_date_time > rec.end_date_time:
                    raise ValidationError(
                        'Start date must be earlier than end date.'
                    )

#TODO TAGS
class TodoTags(models.Model):
    _name = 'todotags'
    _description = 'Todo Tags'

    name = fields.Char(required=True)

#TODO LINE
class TodoLine(models.Model):
    _name = 'todolist.line'
    _description = 'Todo Line'

    todolist_id = fields.Many2one(
        'todolist',
        ondelete='cascade',
        required=True
    )

    parent_state = fields.Selection(
        related='todolist_id.state',
        store=True
    )

    name = fields.Char('Task', required=True)
    description = fields.Char('Description')
    is_done = fields.Boolean('Is Complete')


#TODO ATTENDEE
class TodoAttendee(models.Model):
    _name = 'todolist.attendee'
    _description = 'Todo Attendee'

    todolist_id = fields.Many2one(
        'todolist',
        ondelete='cascade',
        required=True
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True
    )
