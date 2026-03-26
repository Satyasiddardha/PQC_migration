"""
PQC Intelligence Layer
Analyzes detected algorithms and generates NIST-compliant PQC migration recommendations.
"""

def generate_pqc_recommendations(input_data: dict) -> dict:
    """
    Takes a JSON payload of assets and returns structured PQC recommendations.
    """
    assets = input_data.get("assets", [])
    recommendations = []

    for asset in assets:
        file_path = asset.get("file", "unknown")
        algorithm = asset.get("algorithm", "").upper()
        usage = asset.get("usage", "").lower()
        risk_level = asset.get("risk_level", "Low").capitalize()

        pqc_rec = ""
        migration_type = "Monitor"
        reason = ""

        # 1 & 2. Identify Algorithm Type & Map to PQC
        if "RSA" in algorithm or "DH" in algorithm or "DIFFIE" in algorithm:
            if "SIGN" in usage or "SIGNATURE" in usage:
                pqc_rec = "CRYSTALS-Dilithium (ML-DSA)"
                reason = f"{algorithm} signatures are vulnerable to Shor's algorithm. ML-DSA is the primary NIST standard for quantum-safe digital signatures."
            else:
                pqc_rec = "CRYSTALS-Kyber (ML-KEM)"
                reason = f"{algorithm} key exchange is broken by quantum computers. ML-KEM is the chosen NIST standard for secure key encapsulation."
        
        elif "ECC" in algorithm or "ECDH" in algorithm:
            pqc_rec = "CRYSTALS-Kyber (ML-KEM)"
            reason = "Elliptic Curve cryptography is highly vulnerable to quantum attacks. Migrate to ML-KEM for secure key exchange."
            
        elif "ECDSA" in algorithm:
            pqc_rec = "CRYSTALS-Dilithium (ML-DSA)"
            reason = "ECDSA signatures rely on elliptic curves, which are quantum-vulnerable. Migrate to ML-DSA."
            
        elif "TLS" in algorithm:
            pqc_rec = "Hybrid TLS (Kyber + Classical fallback)"
            reason = "Legacy TLS versions use classical key exchange. Upgrade to TLS 1.3 with a hybrid Key Encapsulation Mechanism (e.g., X25519Kyber768) to ensure both classical compliance and quantum safety."
            
        elif "AES" in algorithm:
            pqc_rec = "Keep AES (increase to AES-256)"
            reason = "AES is resistant to Shor's algorithm. However, Grover's algorithm halves effective symmetric key sizes. Ensure you are using AES-256 for full quantum resistance."
            
        elif "SHA" in algorithm:
            pqc_rec = "Keep SHA-2 / SHA-3"
            reason = "Modern hash functions like SHA-256 and SHA-3 are considered quantum-safe. No immediate replacement needed."
            
        else:
            pqc_rec = "Evaluate based on usage"
            reason = "Algorithm type not explicitly mapped. Prioritize transitioning any asymmetric operations to ML-KEM or ML-DSA."

        # 3. Generate Recommendation Logic (Migration Type)
        if risk_level in ["Critical", "High"]:
            if "AES" in algorithm or "SHA" in algorithm:
                migration_type = "Monitor" # Symmetric/Hash are inherently safer
            else:
                migration_type = "Full PQC"
        elif risk_level == "Medium":
            migration_type = "Hybrid"
        else:
            migration_type = "Monitor"

        # Edge Rule: Always prefer hybrid mode if compatibility is uncertain for TLS
        if "TLS" in algorithm:
            migration_type = "Hybrid"

        recommendations.append({
            "file": file_path,
            "detected_algorithm": algorithm,
            "pqc_recommendation": pqc_rec,
            "migration_type": migration_type,
            "reason": reason
        })

    return {"recommendations": recommendations}
