"""
liboqs-based PQC algorithm evaluator.
Uses the Open Quantum Safe library to actually instantiate and run PQC algorithms.
"""

import time
import sys
from datetime import datetime


def get_liboqs_available():
    """Check if liboqs-python is available."""
    try:
        import oqs
        return True
    except ImportError:
        return False


def evaluate_kem_algorithms() -> list:
    """Evaluate Key Encapsulation Mechanism (KEM) algorithms using liboqs."""
    if get_liboqs_available():
        return _run_real_kem_evaluation()
    else:
        return _get_reference_kem_data()


def evaluate_signature_algorithms() -> list:
    """Evaluate digital signature algorithms using liboqs."""
    if get_liboqs_available():
        return _run_real_sig_evaluation()
    else:
        return _get_reference_sig_data()


def _run_real_kem_evaluation() -> list:
    """Run actual KEM evaluation using liboqs-python."""
    import oqs
    
    kem_algos = []
    target_kems = ["Kyber512", "Kyber768", "Kyber1024", "Kyber512"]
    
    # Get available KEMs from liboqs
    available = oqs.get_enabled_kem_mechanisms()
    
    # Map common names to liboqs names
    kem_map = {}
    for name in available:
        lower = name.lower()
        if "kyber" in lower or "ml-kem" in lower:
            kem_map[name] = name
        elif "bike" in lower:
            kem_map[name] = name
        elif "hqc" in lower:
            kem_map[name] = name
        elif "frodokem" in lower:
            kem_map[name] = name
    
    # Select representative algorithms
    test_kems = list(kem_map.keys())[:8]  # Limit to top 8
    
    for algo_name in test_kems:
        try:
            kem = oqs.KeyEncapsulation(algo_name)
            
            # Benchmark key generation
            iterations = 100
            start = time.perf_counter()
            for _ in range(iterations):
                public_key = kem.generate_keypair()
            keygen_time = (time.perf_counter() - start) / iterations * 1000  # ms
            
            # Benchmark encapsulation
            start = time.perf_counter()
            for _ in range(iterations):
                ciphertext, shared_secret = kem.encap_secret(public_key)
            encaps_time = (time.perf_counter() - start) / iterations * 1000
            
            # Benchmark decapsulation
            start = time.perf_counter()
            for _ in range(iterations):
                shared_secret_dec = kem.decap_secret(ciphertext)
            decaps_time = (time.perf_counter() - start) / iterations * 1000
            
            details = kem.details
            
            kem_algos.append({
                "name": algo_name,
                "type": "KEM",
                "nist_level": details.get("claimed_nist_level", 0),
                "public_key_size": details.get("length_public_key", 0),
                "secret_key_size": details.get("length_secret_key", 0),
                "ciphertext_size": details.get("length_ciphertext", 0),
                "shared_secret_size": details.get("length_shared_secret", 0),
                "keygen_time_ms": round(keygen_time, 3),
                "encaps_time_ms": round(encaps_time, 3),
                "decaps_time_ms": round(decaps_time, 3),
                "total_time_ms": round(keygen_time + encaps_time + decaps_time, 3),
                "measured": True,
                "iterations": iterations,
            })
            
            kem.free()
        except Exception as e:
            print(f"Error evaluating {algo_name}: {e}")
    
    return kem_algos


def _run_real_sig_evaluation() -> list:
    """Run actual signature evaluation using liboqs-python."""
    import oqs
    
    sig_algos = []
    available = oqs.get_enabled_sig_mechanisms()
    
    # Select representative signature algorithms
    test_sigs = []
    for name in available:
        lower = name.lower()
        if any(k in lower for k in ["dilithium", "ml-dsa", "sphincs", "falcon"]):
            test_sigs.append(name)
    
    test_sigs = test_sigs[:8]  # Limit
    
    test_message = b"Test message for PQC signature benchmarking - " * 10
    
    for algo_name in test_sigs:
        try:
            sig = oqs.Signature(algo_name)
            
            iterations = 50
            
            # Benchmark key generation
            start = time.perf_counter()
            for _ in range(iterations):
                public_key = sig.generate_keypair()
            keygen_time = (time.perf_counter() - start) / iterations * 1000
            
            # Benchmark signing
            start = time.perf_counter()
            for _ in range(iterations):
                signature = sig.sign(test_message)
            sign_time = (time.perf_counter() - start) / iterations * 1000
            
            # Benchmark verification
            start = time.perf_counter()
            for _ in range(iterations):
                is_valid = sig.verify(test_message, signature, public_key)
            verify_time = (time.perf_counter() - start) / iterations * 1000
            
            details = sig.details
            
            sig_algos.append({
                "name": algo_name,
                "type": "Signature",
                "nist_level": details.get("claimed_nist_level", 0),
                "public_key_size": details.get("length_public_key", 0),
                "secret_key_size": details.get("length_secret_key", 0),
                "signature_size": details.get("max_length_signature", 0),
                "keygen_time_ms": round(keygen_time, 3),
                "sign_time_ms": round(sign_time, 3),
                "verify_time_ms": round(verify_time, 3),
                "total_time_ms": round(keygen_time + sign_time + verify_time, 3),
                "measured": True,
                "iterations": iterations,
            })
            
            sig.free()
        except Exception as e:
            print(f"Error evaluating {algo_name}: {e}")
    
    return sig_algos


def _get_reference_kem_data() -> list:
    """Reference KEM performance data from NIST PQC standardization."""
    return [
        {
            "name": "ML-KEM-512 (Kyber-512)",
            "type": "KEM",
            "nist_level": 1,
            "public_key_size": 800,
            "secret_key_size": 1632,
            "ciphertext_size": 768,
            "shared_secret_size": 32,
            "keygen_time_ms": 0.035,
            "encaps_time_ms": 0.042,
            "decaps_time_ms": 0.040,
            "total_time_ms": 0.117,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "ML-KEM-768 (Kyber-768)",
            "type": "KEM",
            "nist_level": 3,
            "public_key_size": 1184,
            "secret_key_size": 2400,
            "ciphertext_size": 1088,
            "shared_secret_size": 32,
            "keygen_time_ms": 0.055,
            "encaps_time_ms": 0.068,
            "decaps_time_ms": 0.063,
            "total_time_ms": 0.186,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "ML-KEM-1024 (Kyber-1024)",
            "type": "KEM",
            "nist_level": 5,
            "public_key_size": 1568,
            "secret_key_size": 3168,
            "ciphertext_size": 1568,
            "shared_secret_size": 32,
            "keygen_time_ms": 0.083,
            "encaps_time_ms": 0.097,
            "decaps_time_ms": 0.093,
            "total_time_ms": 0.273,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "HQC-128",
            "type": "KEM",
            "nist_level": 1,
            "public_key_size": 2249,
            "secret_key_size": 2289,
            "ciphertext_size": 4497,
            "shared_secret_size": 64,
            "keygen_time_ms": 0.090,
            "encaps_time_ms": 0.160,
            "decaps_time_ms": 0.230,
            "total_time_ms": 0.480,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "BIKE-L1",
            "type": "KEM",
            "nist_level": 1,
            "public_key_size": 1541,
            "secret_key_size": 3749,
            "ciphertext_size": 1573,
            "shared_secret_size": 32,
            "keygen_time_ms": 0.720,
            "encaps_time_ms": 0.230,
            "decaps_time_ms": 1.050,
            "total_time_ms": 2.000,
            "measured": False,
            "source": "NIST reference data",
        },
    ]


def _get_reference_sig_data() -> list:
    """Reference signature performance data."""
    return [
        {
            "name": "ML-DSA-44 (Dilithium2)",
            "type": "Signature",
            "nist_level": 2,
            "public_key_size": 1312,
            "secret_key_size": 2528,
            "signature_size": 2420,
            "keygen_time_ms": 0.080,
            "sign_time_ms": 0.250,
            "verify_time_ms": 0.080,
            "total_time_ms": 0.410,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "ML-DSA-65 (Dilithium3)",
            "type": "Signature",
            "nist_level": 3,
            "public_key_size": 1952,
            "secret_key_size": 4000,
            "signature_size": 3293,
            "keygen_time_ms": 0.130,
            "sign_time_ms": 0.380,
            "verify_time_ms": 0.130,
            "total_time_ms": 0.640,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "ML-DSA-87 (Dilithium5)",
            "type": "Signature",
            "nist_level": 5,
            "public_key_size": 2592,
            "secret_key_size": 4864,
            "signature_size": 4595,
            "keygen_time_ms": 0.200,
            "sign_time_ms": 0.470,
            "verify_time_ms": 0.210,
            "total_time_ms": 0.880,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "SLH-DSA-SHA2-128f (SPHINCS+ fast)",
            "type": "Signature",
            "nist_level": 1,
            "public_key_size": 32,
            "secret_key_size": 64,
            "signature_size": 17088,
            "keygen_time_ms": 0.350,
            "sign_time_ms": 5.200,
            "verify_time_ms": 0.280,
            "total_time_ms": 5.830,
            "measured": False,
            "source": "NIST reference data",
        },
        {
            "name": "Falcon-512",
            "type": "Signature",
            "nist_level": 1,
            "public_key_size": 897,
            "secret_key_size": 1281,
            "signature_size": 666,
            "keygen_time_ms": 8.500,
            "sign_time_ms": 0.400,
            "verify_time_ms": 0.070,
            "total_time_ms": 8.970,
            "measured": False,
            "source": "NIST reference data",
        },
    ]


def get_classical_comparison() -> list:
    """Classical algorithm reference data for comparison."""
    return [
        {
            "name": "RSA-2048",
            "type": "Key Exchange / Signing",
            "public_key_size": 256,
            "secret_key_size": 1190,
            "keygen_time_ms": 150.0,
            "operation_time_ms": 0.80,
            "quantum_safe": False,
            "quantum_threat": "Shor's Algorithm — factored in polynomial time",
        },
        {
            "name": "RSA-4096",
            "type": "Key Exchange / Signing",
            "public_key_size": 512,
            "secret_key_size": 2374,
            "keygen_time_ms": 1200.0,
            "operation_time_ms": 4.30,
            "quantum_safe": False,
            "quantum_threat": "Shor's Algorithm — factored in polynomial time",
        },
        {
            "name": "ECDSA P-256",
            "type": "Signing",
            "public_key_size": 64,
            "secret_key_size": 32,
            "keygen_time_ms": 0.030,
            "operation_time_ms": 0.060,
            "quantum_safe": False,
            "quantum_threat": "Shor's Algorithm — ECDLP solved in polynomial time",
        },
        {
            "name": "ECDH P-256",
            "type": "Key Exchange",
            "public_key_size": 64,
            "secret_key_size": 32,
            "keygen_time_ms": 0.030,
            "operation_time_ms": 0.050,
            "quantum_safe": False,
            "quantum_threat": "Shor's Algorithm — ECDLP solved in polynomial time",
        },
        {
            "name": "AES-256",
            "type": "Symmetric Encryption",
            "public_key_size": 0,
            "secret_key_size": 32,
            "keygen_time_ms": 0.001,
            "operation_time_ms": 0.001,
            "quantum_safe": True,
            "quantum_threat": "Grover's Algorithm — reduces to 128-bit security (still safe)",
        },
    ]


def evaluate_all() -> dict:
    """Run complete PQC evaluation and return results."""
    kem_results = evaluate_kem_algorithms()
    sig_results = evaluate_signature_algorithms()
    classical = get_classical_comparison()
    
    using_liboqs = get_liboqs_available()
    
    return {
        "tool": "liboqs-python" if using_liboqs else "reference-data",
        "liboqs_available": using_liboqs,
        "timestamp": datetime.now().isoformat(),
        "kem_algorithms": kem_results,
        "signature_algorithms": sig_results,
        "classical_algorithms": classical,
        "summary": {
            "total_pqc_evaluated": len(kem_results) + len(sig_results),
            "kem_count": len(kem_results),
            "sig_count": len(sig_results),
            "fastest_kem": min(kem_results, key=lambda x: x["total_time_ms"])["name"] if kem_results else None,
            "fastest_sig": min(sig_results, key=lambda x: x["total_time_ms"])["name"] if sig_results else None,
            "smallest_kem_keys": min(kem_results, key=lambda x: x["public_key_size"])["name"] if kem_results else None,
            "smallest_sig": min(sig_results, key=lambda x: x["signature_size"])["name"] if sig_results else None,
        },
    }
