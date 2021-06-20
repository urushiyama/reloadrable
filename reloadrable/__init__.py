"""
Reloadrable: Reloadr + A Bunch of Little Extensions.

Copyright 2021-2021, Yuta Urushiyama,
Copyright 2015-2020, Hugo Herter and the Reloadr contributers.
"""
from typing import Union, Callable, Any

from .reloadable import Reloadable, ReloadableClass, ReloadableFunc
from .reloadable_handler import ReloadableHandler
from .reloadable_manager import ReloadableManager


def reloadr(target) -> Union[ReloadableClass, ReloadableFunc]:
    """
    Decorates class or function to be manually reloaded by code.

    This is for compatibility to Reloadr (required to obey LGPL).
    """
    wrapped_target = Reloadable.wrapped(target)
    return wrapped_target


def autoupdate(target) -> Union[ReloadableClass, ReloadableFunc]:
    """
    Decorates class or function to be periodically reloaded from its source.
    """
    wrapped_target = Reloadable.wrapped(target)
    wrapped_target.start_periodic_update()
    return wrapped_target


def autoupdate_with(*, handler=None, interval=1.0) -> Callable[[Any], Union[ReloadableClass, ReloadableFunc]]:
    """
    Decorates class or function with adding specific parameters
    to be periodically reloaded from its source.

    Args:
        handler (Optional[ReloadableHandler]): an event handler instance which handles a callback on reload.
        interval (Optional[float]): intervals between periodical update in second.

    Return:
        a decorator function to wrap class or function.
    """
    def _autoupdate(target):
        wrapped_target = Reloadable.wrapped(target)
        wrapped_target.start_periodic_update(interval=interval)
        wrapped_target.set_handler(handler)
        return wrapped_target

    return _autoupdate


def autoreload(target) -> Union[ReloadableClass, ReloadableFunc]:
    """
    Decorates class or function to be reloaded on the file modification from its source.
    """
    wrapped_target = Reloadable.wrapped(target)
    wrapped_target.start_on_modified_update()
    return wrapped_target


def autoreload_with(*, handler=None, file_path=None) -> Callable[[Any], Union[ReloadableClass, ReloadableFunc]]:
    """
    Decorates class or function with adding specific parameters
    to be reloaded on the file modification from its source.

    Args:
        handler (Optional[ReloadableHandler]): an event handler instance which handles a callback on reload.
        file_path (Union[str, Path, None]): a file path to be observed.

    Return:
        a decorator function to wrap class or function.
    """
    def _autoreload(target):
        wrapped_target = Reloadable.wrapped(target)
        wrapped_target.start_on_modified_update()
        wrapped_target.set_handler(handler)
        wrapped_target.set_file_path(file_path)
        return wrapped_target

    return _autoreload
