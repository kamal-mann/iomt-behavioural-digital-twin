# Release v1.0

Code and results behind "A Behavioural Digital Twin for Device-Aware Edge Intrusion Detection in the Internet of
Medical Things" (submitted to the IEEE Internet of Things Journal). See `README.md` for the contents and how to run
the twin study.

## Notes for publication

- All runs were made on one Apple Mac Studio (M1 Ultra, 64 GB memory); neural models used the PyTorch MPS backend.
- Paths on the training machine are replaced by `<repo>`, `<data>` and `<home>`, and its host name by
  `mac-studio`, in logs and run records.
- `twin_model.pkl` is not included: loading a Python pickle runs code, and step 15 regenerates it from the data.
- `src/trace_iomt/` is released as it was at the end of the twin study. Its SHA-256 (`57fe27a8…`) is the one
  recorded by the V4 runs and V0 seed 46. The other 20 twin-study runs (random forest, V0 seeds 42–45, V1, V2, V3)
  record `58e8c900…`, the library before the step-17 to step-19 code was added. The later changes add
  `twin_compare.py`, `twin_poison.py` and functions in `twin_study.py`, and move the body of
  `twin_data.window_inputs` into `window_inputs_at` with the same output; no training code changed.
- Only comments in `configs/`, `requirements.txt` and `twin_all.sh` were edited; all settings are unchanged.
