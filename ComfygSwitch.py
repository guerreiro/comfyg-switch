import comfy.samplers
import json
import os

class ComfygSwitch:
    @classmethod
    def load_configs(cls):
        """
        Load configuration options from a JSON file.
        The file is assumed to be named 'configs.json' and located in the same directory.
        Caches the result in the class attribute _configs.
        """
        if not hasattr(cls, '_configs'):
            config_path = os.path.join(os.path.dirname(__file__), "model_configs.json")
            try:
                with open(config_path, "r") as f:
                    cls._configs = json.load(f)
            except Exception as e:
                # If loading fails, fall back to an empty dict.
                cls._configs = {}
        return cls._configs

    @classmethod
    def INPUT_TYPES(cls):
        # Load the configs so that the dropdown options reflect available keys
        configs = cls.load_configs()
        # If there are no keys, provide a default option
        model_options = list(configs.keys()) if configs else ["SDXL", "Illustrious"]
        return {
            "required": {
                "model_choice": (model_options, ),
                "use_custom_input": ("BOOLEAN", {"default": False}),
                "steps": ("INT", {"default": 30, "min": 1, "max": 200}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.1, "max": 20.0, "step": 0.1}),
                "sampler": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
            }
        }

    RETURN_TYPES = (
        "INT",
        "FLOAT",
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS
    )
    RETURN_NAMES = ("STEPS", "CFG", "SAMPLER", "SCHEDULER")
    FUNCTION = "select_config"
    CATEGORY = "Configuration"

    def select_config(self, model_choice, use_custom_input, steps, cfg, sampler, scheduler):
        """
        If use_custom_input is True, output the manually entered values.
        Otherwise, load the configuration corresponding to the selected model_choice.
        """
        configs = self.load_configs()
        model_choice = self.get_last_path_segment(model_choice)
        config = configs.get(model_choice, {})
        if use_custom_input:
            return (steps, cfg, sampler, scheduler)
        else:
            return ( 
                config.get("steps", 30),
                config.get("cfg", 7.0),
                config.get("sampler", comfy.samplers.KSampler.SAMPLERS[0]),
                config.get("scheduler", comfy.samplers.KSampler.SCHEDULERS[0])
            )

    def update_widgets(self, model_choice):
        """
        Callback triggered when the dropdown value changes.
        Returns new default values for steps, cfg, sampler, and scheduler based on the selected config.
        """
        configs = self.load_configs()
        config = configs.get(model_choice, {})
        return {
            "steps": config.get("steps", 30),
            "cfg": config.get("cfg", 7.0),
            "sampler": config.get("sampler", comfy.samplers.KSampler.SAMPLERS[0]),
            "scheduler": config.get("scheduler", comfy.samplers.KSampler.SCHEDULERS[0])
        }

    @classmethod
    def get_last_path_segment(self, path: str) -> str:
        if not isinstance(path, str) or not path.strip():
            return ""
        last_segment = os.path.basename(path.strip().replace("\\", "/"))
        title, _ = os.path.splitext(last_segment)  # Remove the extension
        return title

NODE_CLASS_MAPPINGS = {
    "ComfygSwitch": ComfygSwitch
}
