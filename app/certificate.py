import datetime
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_signed_cert(
    domain, ca_cert_file, ca_key_file, out_cert_file, out_key_file
):
    with open(ca_key_file, "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(ca_cert_file, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([x509.NameAttribute(x509.OID_COMMON_NAME, domain)]))
        .sign(key, hashes.SHA256())
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(domain)]), critical=False
        )
        .sign(ca_key, hashes.SHA256())
    )

    os.makedirs(os.path.dirname(out_key_file), exist_ok=True)
    os.makedirs(os.path.dirname(out_cert_file), exist_ok=True)

    with open(out_key_file, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(out_cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    generate_signed_cert(
        "www.example.com",
        ca_cert_file="proxy_ca.crt",
        ca_key_file="proxy_ca.key",
        out_cert_file="certs/www.example.com.crt",
        out_key_file="certs/www.example.com.key",
    )
