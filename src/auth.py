# src/auth.py
from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from jwt import PyJWKClient

# Initialize once (e.g., in create_app) rather than per-request
def init_cognito(app):
    region = app.config["COGNITO_REGION"]
    pool_id = app.config["COGNITO_USER_POOL_ID"]
    issuer = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    app.config["COGNITO_ISSUER"] = issuer
    app.config["_COGNITO_JWK_CLIENT"] = PyJWKClient(jwks_url)

def _verify_access_token(token: str, app):
    jwk_client: PyJWKClient = app.config["_COGNITO_JWK_CLIENT"]
    issuer: str = app.config["COGNITO_ISSUER"]
    app_client_id: str = app.config["COGNITO_APP_CLIENT_ID"]

    # 1) Get signing key by kid (cached)
    signing_key = jwk_client.get_signing_key_from_jwt(token).key

    # 2) Decode + validate standard fields
    claims = jwt.decode(
        jwt=token,
        key=signing_key,
        algorithms=["RS256"],
        issuer=issuer,
        options={
            "require": ["exp", "iat"],
            "verify_aud": False,   # access tokens usually lack "aud" in Cognito
        },
        leeway=60,  # allow 60s clock skew
    )

    # 3) Cognito-specific checks
    if claims.get("token_use") != "access":
        raise jwt.InvalidTokenError("Not an access token")

    if claims.get("client_id") != app_client_id:
        raise jwt.InvalidTokenError("client_id mismatch")

    return claims

def cognito_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200
        
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing Bearer token"}), 401
        token = auth_header.split(" ", 1)[1]

        try:
            claims = _verify_access_token(token, current_app)
        except Exception as e:
            current_app.logger.warning(f"Cognito auth failed: {e}")
            return jsonify({"message": "Invalid or expired token"}), 401

        # Stash on flask.g for downstream use
        g.jwt = claims
        g.user_sub = claims.get("sub")
        g.username = claims.get("username")
        g.groups = claims.get("cognito:groups", [])
        g.scope = claims.get("scope", "")

        return f(*args, **kwargs)
    return decorated
