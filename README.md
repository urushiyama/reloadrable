# Reloadrable

> Reloadr + A Bunch of Little Extensions.
> 

[Reloadr](https://github.com/hoh/reloadr) is a great tool to hot-reload Python code.

This library is based on Reloadr, with a bunch of little extensions added.

## List of added features

- Made some functions to be public to suppress IDE's warning
- Ways to stop periodical reloads and to stop reloads on file modifications
- Decorators for periodical reloading.
- Added decorators to set an event handler instance that handles a callback on reload and to set a file path to be observed for reloading the target.
- Added logging.

## Usage

### Add auto-reloading on file modification

You can decorate the target with `@autoreload` just like Reloadr.

```python
from reloadrable import autoreload

@autoreload
def target_function(a, b):
    return a + b

@autoreload
class TargetClass:
    def __init__(self):
        print("Target class is created.")
```

### Add periodic reloading

You can decorate the target with `@autoupdate` instead of `@autoreload`.

```python
from reloadrable import autoupdate, ReloadableHandler

@autoupdate
def target_function(a, b):
    return a + b

@autoupdate
class TargetClass:
    def __init__(self):
        print("Target class is created.")
```

### Add auto-reloading on file modification with specific settings

You can use `@autoreload_with` to set an event handler and/or a file path to be observed.

```python
from reloadrable import autoreload_with, ReloadableHandler

class FuncReloadingHandler(ReloadableHandler):
    def on_reloaded(self, target):
        print(f"{str(target)} reloaded")

@autoreload_with(handler=FuncReloadingHandler())
def target_function(a, b):
    return a + b

@autoreload_with(file_path="/path/to/be/observed")
class TargetClass:
    def __init__(self):
        print("Target class is created.")
```

### Add periodic reloading with specific settings

You can use `@autoupdate_with` to set an event handler and/or the interval between periodic reloading. 

```python
from reloadrable import autoupdate_with, ReloadableHandler

class FuncReloadingHandler(ReloadableHandler):
    def on_reloaded(self, target):
        print(f"{str(target)} reloaded")

@autoupdate_with(handler=FuncReloadingHandler())
def target_function(a, b):
    return a + b

@autoupdate_with(interval=1.5)
class TargetClass:
    def __init__(self):
        print("Target class is created.")
```

### Manually reload the target

You can manually reload the target just like Reloadr.  
Besides, you can manually control reloading without warnings in IDEs. 

```python
from pathlib import Path
from reloadrable import reloadr, ReloadableHandler

@reloadr
class Gear:
    def shift(self):
        print("Rattling")

# Manual reload (just like Reloadr)
Gear._reload()

# Manual reload (without warning in IDEs)
Gear.reload()

# Start auto-reloading on file modification (just like Reloadr)
Gear._start_watch_reload()

# Start auto-reloading on file modification (without warning in IDEs)
Gear.start_on_modified_update()

# Start periodic reloading (just like Reloadr)
Gear._start_timer_reload(1)

# Start periodic reloading (without warning in IDEs)
Gear.start_periodic_update(interval=1)

# Add an event handler
class GearReloadingHandler(ReloadableHandler):
    def on_reloaded(self, target):
        if isinstance(target, Gear):
            target.shift()

Gear.set_handler(handler=GearReloadingHandler())

# Add a file path to be observed for reloading the target
Gear.set_file_path(file_path="/path/to/be/observed")
# You can use pathlib.Path as well as str
Gear.set_file_path(file_path=Path("/path/to/be/observed"))
```

### Manage auto-reloading and observing

You can use `ReloadableManager` to stop periodical reloads and to stop reloads on file modifications.

```python
from reloadrable import ReloadableManager

# Stop all periodical reloads
ReloadableManager.stop_periodic_updates()

# Stop all observations of file modification.
ReloadableManager.stop_on_modified_updates()
```

## License & copyright notice

This library is based on [Reloadr](https://github.com/hoh/reloadr).

### Reloadr

Copyright 2015-2020, Hugo Herter and the Reloadr contributors.

Reloadr is licensed under the GNU Lesser General Public License v3.0.

### Reloadrable

Copyright 2021-2021, Yuta Urushiyama,  
Copyright 2015-2020, Hugo Herter and the Reloadr contributors.

Reloadrable is licensed under the same license as Reloadr.

## Misc

- Back-porting is welcome for me. I made this just because I need it for my personal work as soon as possible.
