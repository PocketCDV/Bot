import asyncio
from datetime import date
from typing import Sequence, Mapping, Set, Dict

from sqlalchemy import select

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.database import DatabaseController
from app.assets.models.records.raw_class_record import RawClassRecord
from app.assets.models.records.class_record import ClassRecord
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.assets.models.records.schedule_record import ScheduleRecord
from app.utils import today_local
from app.assets.models.database import Room, Teacher


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
    ) -> DailyScheduleRecord:
        """
        Retrieves today's schedule for the home page. Returns a DailyScheduleRecord for the current date.
        :param session_id: WU session ID.
        :return: DailyScheduleRecord for the current date.
        """

        schedule_date: date = today_local()

        raw_class_records: Sequence[RawClassRecord] = await self._cdv.get_schedule(
            session_id,
            schedule_date,
            schedule_date,
        )

        room_names: Mapping[int, str] = await self._fetch_room_names(raw_class_records)
        teacher_names: Mapping[int, str] = await self._fetch_teacher_names(raw_class_records, session_id)

        return DailyScheduleRecord(
            class_records=[
                ClassRecord.from_entry(raw_class_record, room_names, teacher_names)
                for raw_class_record in raw_class_records
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

        raw_class_records: Sequence[RawClassRecord] = await self._cdv.get_schedule(
            session_id,
            start_date,
            end_date,
        )

        room_names: Mapping[int, str] = await self._fetch_room_names(raw_class_records)
        teacher_names: Mapping[int, str] = await self._fetch_teacher_names(raw_class_records, session_id)

        schedule: ScheduleRecord = ScheduleRecord()

        for raw_class_record in raw_class_records:
            entry_date = raw_class_record.start_time.date()

            if entry_date not in schedule.schedule:
                schedule.schedule[entry_date] = DailyScheduleRecord()

            schedule.schedule[entry_date].class_records.append(
                ClassRecord.from_entry(raw_class_record, room_names, teacher_names)
            )

        return schedule

    async def _fetch_room_names(
            self,
            raw_class_records: Sequence[RawClassRecord],
    ) -> Mapping[int, str]:
        """
        Fetches room names from database using all room IDs from a sequence of class entries,
        and creates a mapping of existent room ID, and it's name.
        :param raw_class_records: Sequence of class entries.
        :return: Mapping of room IDs to room names.
        """

        room_ids: Set[int] = {raw_class_record.room_id for raw_class_record in raw_class_records}

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

    async def _fetch_teacher_names(
            self,
            raw_class_records: Sequence[RawClassRecord],
            session_id: str,
    ) -> Mapping[int, str]:
        """
        Fetches teacher names from database using all teacher IDs from a sequence of class entries.
        If a teacher is not found in the database, falls back to fetching from remote API.
        Teachers that could not be fetched from either source are excluded from the mapping.
        :param raw_class_records: Sequence of class entries.
        :param session_id: WU session ID.
        :return: Mapping of teacher IDs to teacher names.
        """

        teacher_ids: Set[int] = {raw_class_record.teacher_id for raw_class_record in raw_class_records}

        async with self._database.session() as database_session:
            rows = (
                await database_session.execute(
                    select(Teacher.id, Teacher.full_name)
                    .filter(Teacher.id.in_(teacher_ids))
                )
            ).all()

        result: Dict[int, str] = {row.id: row.full_name for row in rows}

        missing_ids: Set[int] = teacher_ids - result.keys()

        if missing_ids:
            fetched: Sequence[str | None] = await asyncio.gather(
                *[
                    self._cdv.get_teacher_full_name(session_id, teacher_id)
                    for teacher_id in missing_ids
                ]
            )

            fetched_teachers: Dict[int, str] = {
                teacher_id: full_name
                for teacher_id, full_name in zip(missing_ids, fetched)
                if full_name is not None
            }

            if fetched_teachers:
                async with self._database.session() as database_session:
                    database_session.add_all(
                        [
                            Teacher(id=teacher_id, full_name=full_name)
                            for teacher_id, full_name in fetched_teachers.items()
                        ]
                    )
                    await database_session.commit()

            result.update(fetched_teachers)

        return result
