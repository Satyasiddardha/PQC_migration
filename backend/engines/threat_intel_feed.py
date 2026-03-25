import json
import os
import urllib.request
import urllib.error
from datetime import datetime

class ThreatIntelligenceFeed:
    """
    Simulates a Live Quantum Threat Intelligence Feed.
    In a production environment, this would connect to a premium Cyber Threat API
    or a NIST/CISA RSS feed to dynamically predict Q-Day (Collapse Time).
    """
    
    def __init__(self):
        self.cache_file = os.path.join(os.path.dirname(__file__), "..", "data", "threat_feed_cache.json")
        self.default_c_time = 8.0
        
    def fetch_live_threat_data(self):
        """
        Attempts to fetch live threat data indicating a quantum breakthrough.
        For demonstration, we check a mock external URL or fallback to our local state.
        """
        threat_data = {
            "last_updated": datetime.now().isoformat(),
            "global_threat_level": "ELEVATED",
            "recent_breakthroughs": False,
            "algorithms": {
                "RSA": {"predicted_collapse_years": 8.0, "status": "Stable"},
                "ECC": {"predicted_collapse_years": 8.0, "status": "Stable"},
                "AES": {"predicted_collapse_years": 25.0, "status": "Secure"}
            }
        }
        
        # Check if we have a locally injected threat spike (for demo purposes)
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    cached_data = json.load(f)
                    
                # If the cache is newer or contains a manual threat spike, use it
                return cached_data
            except Exception:
                pass
                
        # Save default to cache if not exists
        with open(self.cache_file, "w") as f:
            json.dump(threat_data, f, indent=2)
            
        return threat_data

    def get_dynamic_collapse_time(self, algorithm: str) -> float:
        """
        Returns the dynamic Collapse Time (C) for a given algorithm 
        based on live threat intelligence.
        """
        data = self.fetch_live_threat_data()
        algo_upper = algorithm.upper()
        
        if algo_upper in ["RSA", "ECC", "EC", "DSA", "DH", "ECDH"]:
            # If a massive breakthrough happened, C might drop from 8.0 to 1.0 overnight!
            if data.get("recent_breakthroughs"):
                return 1.5  # Critical Q-Day adjustment!
            
            # Match specific algorithm
            for key, val in data.get("algorithms", {}).items():
                if key in algo_upper:
                    return val.get("predicted_collapse_years", self.default_c_time)
            
            return self.default_c_time
            
        elif algo_upper in ["MD5", "SHA-1", "DES", "3DES"]:
            return 0.0 # Already broken
        else:
            return 25.0 # Grover resistant

threat_feed = ThreatIntelligenceFeed()
