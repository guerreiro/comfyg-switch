import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
  name: "ComfygSwitch.DynamicDefaults",

  async nodeCreated(node) {
    // only act on your node
    if (node.comfyClass !== "ComfygSwitch") return;

    const getW = (name) => node.widgets?.find(w => w.name === name);

    const wCheckpoint   = getW("checkpoint_model");
    const wUseCustom    = getW("use_custom_input");
    const wSteps        = getW("steps");
    const wRefSteps     = getW("refiner_steps");
    const wCfg          = getW("cfg");
    const wSampler      = getW("sampler");
    const wScheduler    = getW("scheduler");

    const applyIfExists = (widget, value) => {
      if (!widget || value === undefined || value === null) return;
      // For COMBO widgets in ComfyUI, .value is the string label
      widget.value = value;
    };

    const applyConfig = (cfg) => {
      if (!cfg) return;
      // Respect the toggle: only autofill when NOT using custom edits
      if (wUseCustom && wUseCustom.value === true) return;

      applyIfExists(wSteps,     typeof cfg.steps === "number" ? cfg.steps : undefined);
      applyIfExists(wRefSteps,  typeof cfg.refiner_steps === "number" ? cfg.refiner_steps : undefined);
      applyIfExists(wCfg,       typeof cfg.cfg === "number" ? cfg.cfg : undefined);

      // Only set sampler/scheduler if the option exists in the dropdown
      const hasOption = (widget, val) =>
        widget && widget.options && widget.options.values
          ? widget.options.values.includes(val)
          : true; // fall back to trusting the string

      if (cfg.sampler && hasOption(wSampler, cfg.sampler))   applyIfExists(wSampler, cfg.sampler);
      if (cfg.scheduler && hasOption(wScheduler, cfg.scheduler)) applyIfExists(wScheduler, cfg.scheduler);

      node.setDirtyCanvas(true, true); // redraw
    };

    const fetchAndApply = async () => {
      try {
        const model = wCheckpoint?.value || "";
        const resp = await api.fetchApi(`/comfygswitch/config?model=${encodeURIComponent(model)}`);
        if (resp?.ok) {
          const data = await resp.json();
          applyConfig(data);
        }
      } catch (e) {
        console.error("ComfygSwitch fetch/apply failed:", e);
      }
    };

    const wReset = node.addWidget("button", "Reset", null, () => {
        fetchAndApply();
    });

    // Re-apply when user toggles custom mode off
    if (wUseCustom) {
      const origToggle = wUseCustom.callback;
      wUseCustom.callback = (v) => {
        origToggle?.call(node, v);
        if (v === false) fetchAndApply();
      };
    }

    // Hook checkpoint dropdown changes
    if (wCheckpoint) {
      const orig = wCheckpoint.callback;
      wCheckpoint.callback = (v) => {
        orig?.call(node, v);
        fetchAndApply();
      };
      // Initial populate for existing nodes
      fetchAndApply();
    }
  }
});
