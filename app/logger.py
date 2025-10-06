#############################################################################
# File Name : logger.py
# Date of creation : 2025-06-24
# Author Name/Dept : Manduva Prapalsha
# Organization : cypher
# Description : Configures the logger for the application.
# Python Version : 3.12
# Modified on :
# Modified by :
# Modification Description:
# Copyright : 
#############################################################################

import logging

##############################################################################
# Name : setup_logger
# Description : Sets up the logger with stream and file handlers.
# Parameters : None
# Return Values : logging.Logger object
#############################################################################
def setup_logger():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("router.log")

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger() # Initialize the logger