#############################################################################
# File Name : schemas.py
# Date of creation : 2025-06-24
# Author Name/Dept : Manduva Prapalsha
# Organization : cypher
# Description : Defines Pydantic models for request and response schemas.
# Python Version : 3.12
# Modified on :
# Modified by :
# Modification Description:
# Copyright :
#############################################################################

from pydantic import BaseModel


##############################################################################
# Name : User
# Description : Pydantic model for user input (question and index name).
# Parameters :
#     question: A list representing the user's question.
#     index_name: A string representing the index name.
#############################################################################
class Chat(BaseModel):
    question: str
    index_name: str


##############################################################################
# Name : UserChat
# Description : Pydantic model for user input (question and index name).
# Parameters :
#     question: A list representing the user's question.
#     index_name: A string representing the index name.
#############################################################################
class UserChat(BaseModel):
    question: list
    index_name: str
