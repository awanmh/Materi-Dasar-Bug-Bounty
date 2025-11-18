import os
import importlib
import inspect
from core.plugin_base import BasePlugin

def load_plugins():
    plugins_dir = "plugins"
    loaded_plugins = {"phase1": [], "phase2_dom": []}

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"plugins.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if issubclass(cls, BasePlugin) and cls is not BasePlugin:
                        plugin_instance = cls()
                        if plugin_instance.PHASE == "phase1":
                            loaded_plugins["phase1"].append(plugin_instance)
                        elif plugin_instance.PHASE == "phase2_dom":
                            loaded_plugins["phase2_dom"].append(plugin_instance)
            except Exception as e:
                print(f"[!] Gagal memuat plugin {module_name}: {e}")
    return loaded_plugins