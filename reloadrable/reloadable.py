from __future__ import annotations

import inspect
import re
import threading
import types
import weakref
from os.path import abspath, dirname
from pathlib import Path
from time import sleep
from typing import Optional, Union
from logging import getLogger, NullHandler

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

from .reloadable_handler import ReloadableHandler
from .reloadable_manager import ReloadableManager


logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Reloadable:
    """
    Base class of reloadable object wrapper.
    """
    class AutoupdateThread(threading.Thread):
        """
        Stoppable thread for periodic updating.
        """
        def __init__(self, reloadable: Reloadable, interval=1.0):
            """
            Initialize the instance with a reloadable object wrapper and other parameters.

            Args:
                reloadable (Reloadable): a reloadable object wrapper to update periodically.
                interval (float): intervals between periodical update in second.
            """
            super().__init__(group=None)
            self.stopping = threading.Event()
            self.reloadable = reloadable
            self.interval = interval

        def run(self) -> None:
            """
            Implementation of periodic reloading.
            """
            while not self.stopping.isSet():
                self.reloadable.reload()
                sleep(self.interval)

    def __init__(self, target):
        """
        Initialize the instance with a target class or function to be reloaded.

        Args:
            target (Any): the target to be wrapped by a reloadable object wrapper.
        """
        self.target = target
        self.handler: Optional[ReloadableHandler] = None
        self.file_path: Optional[str] = None

    def __call__(self, *args, **kwargs):
        """
        Proxy function call to the target.

        Args:
            args (Any): positional arguments to be used by the original function call.
            kwargs (Any): keyword arguments to be used by the original function call.
        """
        return self.target.__call__(*args, **kwargs)

    def __getattr__(self, item):
        """
        Proxy inspection to the target.

        Args:
            item (Any): inspected item.
        """
        return self.target.__getattr__(item)

    @classmethod
    def wrapped(cls, target):
        """
        Wraps the target by a suitable subclass of reloadable object wrapper.

        Args:
            target (Any): the target to be wrapped by a reloadable object wrapper.
        """
        if isinstance(target, types.FunctionType):
            return ReloadableFunc(target)
        else:
            return ReloadableClass(target)

    def set_handler(self, handler: Optional[ReloadableHandler]):
        """
        Sets an event handler instance which handles a callback on reload.

        Args:
            handler (ReloadableHandler): an event handler instance.
        """
        if isinstance(handler, ReloadableHandler):
            self.handler = handler

    def set_file_path(self, file_path: Union[str, Path, None]):
        """
        Sets a file path to be observed for reloading.

        Args:
            file_path (Union[str, Path]): a file path to be observed.
        """
        if isinstance(file_path, Path):
            self.file_path = file_path.absolute()
        elif isinstance(file_path, str):
            self.file_path = file_path

    def reload(self):
        """
        Reloads the target from its source file.
        """
        try:
            source = inspect.getsource(self.target)
            # Avoid thread flooding
            source = re.sub(r'@(autoreload|autoupdate)(_with\(.*\))?\n', '', source)

            module = inspect.getmodule(self.target)
            local_env = dict()
            exec(source, module.__dict__, local_env)
            self.target = local_env[self.target.__name__]
        except SyntaxError as e:
            logger.exception(f"{e}")

    def start_periodic_update(self, interval=1.0):
        """
        Starts periodic reloading.

        Args:
            interval (float): intervals between periodical update in second.
        """
        thread = Reloadable.AutoupdateThread(self, interval=interval)
        thread.start()
        ReloadableManager.thread_list.append(thread)

    def start_on_modified_update(self):
        """
        Starts reloading on the file modification.
        """
        observer = Observer()
        if self.file_path is None:
            filepath = inspect.getsourcefile(self.target)
            assert filepath, f"source file for {self.target} is not found"
        else:
            filepath = self.file_path
        filepath = abspath(filepath)
        file_dir = dirname(filepath)

        this = self

        class EventHandler(FileSystemEventHandler):
            """
            Event handler for the observer to watch the file modification.
            """
            def on_modified(self, event: FileModifiedEvent):
                """
                Gets called when the file is modified.

                Args:
                    event (FileModifiedEvent): the event on file modifications.
                """
                if event.is_directory:
                    return
                if event.src_path == filepath:
                    this.reload()

        if file_dir in ReloadableManager.observer_dict:
            # add event handler if the directory is already observed
            observer, observed_watch = ReloadableManager.observer_dict[file_dir]
            observer.add_handler_for_watch(EventHandler(), observed_watch)
        else:
            # create new observer for the directory that contains the target file
            observed_watch = observer.schedule(EventHandler(), file_dir, recursive=False)
            observer.start()
            ReloadableManager.observer_dict[file_dir] = (observer, observed_watch)

    def _reload(self):
        """
        Reloads the target from its source file.

        This is for compatibility to Reloadr (required to obey LGPL).
        """
        self.reload()

    def _start_timer_reload(self, interval=1.0):
        """
        Starts periodic reloading.

        This is for compatibility to Reloadr (required to obey LGPL).

        Args:
            interval (float): intervals between periodical update in second.
        """
        self.start_periodic_update(interval=interval)

    def _start_watch_reload(self):
        """
        Starts reloading on the file modification.

        This is for compatibility to Reloadr (required to obey LGPL).
        """
        self.start_on_modified_update()


class ReloadableFunc(Reloadable):
    """
    Class of reloadable function wrapper.
    """
    def reload(self):
        """
        Reloads the target function from its source file.
        """
        super().reload()
        logger.info(f"{str(self.target)}: code reloaded")
        if self.handler is not None:
            self.handler.on_reloaded(self.target)


class ReloadableClass(Reloadable):
    """
    Class of reloadable class wrapper.
    """
    def __init__(self, target):
        """
        Initialize the instance with a target class to be reloaded.

        Args:
            target (Any): the target class to be wrapped by a reloadable object wrapper.
        """
        super().__init__(target)
        self.instances = list()

    def __call__(self, *args, **kwargs):
        """
        Proxy function call to the target.

        Args:
            args (Any): positional arguments to be used by the original function call.
            kwargs (Any): keyword arguments to be used by the original function call.
        """
        instance = self.target.__call__(*args, **kwargs)
        self.instances.append(weakref.ref(instance))
        return instance

    def reload(self):
        """
        Reloads the target class and its existing instances from its source file.
        """
        super().reload()
        for ref_instance in self.instances:
            instance = ref_instance()
            if instance:
                instance.__class__ = self.target
        logger.info(f"{str(self.target)}: code reloaded")
        if self.handler is not None:
            self.handler.on_reloaded(self.target)
