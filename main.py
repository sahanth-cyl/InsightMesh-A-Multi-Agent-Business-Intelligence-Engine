#############################################################################
# File Name : main.py
# Date of creation : 2025-06-24
# Author Name/Dept : Manduva Prapalsha
# Organization : cypher
# Description : Starts the uvicorn server for the application.
# Python Version : 3.12
# Modified on :
# Modified by :
# Modification Description:
# Copyright : 
#############################################################################

import os
import uvicorn

from dotenv import load_dotenv


load_dotenv()

PORT = int(os.getenv('PORT',8000))
HOST = '0.0.0.0'


##############################################################################
# Name : main
# Description : Entry point of the application. Starts the uvicorn server.
# Parameters : None
# Return Values : None
#############################################################################
if __name__ == '__main__':
    uvicorn.run('app.app:app', host=HOST, port=PORT, reload=True)