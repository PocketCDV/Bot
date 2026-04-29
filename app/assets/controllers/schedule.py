from datetime import date, datetime, timezone
from typing import Sequence, Mapping, Set

from sqlalchemy import select

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.database import DatabaseController
from app.assets.models.class_entry import ClassEntry
from app.assets.models.class_record import ClassRecord
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.assets.models.schedule_record import ScheduleRecord
from app.database.models import Room


class ScheduleController:
    """
    An abstraction above CDVController and DatabaseController for retrieving
    schedule information as organized records.
    """

    def __init__(
            self,
            cdv: CDVController,
            database: DatabaseController,
    ) -> None:
        """
        ScheduleController Constructor.
        :param cdv: CDVController instance.
        :param database: DatabaseController instance.
        """

        self._cdv: CDVController = cdv
        self._database: DatabaseController = database

    async def get_home_schedule(
            self,
            session_id: str,
    ) -> ScheduleDayRecord:
        """
        Retrieves today's schedule for the home page. Returns a ScheduleDayRecord for the current date.
        :param session_id: WU session ID.
        :return: ScheduleDayRecord for the current date.
        """

        schedule_date: date = datetime.now(timezone.utc).date()

        class_entries: Sequence[ClassEntry] = await self._cdv.get_schedule(
            session_id,
            schedule_date,
            schedule_date,
        )

        room_names: Mapping[int, str] = await self._fetch_room_names(class_entries)

        return ScheduleDayRecord(
            class_records=[
                ClassRecord(
                    title=class_entry.title,
                    start_time=class_entry.start_time,
                    end_time=class_entry.end_time,
                    room_name=room_names.get(class_entry.room, "Unknown room"),
                    online_meeting_url=class_entry.hangout_link,
                )
                for class_entry in class_entries
            ]
        )

    async def get_schedule(
            self,
            start_date: date,
            end_date: date,
            session_id: str,
    ) -> ScheduleRecord:
        """
        Retrieves a schedule for a specific range of dates. Returns a ScheduleRecord for the selected date range.
        :param start_date: Start date for the schedule.
        :param end_date: End date for the schedule.
        :param session_id: WU session ID.
        :return: ScheduleRecord for the selected date range.
        """

        class_entries: Sequence[ClassEntry] = await self._cdv.get_schedule(
            session_id,
            start_date,
            end_date,
        )

        room_names: Mapping[int, str] = await self._fetch_room_names(class_entries)

        schedule: ScheduleRecord = ScheduleRecord()

        for class_entry in class_entries:
            entry_date = class_entry.start_time.date()

            if entry_date not in schedule.schedule:
                schedule.schedule[entry_date] = ScheduleDayRecord()

            schedule.schedule[entry_date].class_records.append(
                ClassRecord(
                    title=class_entry.title,
                    start_time=class_entry.start_time,
                    end_time=class_entry.end_time,
                    room_name=room_names.get(class_entry.room, "Unknown room"),
                    online_meeting_url=class_entry.hangout_link,
                )
            )

        return schedule

    async def _fetch_room_names(
            self,
            class_entries: Sequence[ClassEntry],
    ) -> Mapping[int, str]:
        """
        Fetches room names from database using all room IDs from a sequence of class entries,
        and creates a mapping of existent room ID, and it's name.
        :param class_entries: Sequence of class entries.
        :return: Mapping of room IDs to room names.
        """

        room_ids: Set[int] = {class_entry.room for class_entry in class_entries}

        async with self._database.session() as database_session:
            return {
                row.id: row.name
                for row in (
                    await database_session.execute(
                        select(Room.id, Room.name)
                        .filter(Room.id.in_(room_ids))
                    )
                ).all()
            }
