# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# Copyright 2020 InitOS Gmbh
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.resource.models.resource import Intervals


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _attendance_intervals_batch_exclude_public_holidays(
        self, start_dt, end_dt, intervals, resources, tz
    ):
        list_by_dates = (
            self.env["hr.holidays.public"]
            .get_holidays_list(
                start_dt=start_dt.date(),
                end_dt=end_dt.date(),
                employee_id=self.env.context.get("employee_id", False),
            ))
            # In some cases, an error appears about mixing 2 models
            # (hr.holidays.public.line + resource.calendar.leaves)
            # in _leave_intervals or _leave_intervals_batch functions
            # It only happen when both holidays and leaves exist.
            # The solution is to pass an empty leave in the tuple instead
            # of the public holiday line record, as this element has no
            # further use except the union operation.
            resource_leave_model = self.env["resource.calendar.leaves"]
            for line in lines:
                leaves.append(
                    (
                        datetime.combine(line.date, time.min).replace(tzinfo=tz),
                        datetime.combine(line.date, time.max).replace(tzinfo=tz),
                        resource_leave_model,
                    )
                )
        return Intervals(leaves)

    def _leave_intervals(self, start_dt, end_dt, resource=None, domain=None, tz=None):
        """DEPRECATED since odoo/odoo#51542, but left as is for retro-compatibility"""
        # TODO: To be removed in v14 if not used in any place
        res = super()._leave_intervals(
            start_dt=start_dt, end_dt=end_dt, resource=resource, domain=domain, tz=tz
        )
        for resource in resources:
            interval_resource = intervals[resource.id]
            attendances = []
            for attendance in interval_resource._items:
                if attendance[0].date() not in list_by_dates:
                    attendances.append(attendance)
            intervals[resource.id] = Intervals(attendances)
        return intervals

    def _attendance_intervals_batch(
        self, start_dt, end_dt, resources=None, domain=None, tz=None
    ):
        res = super()._attendance_intervals_batch(
            start_dt=start_dt, end_dt=end_dt, resources=resources, domain=domain, tz=tz
        )
        if self.env.context.get("exclude_public_holidays") and resources:
            return self._attendance_intervals_batch_exclude_public_holidays(
                start_dt, end_dt, res, resources, tz
            )
        return res
