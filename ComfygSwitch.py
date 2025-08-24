import comfy.samplers
import folder_paths
import json
import os
import re
import fnmatch
from pathlib import Path
from typing import Any, Dict

class AlwaysComparisonReturn(str):
    def __eq__(self, other: object) -> bool:
        return True
    def __ne__(self, other: object) -> bool:
        return False
    def __repr__(self) -> str:
        return "<AlwaysComparisonReturn>"


class ComfygSwitch:
    _configs: Dict[str, Any] = {}
    _config_mtime: float = 0.0
    _debug: bool = False  # Set True for debug prints

    GLOBAL_KEY = "__default__"
    DEFAULT_CONFIG_FILE = Path(__file__).parent / "model_configs.json"
    USER_CONFIG_FILE = Path(__file__).parent / "my_model_configs.json"  # Optional

    @classmethod
    def _log(cls, *args):
        if cls._debug:
            print("ComfygSwitch ->", *args)

    @classmethod
    def read_json(cls, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic fix: remove trailing commas before } or ]
            content_fixed = re.sub(r",(\s*[}\]])", r"\1", content)

            try:
                return json.loads(content_fixed)
            except json.JSONDecodeError as e:
                cls._log(f"JSON decode error after fix attempt in {path}:\n  {e}")
                # Try original content for raw error
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e2:
                    cls._log(f"JSON decode error in {path}:\n  {e2}")
                    print(f"[ComfygSwitch] ERROR: Invalid JSON format in '{path}'. Please check the file.")
                    return {}
        except Exception as e:
            cls._log(f"Error loading {path}: {e}")
            print(f"[ComfygSwitch] ERROR: Failed to read '{path}': {e}")
            return {}

    @classmethod
    def load_configs(cls) -> Dict[str, Any]:
        mtime = sum(p.stat().st_mtime for p in [cls.DEFAULT_CONFIG_FILE, cls.USER_CONFIG_FILE] if p.exists())
        if cls._configs and mtime == cls._config_mtime:
            return cls._configs

        default_config = cls.read_json(cls.DEFAULT_CONFIG_FILE)
        user_config = cls.read_json(cls.USER_CONFIG_FILE)

        merged_config = cls.deep_merge(default_config, user_config)

        cls._configs = merged_config
        cls._config_mtime = mtime
        cls._log("Loaded merged config:", merged_config)
        return cls._configs

    @staticmethod
    def deep_merge(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dicts:
        - For each key in overrides, replace or merge into defaults.
        - Supports nested dicts.
        """
        result = dict(defaults)  # copy
        for key, value in overrides.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ComfygSwitch.deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @classmethod
    def get_config_for_model(cls, model: str) -> tuple[Dict[str, Any], str, str]:
        """
        Returns (config_dict, config_name, model_choice):
        - config_dict = dict of config values
        - config_name = key that matched (exact, wildcard, or __default__)
        - model_choice = checkpoint basename
        """
        import fnmatch

        configs = cls.load_configs()
        model_choice = cls.get_last_path_segment(model)

        # 1️⃣ Exact match
        if model_choice in configs and configs[model_choice]:
            return configs[model_choice], model_choice, model_choice

        # 2️⃣ Wildcard patterns
        for pattern, cfg in configs.items():
            if pattern == cls.GLOBAL_KEY:
                continue
            if fnmatch.fnmatch(model_choice, pattern) and cfg:
                return cfg, pattern, model_choice

        # 3️⃣ Global fallback
        return configs.get(cls.GLOBAL_KEY, {}), cls.GLOBAL_KEY, model_choice

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint_model": (sorted(folder_paths.get_filename_list("checkpoints")),),
                "config_source": ("STRING", {"default": "(auto)", "multiline": False}),
                "steps": ("INT", {"default": 30, "min": 1, "max": 200}),
                "refiner_steps": ("INT", {"default": 30, "min": 1, "max": 200}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.1, "max": 20.0, "step": 0.1}),
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            }
        }

    RETURN_TYPES = (
        AlwaysComparisonReturn(),
        "STRING",
        "INT",
        "INT",
        "FLOAT",
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS,
    )
    RETURN_NAMES = ("MODEL_NAME", "CONFIG_SOURCE", "STEPS", "REFINE_STEPS", "CFG", "SAMPLER", "SCHEDULER")
    FUNCTION = "select_config"
    CATEGORY = "Configuration"

    def select_config(self, checkpoint_model, config_source, steps, refiner_steps, cfg, sampler, scheduler):
        config, config_name, model_choice = self.get_config_for_model(checkpoint_model)

        self._log(f"Model choice={model_choice}, using config={config_name}")

        final_config = self.merge_defaults(
            {
                "steps": steps,
                "refiner_steps": refiner_steps,
                "cfg": cfg,
                "sampler": sampler,
                "scheduler": scheduler,
            },
            config,
        )

        return (
            checkpoint_model,
            config_source,
            final_config["steps"],
            final_config["refiner_steps"],
            final_config["cfg"],
            final_config["sampler"],
            final_config["scheduler"],
        )

    @staticmethod
    def merge_defaults(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        return {**defaults, **overrides}

    @staticmethod
    def get_last_path_segment(path: str) -> str:
        if not isinstance(path, str) or not path.strip():
            return ""
        return Path(path.strip()).stem


# NEW: tiny API to fetch a model's final config
try:
    from server import PromptServer
    from aiohttp import web
except Exception:
    PromptServer = None
    web = None

if PromptServer and web:
    @PromptServer.instance.routes.get("/comfyg-switch/config")
    async def get_config(request):
        model = request.query.get("model", "")
        config, config_name, model_choice = ComfygSwitch.get_config_for_model(model)

        return web.json_response({
            "config": config,
            "config_name": config_name,
            "model_choice": model_choice,
        })

NODE_CLASS_MAPPINGS = {
    "ComfygSwitch": ComfygSwitch
}
