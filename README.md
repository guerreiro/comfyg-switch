# Comfyg Switch

Comfyg Switch is a custom node that dynamically selects model configuration parameters based on the chosen checkpoint.
It reads model-specific settings from a JSON file (model_configs.json). You can change the values, but updating the node will lose all changes.
Alternatively, you can create your own custom file, named "my_model_configs.json," place it in the node's root directory, and then insert your settings into the new file, using the same pattern as the default file. You can even overwrite some settings from the default file by creating an item with the same name as the model and changing any attributes.
Now, updating the node won't lose your custom settings because this file isn't in Git.

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

# Roadmap (or ideas)

- Maybe load configs from an external database or something like that, to avoid update the config file everytime;
- Import each model config dinamically from CivitAI API and use the config file as optional (maybe use LLM to read the model content and create the config object);
- When switch the model, load the config data into the node inputs (steps, cfg, etc...) and let us see the values before start queue, or change them too;
- Load more details about the selected model to help us with the workflow (result examples, tips, prompts...);

# Contributing

Contributions and suggestions are welcome! If you encounter any issues or have ideas for improvements, please open an issue or submit a pull request.

# License

This project is licensed under the MIT License.
