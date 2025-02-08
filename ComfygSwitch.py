import comfy.samplers
import folder_paths
import json
import os

class ComfygSwitch:
    @classmethod
    def load_configs(cls):
        """
        Load configuration options from a JSON file and return sorted keys.
        """
        if not hasattr(cls, '_configs'):
            config_path = os.path.join(os.path.dirname(__file__), "model_configs.json")
            try:
                with open(config_path, "r") as f:
                    cls._configs = json.load(f)
            except Exception as e:
                print('ComfygSwitch -> Exception', e)
                cls._configs = {}
        return cls._configs

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "checkpoint_model": (sorted(folder_paths.get_filename_list("checkpoints")),),
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

    def select_config(self, checkpoint_model, use_custom_input, steps, cfg, sampler, scheduler):
        """
        If use_custom_input is True, output the manually entered values.
        Otherwise, load the configuration corresponding to the selected model_choice.
        """
        configs = self.load_configs()
        model_choice = self.get_last_path_segment(checkpoint_model)
        config = configs.get(model_choice, {})
        print('ComfygSwitch -> model_choice', model_choice)

        # Define a default configuration.
        default_config = {
            "steps": steps,
            "cfg": cfg,
            "sampler": sampler,
            "scheduler": scheduler
        }
        final_config = {**default_config, **config}

        if use_custom_input:
            return (steps, cfg, sampler, scheduler)
        else:
            return (
                final_config["steps"],
                final_config["cfg"],
                final_config["sampler"],
                final_config["scheduler"]
            )

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
