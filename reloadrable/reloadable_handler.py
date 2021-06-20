from abc import ABCMeta, abstractmethod


class ReloadableHandler(metaclass=ABCMeta):
    """
    Base class of handler for reloading.
    """

    @abstractmethod
    def on_reloaded(self, target):
        """
        Called when a reloadable object is reloaded.

        Args:
            target (object): reloaded class or function.
        """
        pass
