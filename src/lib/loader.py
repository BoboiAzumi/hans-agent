import sys
import importlib.util
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"

def plugin_load():
    plugins = {}

    for plugin_dir in PLUGINS_DIR.iterdir():
        if not plugin_dir.is_dir():
            continue

        setup_file = plugin_dir / "setup.py"

        if not setup_file.exists():
            continue

        module_name = plugin_dir.name

        spec = importlib.util.spec_from_file_location(
                module_name,
                setup_file
        )

        if spec is None or spec.loader is None:
                continue

        module = importlib.util.module_from_spec(spec)

        sys.path.insert(0, str(plugin_dir))
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[warn] plugin '{module_name}' failed to load, skipped: {e}")
            continue

        plugins[plugin_dir.name] = module.plugin

    return plugins
