# iomt-behavioural-digital-twin

Code and results for the paper "A Behavioural Digital Twin for Device-Aware Edge Intrusion Detection in the
Internet of Medical Things" (K. Mann, S. K. Sharma, S. Vasishth; submitted to the IEEE Internet of Things
Journal). Release `v1.0`.

https://github.com/kamal-mann/iomt-behavioural-digital-twin

The twin keeps per-device, per-operating-state profiles of benign traffic at the IoMT gateway, scores each window
of traffic by its deviation from the device's profile, and synchronises the profiles from trusted traffic under a
poisoning guard. The study measures the twin as a detector input, as an attack sensor, and in operation
(poisoning, cost and time to detect).

## Contents

| Path | What it is |
|---|---|
| `src/trace_iomt/` | Library: packet-capture features (`pcapfeat.py`, `pcapcheck.py`), the twin (`twin.py`, `twin_data.py`, `twin_sync.py`, `twin_poison.py`), the twin-aware detector (`models/`), training, metrics and the twin-study tables (`twin_study.py`, `twin_compare.py`) |
| `scripts/12`–`14` | Packet-capture scan, check of the extractor against the published profiling CSVs, extraction of per-device rows |
| `scripts/15`–`19` | Twin build, training of the twin variants (V0–V4) and the random forest, tables and verdict, poisoning test, cost and time to detect |
| `twin_all.sh` | Runs step 16 in lanes (`check`, `A`, `B`, `final`) |
| `configs/` | `twin.yaml` (twin study), its base configs `rerun.yaml`, `default_v2.yaml` and `default.yaml`, `twin_devices.json` (device identities), `smoke.yaml` and `twin_smoke.yaml` (tests) |
| `tests/` | Unit and smoke tests (`python -m pytest -q tests`) |
| `results/twin_study/` | The twin-study runs, the tables behind the paper's twin results (`tables/`), the hypothesis verdict (`twin_h11.json`), poisoning, synchronisation and cost records, and logs |
| `results/pcap_extraction/` | Extraction and validation logs, the check of the extractor against the profiling CSVs (`pcap_validation.csv`), the device-row manifests |

Every run folder has `config.json` and `metrics.json`; `metrics.json` records the SHA-256 of `src/trace_iomt/`
and of the input data (see `RELEASE_NOTES.md` for the two code states). Trained models, per-window predictions and the extracted device rows are not included
because of their size.

## Running the twin study

The reported runs used one Apple Mac Studio (M1 Ultra, 64 GB memory), the neural models on its GPU through the
PyTorch MPS backend. Python 3.10 to 3.12. Install PyTorch for your platform first, then `pip install -r requirements.txt`.

1. Download CICIoMT2024 (see Data below) and put the `WiFi_and_MQTT` folder under `data/raw/CICIoMT2024/`.
2. Extract per-device rows from the packet captures:
   `python scripts/14_pcap_extract.py --root data/raw/CICIoMT2024/WiFi_and_MQTT --mode device --all-hosts --workers 12`
   (`12_pcap_scan.py` and `13_pcap_validate.py` reproduce the scan and the check against the profiling CSVs).
3. Build the twin: `python scripts/15_twin_build.py --config configs/rerun.yaml --mode device_state --labels file`.
4. Train: `./twin_all.sh <device> A` and `./twin_all.sh <device> B` (in parallel), then `./twin_all.sh <device> final`.
   `<device>` is `cuda`, `mps` or `cpu`; `./twin_all.sh <device> check` is a one-epoch dry run.
5. Tables and verdict: `python scripts/17_twin_compare.py --config configs/twin.yaml`; poisoning:
   `python scripts/18_twin_poison.py --config configs/twin.yaml --seed 42`; cost and time to detect:
   `python scripts/19_twin_cost.py --config configs/twin.yaml`.

## Data

CICIoMT2024 (Dadkhah et al., Internet of Things, 2024) is available from the Canadian Institute for Cybersecurity:
https://www.unb.ca/cic/datasets/iomt-dataset-2024.html. It is not redistributed here.

## License and citation

MIT with a citation requirement; see `LICENSE` and `CITATION.cff`.
