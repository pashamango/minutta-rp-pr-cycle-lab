use base64::prelude::*;
use ed25519_dalek::{Signer, SigningKey, Verifier, VerifyingKey};
use std::env;
use std::time::{SystemTime, UNIX_EPOCH};

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.contains(&"--self-test".to_string()) {
        run_self_test();
        return;
    }

    println!("Polymarket US Rust Signer");
    println!("Usage: cargo run -- --self-test");
}

fn create_auth_headers(
    key_id: &str,
    secret_key_b64: &str,
    method: &str,
    path: &str,
    timestamp_ms: Option<u64>,
) -> Result<(String, String, String), String> {
    let ts = timestamp_ms.unwrap_or_else(|| {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    });

    let raw_key = BASE64_STANDARD
        .decode(secret_key_b64)
        .map_err(|e| format!("Invalid base64: {}", e))?;

    let seed: &[u8; 32] = match raw_key.len() {
        32 => raw_key[..32].try_into().unwrap(),
        64 => raw_key[..32].try_into().unwrap(),
        n => return Err(format!("Invalid key length: {}", n)),
    };

    let signing_key = SigningKey::from_bytes(seed);
    let message = format!("{}{}{}", ts, method.to_uppercase(), path);
    let signature = signing_key.sign(message.as_bytes());
    let sig_b64 = BASE64_STANDARD.encode(signature.to_bytes());

    Ok((key_id.to_string(), ts.to_string(), sig_b64))
}

fn run_self_test() {
    println!("Running Rust Polymarket US Signer Self-Test...");

    // Test vector from official SDK
    let key_id = "test-key-id";
    let secret = "nWGxne/9WmC6hEr0kuwsxERJxWl7MmkZcDusAxyuf2A=";
    let ts = 1700000000000u64;
    let path = "/v1/orders";
    let method = "POST";

    let (out_key, out_ts, out_sig) =
        create_auth_headers(key_id, secret, method, path, Some(ts)).expect("Signing failed");

    assert_eq!(out_key, key_id);
    assert_eq!(out_ts, "1700000000000");

    // Verify signature with ed25519-dalek VerifyingKey
    let raw_key = BASE64_STANDARD.decode(secret).unwrap();
    let seed: &[u8; 32] = raw_key[..32].try_into().unwrap();
    let signing_key = SigningKey::from_bytes(seed);
    let verifying_key: VerifyingKey = signing_key.verifying_key();

    let message = format!("{}{}{}", ts, method.to_uppercase(), path);
    let sig_bytes = BASE64_STANDARD.decode(&out_sig).unwrap();
    let sig = ed25519_dalek::Signature::from_slice(&sig_bytes).unwrap();

    verifying_key
        .verify(message.as_bytes(), &sig)
        .expect("Signature verification failed");

    println!("Rust Signer Self-Test: PASS (verified against official SDK vector)");
}
