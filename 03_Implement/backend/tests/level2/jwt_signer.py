"""ADR-0063 D9-7: ephemeral RS256 key pair for the Level 2 mock IdP.

Keys are generated at startup and never committed to the repository.
Each process restart invalidates all previously issued tokens.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class EphemeralSigningKey:
    """An RS256 key pair generated once at process start."""

    def __init__(self, *, kid: str = "mock-idp-level2") -> None:
        self._kid = kid
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

    @property
    def kid(self) -> str:
        return self._kid

    @property
    def private_key_pem(self) -> str:
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

    def public_jwk(self) -> dict[str, object]:
        """Return the public key as a JWK suitable for a /jwks.json endpoint."""
        import base64

        public_key = self._private_key.public_key()
        public_numbers = public_key.public_numbers()

        def _b64url(x: int) -> str:
            length = (x.bit_length() + 7) // 8
            return (
                base64.urlsafe_b64encode(x.to_bytes(length, "big"))
                .rstrip(b"=")
                .decode()
            )

        return {
            "kty": "RSA",
            "kid": self._kid,
            "use": "sig",
            "alg": "RS256",
            "n": _b64url(public_numbers.n),
            "e": _b64url(public_numbers.e),
        }
