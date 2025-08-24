import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
  name: "ComfygSwitch.DynamicDefaults",

  async nodeCreated(node) {
    if (node.comfyClass !== "ComfygSwitch") return;

    const getW = (name) => node.widgets?.find(w => w.name === name);

    const wCheckpoint   = getW("checkpoint_model");
    const wConfigSource = getW("config_source");
    const wSteps        = getW("steps");
    const wRefSteps     = getW("refiner_steps");
    const wCfg          = getW("cfg");
    const wSampler      = getW("sampler");
    const wScheduler    = getW("scheduler");

    const applyIfExists = (widget, value) => {
      if (widget && value !== undefined) {
        widget.value = value;
      }
    };

    const applyConfig = (cfg) => {
      if (!cfg) return;
      applyIfExists(wConfigSource, cfg.config_name);
      applyIfExists(wSteps, cfg.config.steps);
      applyIfExists(wRefSteps, cfg.config.refiner_steps);
      applyIfExists(wCfg, cfg.config.cfg);
      applyIfExists(wSampler, cfg.config.sampler);
      applyIfExists(wScheduler, cfg.config.scheduler);
      node.setDirtyCanvas(true, true);
    };

    const fetchAndApply = async () => {
      try {
        const model = wCheckpoint?.value || "";
        if (!model) return;
        const resp = await api.fetchApi(`/comfyg-switch/config?model=${encodeURIComponent(model)}`);
        if (resp?.ok) {
          const data = await resp.json();
          applyConfig(data);
        }
      } catch (e) {
        console.error("ComfygSwitch fetch/apply failed:", e);
      }
    };

    // Add reset button
    node.addWidget("button", "Reset from JSON", null, () => {
      fetchAndApply();
    });

    // Hook checkpoint dropdown changes
    if (wCheckpoint) {
      const orig = wCheckpoint.callback;
      wCheckpoint.callback = (v) => {
        orig?.call(node, v);
        fetchAndApply();
      };
    }
  }
});
