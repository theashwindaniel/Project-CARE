# Project C.A.R.E. (Cognitive Adaptive Radio Engine) 🛡️
**Track-II: AI KAVACH | Indian Army Terrier Cyber Quest 2026**

## Overview
Conventional SDRs attempt to force heavy payloads (live video, 3D maps) through degraded channels during an Electronic Warfare (EW) barrage, resulting in complete link collapse and the loss of critical telemetry. 

Project C.A.R.E. is a lightweight middleware that acts as a cognitive shield. It detects the onset of link collapse using a **CUSUM statistical tripwire**. It autonomously throttles Tier 3/4 data (Video/Maps) to a local edge cache and reserves the remaining bandwidth exclusively for Tier 0/1 survival data (GPS/SOS), authenticated via **HMAC-SHA256 zero-trust cryptography**.

## Core Defense Capabilities
* **CUSUM Anomaly Detection:** Real-time statistical drift tracking to detect jamming vs. natural fading.
* **Zero-Trust Telemetry:** Embedded HMAC-SHA256 signatures with sequence counters to block replay and spoofing attacks.
* **SWaP Monitoring:** Battery depletion tracking triggering low-power micro-burst cycles.
* **Dynamic Waveform Adaptation:** Autonomous shifting from 64-QAM to BPSK with FEC during barrage interference.
* **Mesh Rerouting & Cache Offload:** Relays packets via alternate nodes when jammed, and autonomously flushes tactical edge caches once RF conditions stabilize.
* **Mission Utility Delivered (MUD) Analytics:** Live evaluation of Critical Delivery Ratio (CDR).

## Running the Simulation
This repository contains a functional Python terminal simulation of the C.A.R.E. triage logic. 

```bash
python qos_triage.py
```

*The simulation will output a color-coded tactical terminal demonstrating real-time threat classification, cryptographic verification, and the final MUD evaluation report.*

## Future Scope
* **Hardware Integration:** Deployment onto GNU Radio and procurement-ready SDRs.
* **Field Trials:** Testing on active Army-procured radio sets in simulated electronic warfare ranges.
* **Expanded Mesh:** Satellite ground station support for over-the-horizon telemetry recovery.

## Limitations
* This repository serves as a mathematical proof-of-concept simulation designed for rapid hackathon evaluation. 
* Real RF integration requires physical layer translation. 
* The ML threat classifier utilizes heuristic boundaries for demonstration; future iterations will deploy trained models via TensorFlow Lite.

## License
Distributed under the MIT License.
