from src.security import verify_meta_signature


def test_valid_x_hub_signature_256_passes():
    raw_body = b'{"hello":"world"}'
    app_secret = "super-secret"
    signature = "sha256=e700c37c92d324b8d7af871f9cd3b18a47958b90b2e2a6657b2a83311959d38f"

    assert verify_meta_signature(raw_body, signature, app_secret)


def test_missing_signature_fails():
    assert not verify_meta_signature(b"{}", None, "secret")


def test_wrong_prefix_fails():
    assert not verify_meta_signature(b"{}", "sha1=abcdef", "secret")


def test_wrong_secret_fails():
    raw_body = b'{"hello":"world"}'
    signature = "sha256=e700c37c92d324b8d7af871f9cd3b18a47958b90b2e2a6657b2a83311959d38f"

    assert not verify_meta_signature(raw_body, signature, "different-secret")


def test_empty_secret_fails():
    assert not verify_meta_signature(b"{}", "sha256=abcdef", "")
