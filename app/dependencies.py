# #############################################################################
# # File Name : dependencies.py
# # Date of creation : 2025-06-24
# # Author Name/Dept : Manduva Prapalsha
# # Organization : cypher
# # Description : Defines dependencies for authentication and authorization.
# # Python Version : 3.12
# # Modified on :
# # Modified by :
# # Modification Description:
# # Copyright : 
# #############################################################################

# import os
# import jwt

# from fastapi import HTTPException, status, Security
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
#...existing code...
# from jwt import PyJWKClient
# from dotenv import load_dotenv


# from app.logger import logger
# load_dotenv()

# # --- Initialize Key Vault and retrieve secrets ---
# ##############################################################################
# # Name : init_key_vault
# # Description : Initializes the Key Vault client and retrieves secrets.
# # Parameters : None
# # Return Values : Tuple containing CLIENT_SECRET, TENANT_ID, CLIENT_ID
# #############################################################################
# def init_key_vault():
#     # mic = ManagedIdentityCredential()
#     # secret_client = SecretClient(vault_url=os.getenv("VAULT_URL"), credential=mic)
#     # client_secret = secret_client.get_secret("SECRETKEYCYPHER").value
#     # tenant_id = secret_client.get_secret("TENANTID").value
#     # client_id = secret_client.get_secret("CLIENTID").value

#     client_secret = os.getenv("SECRETKEYCYPHER")
#     tenant_id = os.getenv("TENANTID")
#     client_id = os.getenv("CLIENTID")
#     return client_secret, tenant_id, client_id

# CLIENT_SECRET, TENANT_ID, CLIENT_ID = init_key_vault()



# ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
# JWK_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

# security = HTTPBearer()


# ##############################################################################
# # Name : verify_token
#...existing code...
# # Parameters : 
# #    token (str): The JWT token to verify.
# # Return Values : 
# #    dict: The decoded JWT payload if the token is valid.
# #    Raises HTTPException: If the token is invalid or expired.
# #############################################################################
# def verify_token(token: str):
#     try:
#         jwk_client = PyJWKClient(JWK_URL)
#         signing_key = jwk_client.get_signing_key_from_jwt(token=token)

#         payload = jwt.decode(
#             token,
#             signing_key.key,
#             algorithms=["RS256"],
#             audience=CLIENT_ID,
#             issuer=ISSUER
#         )

#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
#         )
#     except Exception as e:
#         try:
#             payload = jwt.decode(
#                 token,
#                 CLIENT_SECRET,
#                 algorithms=['HS256'],
#                 audience=CLIENT_ID,
#                 options={"verify_exp": True}
#             )

#             return payload
#         except jwt.ExpiredSignatureError:
#             logger.info("Token has expired")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired! Please close the tab and relogin."
#             )
#         except jwt.InvalidTokenError as e:
#             logger.info(f"Invalid token: {str(e)}")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Not Authorized"
#             )
#         except Exception as e:
#             logger.info(f"Token validation error: {str(e)}")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail=f"Validation error"
#             )


# ##############################################################################
# # Name : get_current_user
# # Description : Dependency function to retrieve the currently logged-in user.
# # Parameters :
# #    credentials: HTTPAuthorizationCredentials obtained from the security scheme.
# # Return Values : 
# #    dict: The decoded JWT payload representing the current user.
# #############################################################################
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
#     token = credentials.credentials
#     return verify_token(token=token)


async def get_current_user():
    return {"user": "anonymous"}