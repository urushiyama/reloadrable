from __future__ import annotations

from logging import getLogger, NullHandler
from typing import TYPE_CHECKING, List, Dict, Tuple

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

if TYPE_CHECKING:
    from . import Reloadable


logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ReloadableManager:
    """
    Management class for auto-reload.

    This class provides a way to stop threads and observers for reloading.
    """

    thread_list: List[Reloadable.AutoupdateThread] = list()
    observer_dict: Dict[str, Tuple[Observer, ObservedWatch]] = dict()

    @classmethod
    def stop_periodic_updates(cls):
        """
        Stops all periodic reloading.
        """
        for thread in cls.thread_list:
            thread.stopping.set()
        cls.thread_list.clear()
        logger.info(f"all periodic reloading are stopped.")

    @classmethod
    def stop_on_modified_updates(cls):
        """
        Stops all reloading on the file modification.
        """
        for observer, _ in cls.observer_dict.values():
            observer.stop()
            observer.join()
        cls.observer_dict.clear()
        logger.info(f"all reloading on the file modification are stopped.")
