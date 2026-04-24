from abc import ABC
from inspect import getfullargspec, FullArgSpec
from typing import List, Callable, Awaitable

from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery

from app.bot.actions.back import BackAction
from app.bot.actions.switch_scene import SwitchSceneAction


class BaseScene(Scene, ABC, state="base"):
    async def on_back(
            self,
            **kwargs
    ) -> None:
        await self.wizard.back(**kwargs)

    async def on_switch_scene(
            self,
            callback_data: SwitchSceneAction,
            **kwargs
    ) -> None:
        await self.wizard.goto(callback_data.scene, **kwargs)

    async def on_scene_leave(
            self,
            **kwargs
    ) -> None:
        pass

    @on.callback_query(BackAction.filter())
    async def __on_back(
            self,
            callback_query: CallbackQuery,
            **kwargs
    ) -> None:
        if await self.wizard.state.get_state() != "start":
            await self._prepare_coroutine(
                self.on_back,
                **kwargs
            )

    @on.callback_query(SwitchSceneAction.filter())
    async def __on_switch_scene(
            self,
            callback_query: CallbackQuery,
            callback_data: SwitchSceneAction,
            **kwargs
    ) -> None:
        await self._prepare_coroutine(
            self.on_switch_scene,
            callback_data=callback_data,
            **kwargs
        )

    @on.callback_query.leave()
    async def __on_scene_leave(
            self,
            callback_query: CallbackQuery,
            **kwargs
    ) -> None:
        await self._prepare_coroutine(
            self.on_scene_leave,
            **kwargs
        )

    @staticmethod
    def _prepare_coroutine(
            coroutine: Callable[..., Awaitable[None]],
            **kwargs
    ) -> Awaitable[None]:
        """
        Create a coroutine and insert only available arguments to avoid exceptions.

        :param coroutine: Coroutine callable to create.
        :param kwargs: Additional arguments for passing to coroutine.
        :return: Awaitable coroutine.
        """

        arg_spec: FullArgSpec = getfullargspec(coroutine)

        args: List[str] = arg_spec.args

        if arg_spec.varkw is None:
            kwargs = {
                k: arg for k, arg in kwargs.items()
                if k in args
            }

        return coroutine(**kwargs)
