# Comfyg Switch

Comfyg Switch is a custom node that dynamically selects model configuration parameters based on the chosen checkpoint. 
It reads model-specific settings from a JSON file (model_configs.json).

## Inputs

- checkpoint_model: This value is used to determine which configuration to load.
- use_custom_input (BOOLEAN): Toggle between using manual inputs and automatically loaded configurations.
- steps (INT): Number of inference steps (default: 30).
- refiner_steps (INT): Number of inference steps for enhancement (default: 30).
- cfg (FLOAT): Classifier-free guidance scale (default: 7.0).
- sampler (SAMPLER)
- scheduler (SCHEDULER)

## Outputs

- MODEL_NAME
- STEPS (INT)
- REFINE_STEPS (INT)
- CFG (FLOAT)
- SAMPLER (SAMPLER)
- SCHEDULER (SCHEDULER)

## Example

See the file: ComfygSwitch-example.json

# Contributing

Contributions and suggestions are welcome! If you encounter any issues or have ideas for improvements, please open an issue or submit a pull request on the ComfyUI GitHub repository.

# License

This project is licensed under the MIT License.