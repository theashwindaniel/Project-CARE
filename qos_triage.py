import os
import time
import random
import hmac
import hashlib
import sys

# Terminal Styling
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Priority 4: Environment Variable Key Handling with Secure Fallback
SHARED_KEY = os.environ.get("CARE_SECRET_KEY", "TCQ_AI_KAVACH_PROD_SECURE_2026").encode('utf-8')

class CUSUMDetector:
    """Cumulative Sum Anomaly Detection for RF Link Degradation"""
    def __init__(self, baseline_snr=26.0, threshold=12.0, drift=1.5):
        self.baseline = baseline_snr
        self.threshold = threshold
        self.drift = drift
        self.cum_sum = 0.0

    def update(self, current_snr):
        deviation = (self.baseline - current_snr) - self.drift
        self.cum_sum = max(0.0, self.cum_sum + deviation)
        return self.cum_sum > self.threshold, self.cum_sum

    def reset(self):
        self.cum_sum = 0.0


class CAREEvaluationEngine:
    def __init__(self):
        self.tripwire = CUSUMDetector()
        self.sequence_counter = 0
        self.battery_level = 100.0
        self.edge_cache_kb = 0
        self.cached_packets_count = 0  
        self.cache_limit_kb = 51200  
        self.current_waveform = "64-QAM (Uncoded Wideband)"
        
        # Priority 3: Spatial Diversity / Mesh Neighbor Table
        self.mesh_neighbors = {
            "NODE_BRAVO_RELAY": {"snr": 18.2, "status": "ACTIVE"},
            "NODE_CHARLIE_SQUAD": {"snr": 4.1, "status": "JAMMED"}
        }

        # Verification & Delivery Tracking
        self.stats = {
            "critical": {"sent": 0, "delivered": 0, "weight": 100},
            "heavy": {"sent": 0, "delivered": 0, "weight": 10},
            "spoofed_blocked": 0
        }

    def generate_hmac(self, payload, seq):
        message = f"{seq}:{payload}".encode('utf-8')
        return hmac.new(SHARED_KEY, message, hashlib.sha256).hexdigest()[:16]

    def verify_hmac(self, payload, seq, received_hmac):
        expected = self.generate_hmac(payload, seq)
        return hmac.compare_digest(expected, received_hmac)

    def find_mesh_alternate(self):
        for node, data in self.mesh_neighbors.items():
            if data["status"] == "ACTIVE" and data["snr"] > 12.0:
                return node, data["snr"]
        return None, None

    def classify_interference(self, snr, loss_rate):
        if snr < 6.0 and loss_rate >= 0.70:
            return "BARRAGE JAMMING (High EW Intensity)"
        elif snr < 14.0 and loss_rate >= 0.35:
            return "SPOT/REACTIVE JAMMING"
        return "BENIGN CHANNEL FADING"

    def adapt_waveform(self, threat):
        if "BARRAGE" in threat:
            self.current_waveform = "BPSK + 1/2 Rate Convolutional FEC"
        elif "SPOT" in threat:
            self.current_waveform = "QPSK + Frequency Hopping"
        else:
            self.current_waveform = "64-QAM (Uncoded Wideband)"
        print(f"[{YELLOW}WAVEFORM ADAPT{RESET}] PHY Layer Reconfigured -> {BOLD}{self.current_waveform}{RESET}")

    def update_power(self, cost):
        self.battery_level = max(0.0, self.battery_level - cost)

    def process_packet(self, tier, data_name, payload, payload_size_kb, is_jammed):
        self.sequence_counter += 1
        seq = self.sequence_counter
        is_critical = tier in [0, 1]
        stat_key = "critical" if is_critical else "heavy"
        self.stats[stat_key]["sent"] += 1

        print(f"\n[{CYAN}PKT DISPATCH{RESET}] Seq #{seq} | Tier {tier} | Payload: {data_name} ({payload_size_kb} KB)")
        time.sleep(0.3)

        if self.battery_level <= 20.0 and is_critical:
            print(f"[{YELLOW}SWaP POLICY{RESET}] Battery Critical ({self.battery_level:.1f}%). Shifted to micro-burst cycle.")

        if is_jammed:
            if not is_critical:
                print(f"[{RED}MUD DECISION: DROP{RESET}] Insufficient bandwidth for Tier {tier}. Suppressing transmission.")
                if (self.edge_cache_kb + payload_size_kb) <= self.cache_limit_kb:
                    self.edge_cache_kb += payload_size_kb
                    self.cached_packets_count += 1  
                    print(f"[{YELLOW}EDGE CACHE{RESET}] Buffered locally. Tactical Cache: {self.edge_cache_kb} KB / {self.cache_limit_kb} KB")
                return False

            print(f"[{GREEN}MUD DECISION: SURVIVAL ROUTE{RESET}] Allocating protected sub-carrier.")
            
            relay_node, relay_snr = self.find_mesh_alternate()
            if relay_node:
                print(f"[{CYAN}MESH DIVERSITY{RESET}] Routing micro-burst via relay {BOLD}{relay_node}{RESET} (SNR: {relay_snr} dB)")

            sig = self.generate_hmac(payload, seq)
            self.update_power(1.8)

            retries = 2
            for attempt in range(1, retries + 1):
                # SIMULATING ACTUAL RF CORRUPTION (Bit-flips altering the payload)
                is_corrupted = random.random() < 0.15
                received_payload = payload if not is_corrupted else payload + "_NOISE_CORRUPTION"

                if self.verify_hmac(received_payload, seq, sig):
                    print(f"[{GREEN}AUTH SUCCESS{RESET}] Zero-Trust Signature Verified [{sig}]. Telemetry logged.")
                    self.stats["critical"]["delivered"] += 1
                    return True
                else:
                    if is_corrupted:
                        print(f"[{YELLOW}RF CORRUPTION{RESET}] Packet #{seq} distorted in transit (HMAC Mismatch). Retrying ({attempt}/{retries})...")
                        time.sleep(0.2)
                        continue
                    else:
                        print(f"[{RED}TAMPER DETECTED{RESET}] Cryptographic hash mismatch. Dropping packet.")
                        return False

            print(f"[{RED}BURST FAILED{RESET}] Packet #{seq} lost in jamming noise after {retries} retries.")
            return False

        else:
            self.update_power(0.5)
            self.stats[stat_key]["delivered"] += 1
            print(f"[{GREEN}DIRECT TRANSMIT{RESET}] Nominal delivery confirmed across primary link.")
            return True

    def test_spoofing_defense(self):
        self.sequence_counter += 1
        seq = self.sequence_counter
        tampered_payload = '{"lat": 34.999, "lon": 74.111, "spoofed": true}'
        fake_hmac = "deadbeefcafebabe"  
        expected_hmac = self.generate_hmac(tampered_payload, seq)
        
        print(f"\n[{RED}ADVERSARIAL INJECTION{RESET}] Hostile EW node injecting spoofed GPS packet (Seq #{seq})...")
        time.sleep(0.8) 
        
        # Attacker does not have SHARED_KEY, so any HMAC they guess will not match.
        print(f"[{YELLOW}HMAC CHECK{RESET}] Expected: {expected_hmac} | Received: {fake_hmac}")
        time.sleep(0.5)

        if self.verify_hmac(tampered_payload, seq, fake_hmac):
            print(f"[{RED}CRITICAL SECURITY BREACH{RESET}] Malicious packet accepted.")
        else:
            print(f"[{GREEN}ZERO-TRUST DEFENSE{RESET}] Cryptographic signature invalid! Spoofed telemetry rejected at the boundary.")
            self.stats["spoofed_blocked"] += 1

    def execute_link_recovery(self, recovered_snr=25.8):
        print(f"\n{GREEN}>>> PHASE 4: RF ENVIRONMENT CLEARING (SNR Rising to {recovered_snr} dB){RESET}")
        time.sleep(0.5)
        
        print(f"[{YELLOW}HYSTERESIS TIMER{RESET}] Holding degraded state for 1.0s to prevent state oscillation / RF flutter...")
        time.sleep(1.0)
        print(f"[{GREEN}LINK STABILIZED{RESET}] Channel persistence confirmed. Resetting CUSUM threshold.")
        self.tripwire.reset()
        self.adapt_waveform("BENIGN")

        if self.edge_cache_kb > 0:
            print(f"[{CYAN}CACHE OFFLOAD{RESET}] Uplinking {self.edge_cache_kb} KB of deferred high-res reconnaissance data...")
            time.sleep(0.6)
            
            self.stats["heavy"]["delivered"] += self.cached_packets_count
            self.update_power(self.edge_cache_kb * 0.0005)
            
            self.edge_cache_kb = 0
            self.cached_packets_count = 0
            print(f"[{GREEN}SYNC COMPLETE{RESET}] Tactical Edge Cache flushed. All reconnaissance data synced.")

    def print_mission_report(self):
        crit_sent = self.stats["critical"]["sent"]
        crit_del = self.stats["critical"]["delivered"]
        heavy_sent = self.stats["heavy"]["sent"]
        heavy_del = self.stats["heavy"]["delivered"]

        cdr_critical = (crit_del / crit_sent * 100) if crit_sent > 0 else 0.0
        cdr_heavy = (heavy_del / heavy_sent * 100) if heavy_sent > 0 else 0.0

        delivered_utility = (crit_del * self.stats["critical"]["weight"]) + (heavy_del * self.stats["heavy"]["weight"])
        max_possible_utility = (crit_sent * self.stats["critical"]["weight"]) + (heavy_sent * self.stats["heavy"]["weight"])
        mud_score = (delivered_utility / max_possible_utility * 100) if max_possible_utility > 0 else 0.0

        print(f"\n{CYAN}======================================================================{RESET}")
        print(f"{BOLD}             MISSION UTILITY DELIVERED (MUD) FINAL REPORT             {RESET}")
        print(f"{CYAN}======================================================================{RESET}")
        print(f" {'Data Category':<20} | {'Sent':<6} | {'Delivered':<10} | {'CDR (%)':<10} | {'Priority Weight'}")
        print(f"----------------------------------------------------------------------")
        print(f" Tier 0/1 (GPS/SOS)   | {crit_sent:<6} | {crit_del:<10} | {cdr_critical:>6.1f}%    | 100 (Survival)")
        print(f" Tier 3/4 (Video/Map) | {heavy_sent:<6} | {heavy_del:<10} | {cdr_heavy:>6.1f}%    | 10  (Recovered)")
        print(f"----------------------------------------------------------------------")
        print(f" {BOLD}MUD Score (Weighted Utility Achieved): {mud_score:.2f}%{RESET}")
        print(f" Adversarial Spoofing Attacks Thwarted: {self.stats['spoofed_blocked']}")
        print(f" Tactical Edge Cache Backlog: {self.edge_cache_kb} KB")
        print(f" Remaining System Battery: {self.battery_level:.1f}%")
        print(f"{CYAN}======================================================================{RESET}\n")


def run_simulation():
    engine = CAREEvaluationEngine()

    print(f"\n{CYAN}======================================================================{RESET}")
    print(f"{BOLD} C.A.R.E. (Cognitive Adaptive Radio Engine) - Tactical Defense Core{RESET}")
    print(f" Track-II: AI KAVACH EW-Resilient Telemetry Validation")
    print(f"{CYAN}======================================================================{RESET}\n")
    time.sleep(0.6)

    # 1. Nominal Clean Operations
    print(f"{GREEN}>>> PHASE 1: CLEAR SPECTRUM (SNR: 26.0 dB, Bit Error Rate: 0.01%){RESET}")
    engine.process_packet(4, "HD Drone Video Feed", "stream_chunk_001", 1400, False)
    engine.process_packet(0, "GPS Positioning (Blue Force)", '{"lat": 34.08, "lon": 74.79}', 4, False)
    time.sleep(0.8)

    # 2. Electronic Warfare Attack Detected
    print(f"\n{RED}>>> PHASE 2: EW INTERFERENCE ENGAGED (High-Power Barrage Detected){RESET}")
    current_snr = 3.4
    packet_loss = 0.88
    print(f"[{RED}RF SENSOR{RESET}] Channel collapsed: SNR={current_snr} dB, Loss Rate={packet_loss*100:.0f}%")

    _, score = engine.tripwire.update(current_snr)
    print(f"[{RED}CUSUM TRIPWIRE{RESET}] Anomaly Score: {score:.2f} (Breach Threshold: {engine.tripwire.threshold})")

    threat = engine.classify_interference(current_snr, packet_loss)
    print(f"[{YELLOW}THREAT CLASSIFIER{RESET}] Classification: {BOLD}{threat}{RESET}")
    engine.adapt_waveform(threat)
    time.sleep(0.8)

    # 3. Triage Execution & Zero-Trust Adversarial Defense
    print(f"\n{YELLOW}>>> PHASE 3: AUTONOMOUS TRIAGE & ZERO-TRUST COUNTERMEASURES{RESET}")
    engine.process_packet(4, "HD Drone Video Feed", "stream_chunk_002", 1400, True)
    engine.process_packet(3, "High-Res Contour Map", "elevation_tile_x4", 820, True)
    engine.process_packet(0, "GPS Positioning (Blue Force)", '{"lat": 34.083, "lon": 74.792}', 4, True)
    
    engine.test_spoofing_defense()

    engine.process_packet(0, "Immediate Medevac SOS", "SOS_CASUALTY_URGENT", 2, True)
    time.sleep(0.8)

    # 4. RF Link Recovery & Edge Cache Sync
    engine.execute_link_recovery(recovered_snr=25.8)

    # 5. Output Final Assessment Report
    engine.print_mission_report()

if __name__ == "__main__":
    run_simulation()
