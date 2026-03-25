"""
PQC Benchmarking engine using liboqs-python.
Provides detailed performance comparison between classical and PQC algorithms.
"""

import time
import statistics
from datetime import datetime


def run_benchmarks(iterations: int = 100) -> dict:
    """Run comprehensive PQC benchmarks."""
    try:
        import oqs
        return _run_liboqs_benchmarks(oqs, iterations)
    except ImportError:
        return _get_reference_benchmarks()


def _run_liboqs_benchmarks(oqs, iterations: int) -> dict:
    """Run real benchmarks using liboqs-python."""
    results = {
        "tool": "liboqs-python",
        "timestamp": datetime.now().isoformat(),
        "iterations": iterations,
        "kem_benchmarks": [],
        "sig_benchmarks": [],
        "measured": True,
    }
    
    # Benchmark KEMs
    kem_targets = []
    available_kems = oqs.get_enabled_kem_mechanisms()
    for name in available_kems:
        lower = name.lower()
        if any(k in lower for k in ["kyber", "ml-kem", "bike", "hqc"]):
            kem_targets.append(name)
    
    for algo in kem_targets[:6]:
        bench = _benchmark_kem(oqs, algo, iterations)
        if bench:
            results["kem_benchmarks"].append(bench)
    
    # Benchmark Signatures
    sig_targets = []
    available_sigs = oqs.get_enabled_sig_mechanisms()
    for name in available_sigs:
        lower = name.lower()
        if any(k in lower for k in ["dilithium", "ml-dsa", "sphincs", "falcon"]):
            sig_targets.append(name)
    
    for algo in sig_targets[:6]:
        bench = _benchmark_sig(oqs, algo, iterations)
        if bench:
            results["sig_benchmarks"].append(bench)
    
    # Add comparison with classical
    results["classical_comparison"] = _get_classical_benchmarks()
    results["analysis"] = _analyze_benchmarks(results)
    
    return results


def _benchmark_kem(oqs, algo_name: str, iterations: int) -> dict:
    """Benchmark a single KEM algorithm."""
    try:
        kem = oqs.KeyEncapsulation(algo_name)
        
        keygen_times = []
        encaps_times = []
        decaps_times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            public_key = kem.generate_keypair()
            keygen_times.append((time.perf_counter() - start) * 1000)
            
            start = time.perf_counter()
            ciphertext, shared_secret = kem.encap_secret(public_key)
            encaps_times.append((time.perf_counter() - start) * 1000)
            
            start = time.perf_counter()
            shared_secret_dec = kem.decap_secret(ciphertext)
            decaps_times.append((time.perf_counter() - start) * 1000)
        
        details = kem.details
        kem.free()
        
        return {
            "algorithm": algo_name,
            "type": "KEM",
            "nist_level": details.get("claimed_nist_level", 0),
            "sizes": {
                "public_key": details.get("length_public_key", 0),
                "secret_key": details.get("length_secret_key", 0),
                "ciphertext": details.get("length_ciphertext", 0),
                "shared_secret": details.get("length_shared_secret", 0),
            },
            "keygen_ms": {
                "mean": round(statistics.mean(keygen_times), 4),
                "median": round(statistics.median(keygen_times), 4),
                "stdev": round(statistics.stdev(keygen_times), 4) if len(keygen_times) > 1 else 0,
                "min": round(min(keygen_times), 4),
                "max": round(max(keygen_times), 4),
            },
            "encaps_ms": {
                "mean": round(statistics.mean(encaps_times), 4),
                "median": round(statistics.median(encaps_times), 4),
                "stdev": round(statistics.stdev(encaps_times), 4) if len(encaps_times) > 1 else 0,
                "min": round(min(encaps_times), 4),
                "max": round(max(encaps_times), 4),
            },
            "decaps_ms": {
                "mean": round(statistics.mean(decaps_times), 4),
                "median": round(statistics.median(decaps_times), 4),
                "stdev": round(statistics.stdev(decaps_times), 4) if len(decaps_times) > 1 else 0,
                "min": round(min(decaps_times), 4),
                "max": round(max(decaps_times), 4),
            },
            "total_mean_ms": round(
                statistics.mean(keygen_times) + statistics.mean(encaps_times) + statistics.mean(decaps_times), 4
            ),
        }
    except Exception as e:
        print(f"Benchmark error for {algo_name}: {e}")
        return None


def _benchmark_sig(oqs, algo_name: str, iterations: int) -> dict:
    """Benchmark a single signature algorithm."""
    try:
        sig = oqs.Signature(algo_name)
        message = b"Benchmark test message for PQC signatures " * 10
        
        keygen_times = []
        sign_times = []
        verify_times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            public_key = sig.generate_keypair()
            keygen_times.append((time.perf_counter() - start) * 1000)
            
            start = time.perf_counter()
            signature = sig.sign(message)
            sign_times.append((time.perf_counter() - start) * 1000)
            
            start = time.perf_counter()
            is_valid = sig.verify(message, signature, public_key)
            verify_times.append((time.perf_counter() - start) * 1000)
        
        details = sig.details
        sig.free()
        
        return {
            "algorithm": algo_name,
            "type": "Signature",
            "nist_level": details.get("claimed_nist_level", 0),
            "sizes": {
                "public_key": details.get("length_public_key", 0),
                "secret_key": details.get("length_secret_key", 0),
                "signature": details.get("max_length_signature", 0),
            },
            "keygen_ms": {
                "mean": round(statistics.mean(keygen_times), 4),
                "median": round(statistics.median(keygen_times), 4),
                "stdev": round(statistics.stdev(keygen_times), 4) if len(keygen_times) > 1 else 0,
            },
            "sign_ms": {
                "mean": round(statistics.mean(sign_times), 4),
                "median": round(statistics.median(sign_times), 4),
                "stdev": round(statistics.stdev(sign_times), 4) if len(sign_times) > 1 else 0,
            },
            "verify_ms": {
                "mean": round(statistics.mean(verify_times), 4),
                "median": round(statistics.median(verify_times), 4),
                "stdev": round(statistics.stdev(verify_times), 4) if len(verify_times) > 1 else 0,
            },
            "total_mean_ms": round(
                statistics.mean(keygen_times) + statistics.mean(sign_times) + statistics.mean(verify_times), 4
            ),
        }
    except Exception as e:
        print(f"Benchmark error for {algo_name}: {e}")
        return None


def _get_classical_benchmarks() -> list:
    """Reference classical algorithm benchmarks for comparison."""
    return [
        {
            "algorithm": "RSA-2048",
            "type": "Key Exchange / Signing",
            "keygen_ms": {"mean": 150.0},
            "operation_ms": {"mean": 0.80},
            "sizes": {"public_key": 256, "secret_key": 1190, "signature": 256},
            "quantum_safe": False,
        },
        {
            "algorithm": "ECDSA P-256",
            "type": "Signing",
            "keygen_ms": {"mean": 0.03},
            "operation_ms": {"mean": 0.06},
            "sizes": {"public_key": 64, "secret_key": 32, "signature": 72},
            "quantum_safe": False,
        },
        {
            "algorithm": "ECDH P-256",
            "type": "Key Exchange",
            "keygen_ms": {"mean": 0.03},
            "operation_ms": {"mean": 0.05},
            "sizes": {"public_key": 64, "secret_key": 32},
            "quantum_safe": False,
        },
        {
            "algorithm": "AES-256-GCM",
            "type": "Symmetric",
            "keygen_ms": {"mean": 0.001},
            "operation_ms": {"mean": 0.001},
            "sizes": {"secret_key": 32},
            "quantum_safe": True,
        },
    ]


def _get_reference_benchmarks() -> dict:
    """Return reference benchmark data when liboqs is not available."""
    return {
        "tool": "reference-data",
        "timestamp": datetime.now().isoformat(),
        "iterations": 0,
        "measured": False,
        "kem_benchmarks": [
            {
                "algorithm": "ML-KEM-512 (Kyber-512)",
                "type": "KEM", "nist_level": 1,
                "sizes": {"public_key": 800, "secret_key": 1632, "ciphertext": 768, "shared_secret": 32},
                "keygen_ms": {"mean": 0.035}, "encaps_ms": {"mean": 0.042}, "decaps_ms": {"mean": 0.040},
                "total_mean_ms": 0.117,
            },
            {
                "algorithm": "ML-KEM-768 (Kyber-768)",
                "type": "KEM", "nist_level": 3,
                "sizes": {"public_key": 1184, "secret_key": 2400, "ciphertext": 1088, "shared_secret": 32},
                "keygen_ms": {"mean": 0.055}, "encaps_ms": {"mean": 0.068}, "decaps_ms": {"mean": 0.063},
                "total_mean_ms": 0.186,
            },
            {
                "algorithm": "ML-KEM-1024 (Kyber-1024)",
                "type": "KEM", "nist_level": 5,
                "sizes": {"public_key": 1568, "secret_key": 3168, "ciphertext": 1568, "shared_secret": 32},
                "keygen_ms": {"mean": 0.083}, "encaps_ms": {"mean": 0.097}, "decaps_ms": {"mean": 0.093},
                "total_mean_ms": 0.273,
            },
        ],
        "sig_benchmarks": [
            {
                "algorithm": "ML-DSA-44 (Dilithium2)",
                "type": "Signature", "nist_level": 2,
                "sizes": {"public_key": 1312, "secret_key": 2528, "signature": 2420},
                "keygen_ms": {"mean": 0.080}, "sign_ms": {"mean": 0.250}, "verify_ms": {"mean": 0.080},
                "total_mean_ms": 0.410,
            },
            {
                "algorithm": "ML-DSA-65 (Dilithium3)",
                "type": "Signature", "nist_level": 3,
                "sizes": {"public_key": 1952, "secret_key": 4000, "signature": 3293},
                "keygen_ms": {"mean": 0.130}, "sign_ms": {"mean": 0.380}, "verify_ms": {"mean": 0.130},
                "total_mean_ms": 0.640,
            },
            {
                "algorithm": "SLH-DSA-SHA2-128f (SPHINCS+)",
                "type": "Signature", "nist_level": 1,
                "sizes": {"public_key": 32, "secret_key": 64, "signature": 17088},
                "keygen_ms": {"mean": 0.350}, "sign_ms": {"mean": 5.200}, "verify_ms": {"mean": 0.280},
                "total_mean_ms": 5.830,
            },
        ],
        "classical_comparison": _get_classical_benchmarks(),
        "analysis": {
            "recommendation": "ML-KEM-768 (Kyber) offers the best balance of security (NIST Level 3) and performance for key exchange. ML-DSA-65 (Dilithium) is recommended for digital signatures.",
            "key_size_impact": "PQC public keys are 5-20x larger than classical counterparts, impacting bandwidth. Plan for increased TLS handshake sizes.",
            "performance_impact": "PQC operations are very fast — Kyber is actually faster than RSA-2048 key generation. The main impact is on key/ciphertext sizes, not computation.",
        },
    }


def _analyze_benchmarks(results: dict) -> dict:
    """Analyze benchmark results and generate recommendations."""
    kem_benchmarks = results.get("kem_benchmarks", [])
    sig_benchmarks = results.get("sig_benchmarks", [])
    
    fastest_kem = min(kem_benchmarks, key=lambda x: x["total_mean_ms"]) if kem_benchmarks else None
    fastest_sig = min(sig_benchmarks, key=lambda x: x["total_mean_ms"]) if sig_benchmarks else None
    smallest_kem = min(kem_benchmarks, key=lambda x: x["sizes"]["public_key"]) if kem_benchmarks else None
    
    return {
        "recommendation": f"Recommended KEM: {fastest_kem['algorithm'] if fastest_kem else 'N/A'} (fastest). "
                         f"Recommended Signature: {fastest_sig['algorithm'] if fastest_sig else 'N/A'} (fastest).",
        "fastest_kem": fastest_kem["algorithm"] if fastest_kem else None,
        "fastest_sig": fastest_sig["algorithm"] if fastest_sig else None,
        "key_size_impact": "PQC keys are larger than classical equivalents. Plan for 2-10x increase in key material sizes.",
        "performance_impact": "PQC computational overhead is minimal. Main impact is bandwidth from larger keys and ciphertexts.",
        "migration_readiness": "READY" if kem_benchmarks and sig_benchmarks else "NEEDS_EVALUATION",
    }
