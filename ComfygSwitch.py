import comfy.samplers

class ComfygSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_choice": (["SDXL", "Illustrious"],),
                # "steps": ("INT", {"default": 20, "min": 1, "max": 200}),
                # "cfg": ("FLOAT", {"default": 7.5, "min": 0.1, "max": 20.0, "step": 0.1}),
                # "sampler": ("STRING", {"default": "dpmpp_2m"}),
                # "scheduler": ("STRING", {"default": "karras"}),
                # "save_changes": ("BOOLEAN", {"default": False}),  # Optional save flag
            }
        }
    
    # Define output types:
    # For example, steps (integer), cfg (float), sampler (string), scheduler (string)
    # RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING")
    RETURN_TYPES = ("INT", "FLOAT", comfy.samplers.KSampler.SAMPLERS,
                  comfy.samplers.KSampler.SCHEDULERS)
    RETURN_NAMES = ("STEPS", "CFG", "SAMPLER", "SCHEDULER")
    FUNCTION = "select_config"
    CATEGORY = "Configuration"

    # Your configuration dictionary:
    CONFIGS = {
        "SDXL": {"steps": 30, "cfg": 7.0, "sampler": "dpmpp_2m", "scheduler": "karras"},
        "Illustrious": {"steps": 30, "cfg": 5.0, "sampler": "euler_ancestral", "scheduler": "Exponential"},
    }

    # UI Widget to display real-time info
    UI_WIDGETS = {
        "model_choice": {
            "type": "dropdown",
            "options": ["SDXL", "Illustrious"],
            "on_change": "update_preview"
        }
    }

    def select_config(self, model_choice):
        # Look up the configuration for the selected model.
        config = self.CONFIGS.get(model_choice, None)
        if config is None:
            # If the model name isn't found, you can return defaults or raise an error.
            return (20, 7.0, "euler_a", "normal")
        return (config["steps"], config["cfg"], config["sampler"], config["scheduler"])

    def update_preview(self, model_choice):
        config = self.CONFIGS.get(model_choice, {})
        steps = config.get("steps", "N/A")
        cfg = config.get("cfg", "N/A")
        sampler = config.get("sampler", "N/A")
        scheduler = config.get("scheduler", "N/A")

        # Update node UI dynamically
        return {
            "preview": f"Steps: {steps}, CFG: {cfg}, Sampler: {sampler}, Scheduler: {scheduler}"
        }

NODE_CLASS_MAPPINGS = {
    "ComfygSwitch": ComfygSwitch
}