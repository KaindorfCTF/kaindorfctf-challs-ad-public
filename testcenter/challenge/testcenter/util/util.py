import base64
import zlib
import base45
import cbor2

from base45 import b45encode
from cose.algorithms import Es256, Ps256
from cose.headers import Algorithm
from cose.headers import KID
from cose.keys import CoseKey
from cose.keys.curves import P256
from cose.keys.keyparam import EC2KpD
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN
from cose.keys.keyparam import KpKty
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.messages import CoseMessage
from cose.messages import Sign1Message
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.utils import int_to_bytes

from model import db
from model.TrustedKeys import TrustedKey


def get_kids() -> dict:
    kids = {}
    trustedkeys = TrustedKey.query.all()

    for trustedkey in trustedkeys:
        cert = x509.load_pem_x509_certificate(trustedkey.public_key.encode())
        pub = cert.public_key()

        fingerprint = cert.fingerprint(hashes.SHA256())
        keyid = fingerprint[0:8]
        kid_b64 = base64.b64encode(keyid).decode("ASCII")

        if isinstance(pub, RSAPublicKey):
            kids[kid_b64] = CoseKey.from_dict(
                {
                    KpKty: KtyRSA,
                    KpAlg: Ps256,
                    RSAKpE: int_to_bytes(pub.public_numbers().e),
                    RSAKpN: int_to_bytes(pub.public_numbers().n)
                })
        elif isinstance(pub, EllipticCurvePublicKey):
            kids[kid_b64] = CoseKey.from_dict(
                {
                    KpKty: KtyEC2,
                    EC2KpCurve: P256,
                    KpAlg: Es256,
                    EC2KpX: pub.public_numbers().x.to_bytes(32, byteorder="big"),
                    EC2KpY: pub.public_numbers().y.to_bytes(32, byteorder="big")
                })
        else:
            print(f"Skipping unexpected/unknown key type (keyid={kid_b64}, {pub.__class__.__name__}).")

    return kids


def verify(message) -> bool:
    kids = get_kids()

    given_kid = None
    if KID in message.phdr.keys():
        given_kid = message.phdr[KID]
    else:
        given_kid = message.uhdr[KID]

    given_kid_b64 = base64.b64encode(given_kid).decode('ASCII')

    if not given_kid_b64 in kids:
        print(f"KeyID is unknown (kid={given_kid_b64}) -- cannot verify.")
        return False

    key = kids[given_kid_b64]
    message.key = key
    return message.verify_signature()


def generate_signup_cert(username, password, is_admin):
    jp = {"username": username, "password": password, "is_admin": is_admin}
    payload = cbor2.dumps(jp)

    trusted_key = TrustedKey.get_signup_key()

    cert = x509.load_pem_x509_certificate(trusted_key.public_key.encode())
    fingerprint = cert.fingerprint(hashes.SHA256())
    keyid = fingerprint[0:8]

    keyfile = load_pem_private_key(trusted_key.private_key.encode(), password=None)
    priv = keyfile.private_numbers().private_value.to_bytes(32, byteorder="big")

    msg = Sign1Message(phdr={Algorithm: Es256, KID: keyid}, payload=payload)
    cose_key = {
        KpKty: KtyEC2,
        KpAlg: Es256,
        EC2KpCurve: P256,
        EC2KpD: priv,
    }

    msg.key = CoseKey.from_dict(cose_key)
    out = msg.encode()
    out = zlib.compress(out, 9)
    out = b45encode(out).decode()

    return out


def parse_signup_cert(cert: bytes):
    try:
        b45decoded = base45.b45decode(cert)
        decompressed = zlib.decompress(b45decoded)
        message = CoseMessage.decode(decompressed)
        data = cbor2.loads(message.payload)
        return data
    except ValueError:
        return None


def import_trusted_keys(pub: bytes, priv: bytes) -> bool:
    try:
        public_key = pub.decode()
        private_key = priv.decode()
    except UnicodeDecodeError:
        return False

    if public_key.startswith("-----BEGIN CERTIFICATE-----") and private_key.startswith(
            "-----BEGIN EC PRIVATE KEY-----"):
        trustedkey = TrustedKey(public_key, private_key)
        db.session.add(trustedkey)
        db.session.commit()
        return True
    else:
        return False
