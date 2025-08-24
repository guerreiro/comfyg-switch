from .ComfygSwitch import ComfygSwitch 
NODE_CLASS_MAPPINGS = { "ComfygSwitch" : ComfygSwitch }
NODE_DISPLAY_NAME_MAPPINGS = { "ComfygSwitch" : "Comfyg Switch" }
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

from pathlib import Path
WEB_DIRECTORY = str((Path(__file__).parent / "web").absolute())