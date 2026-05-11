import asyncio
import sys
from ssl import create_default_context, SSLContext
from typing import Any

from aiohttp import ClientSession
from certifi import where
from sqlalchemy.dialects.postgresql import insert

from app.assets.controllers.database import DatabaseController
from app.assets.models.database import Room
from config import config

SSL_CONTEXT: SSLContext = create_default_context(cafile=where())
SESSION_ID: str = input("Enter your WU_PHPSESSID: ").strip()


async def fetch_room(
        session: ClientSession,
        room: int,
) -> str:
    """
    Fetches a single room name from WU.
    :param session: WU session ID.
    :param room: Room id.
    :return: Room name.
    """

    async with session.post(
            "https://wu.cdv.pl/ajax.php",
            params={"action": "get-classes-term-details-for-student"},
            data={
                "room_id": room,
                "teacher_id": 0,
                "term_id": 0,
                "group_id": 0,
            },
            cookies={"WU_PHPSESSID": SESSION_ID},
            ssl=SSL_CONTEXT,
    ) as response:
        return (await response.json())["return"]["room"]["nazwaSali"]


async def main() -> None:
    initial_room: int = 1
    step: int = 50
    unknown_room_tail_amount: int = 10

    all_rooms: dict[int, str] = {}

    async with ClientSession() as session:
        while True:
            rg = range(initial_room, initial_room + step)

            rooms: tuple[Any] = await asyncio.gather(
                *[fetch_room(session, room) for room in rg],
                return_exceptions=True,
            )

            all_rooms.update(zip(rg, rooms))

            if all([isinstance(room, str) for room in rooms]):
                print(f"Fetched {len(all_rooms)} rooms: {rooms}.")
            else:
                raise Exception(f"CDV refused to give 200 room names in 10 seconds: {rooms}.")

            last_entries: list[str] = list(all_rooms.values())[-unknown_room_tail_amount:]

            if all(item.lower() == "unknown room" for item in last_entries):
                a: str = input("Fetched all rooms. Update DB? (y / n): ").strip().lower()

                if a not in ["y", "yes"]:
                    raise Exception("k fine.")

                filtered_rooms: dict[int, str] = {k: v for k, v in all_rooms.items() if v.lower() != "unknown room"}

                database: DatabaseController = DatabaseController.from_dsn(
                    config.database_dsn.get_secret_value(),
                )

                async with database.session() as database_session:
                    await database_session.execute(
                        insert(Room).values(
                            [
                                {"id": room_id, "name": name}
                                for room_id, name in filtered_rooms.items()
                            ]
                        ).on_conflict_do_update(
                            index_elements=["id"],
                            set_={"name": insert(Room).excluded.name}
                        )
                    )
                    await database_session.commit()

                print("Done.")
                return

            initial_room += step


if __name__ == "__main__":
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())
