#############################################################################
# File Name : app.py
# Date of creation : 2025-06-24
# Author Name/Dept : Manduva Prapalsha
# Organization : cypher
# Description : Main application file for the FastAPI app.
# Python Version : 3.12
# Modified on :
# Modified by :
# Modification Description:
# Copyright : 
#############################################################################

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.routers import main_route

load_dotenv()

app = FastAPI(title="cypher Tech CoPilot")
app.include_router(router=main_route.router)

# allowed origins
allowed_origins = [
    "*"
]

#############################################################################
#  Name            : SecurityHeadersMiddleware
# Description      : Middleware to add security headers to HTTP responses.
# Parameters       : BaseHTTPMiddleware
#############################################################################

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    #############################################################################
    # Name           : dispatch
    # Description    : Adds security headers to the HTTP response.
    # Parameters     : request - the incoming HTTP request
    #                  call_next - the next middleware or route handler
    # Return Values  : response - the modified HTTP response with security headers
    #############################################################################
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        if request.url.path != "/docs":
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
                "font-src 'self'; frame-ancestors 'none'"
            )
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        response.headers['X-DNS-Prefetch-Control'] = 'off'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        response.headers['Server'] = 'webserver'
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##############################################################################
# Name : root
# Description : Root endpoint of the application.
# Parameters : None
# Return Values : 
#    str: A message indicating access denied.
#############################################################################
@app.get('/', tags=["Root"])
async def root():
    return "Access Denied!"

@app.on_event("startup")
async def app_startup():
    """Initialize application components on startup"""
    try:
        from app.routers.main_route import startup_event
        await startup_event()
        print("Application startup completed successfully")
    except Exception as e:
        print(f"ERROR during startup: {str(e)}")
        # Don't raise the exception to prevent server shutdown
        import traceback
        traceback.print_exc()