import comfy.samplers

class ComfygSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_choice": (["SDXL", "Illustrious"],),
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

    CONFIGS = {
        "SDXL": {"steps": 30, "cfg": 7.0, "sampler": "dpmpp_2m", "scheduler": "karras"},
        "Illustrious": {"steps": 30, "cfg": 5.0, "sampler": "euler_ancestral", "scheduler": "Exponential"},
    }

    def select_config(self, model_choice, use_custom_input, steps, cfg, sampler, scheduler):
        config = self.CONFIGS.get(model_choice, {})

        if use_custom_input:
            # Use custom input values
            return (steps, cfg, sampler, scheduler)
        else:
            # Use configuration from model_choice
            return (
                config.get("steps", 30),
                config.get("cfg", 7.0),
                config.get("sampler", comfy.samplers.KSampler.SAMPLERS[0]),
                config.get("scheduler", comfy.samplers.KSampler.SCHEDULERS[0])
            )

    def update_widgets(self, model_choice):
        config = self.CONFIGS.get(model_choice, {})
        return {
            "steps": config.get("steps", 30),
            "cfg": config.get("cfg", 7.0),
            "sampler": config.get("sampler", comfy.samplers.KSampler.SAMPLERS[0]),
            "scheduler": config.get("scheduler", comfy.samplers.KSampler.SCHEDULERS[0])
        }

NODE_CLASS_MAPPINGS = {
    "ComfygSwitch": ComfygSwitch
}
