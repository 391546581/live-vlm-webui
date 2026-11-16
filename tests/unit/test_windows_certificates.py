"""Regression tests for TLS startup without openssl.exe on Windows."""

import ipaddress
import ssl
from unittest.mock import patch

from cryptography import x509
from cryptography.hazmat.primitives import serialization

from live_vlm_webui.server import generate_self_signed_cert


def test_windows_certificates_load_without_openssl(tmp_path):
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    with (
        patch("live_vlm_webui.server.sys.platform", "win32"),
        patch("live_vlm_webui.server.subprocess.run") as run,
    ):
        assert generate_self_signed_cert(str(cert_path), str(key_path))
    run.assert_not_called()
    ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(cert_path, key_path)
    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    assert cert.public_key().public_numbers() == key.public_key().public_numbers()
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert san.get_values_for_type(x509.DNSName) == ["localhost"]
    assert san.get_values_for_type(x509.IPAddress) == [
        ipaddress.ip_address("127.0.0.1"),
        ipaddress.ip_address("::1"),
    ]


def test_existing_certificates_are_preserved(tmp_path):
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    with patch("live_vlm_webui.server.sys.platform", "win32"):
        assert generate_self_signed_cert(str(cert_path), str(key_path))
        original = (cert_path.read_bytes(), key_path.read_bytes())
        assert generate_self_signed_cert(str(cert_path), str(key_path))
    assert (cert_path.read_bytes(), key_path.read_bytes()) == original


def test_windows_certificate_write_failure_is_reported(tmp_path, caplog):
    with patch("live_vlm_webui.server.sys.platform", "win32"):
        assert not generate_self_signed_cert(
            str(tmp_path / "missing" / "cert.pem"), str(tmp_path / "missing" / "key.pem")
        )
    assert "Failed to write SSL credentials" in caplog.text


def test_posix_keeps_openssl_generation(tmp_path):
    with (
        patch("live_vlm_webui.server.sys.platform", "linux"),
        patch("live_vlm_webui.server.subprocess.run") as run,
    ):
        assert generate_self_signed_cert(str(tmp_path / "cert.pem"), str(tmp_path / "key.pem"))
    assert run.call_args.args[0][0] == "openssl"
