from jwcrypto import jwk
key = jwk.JWK.generate(kty="RSA", size=2048, alg='RSA-OAEP-256', use='enc', kid='OpenID Connect Playground')

public_key = key.export_public()
private_key = key.export_private()

print(f"Public Key: {public_key}")
print(f"Private Key: {private_key}")