#############################################################################
# File Name : main_router.py
# Date of creation : 2025-06-24
# Author Name/Dept : Manduva Prapalsha
# Organization : cypher
# Description : Defines the main API routes for the SQL Agent application.
# Python Version : 3.12
# Modified on :
# Modified by :
# Modification Description:
# Copyright :
#############################################################################

import os
import base64
from typing import Optional
from dotenv import load_dotenv
from fastapi import status, HTTPException, Request, APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from app.logger import logger
from app.utils import (
    initialize_database_components, 
    process_chat_query, 
    validate_configuration,
    setup_database,
    CSV_FILE_PATH,
    DATABASE_FILE_PATH
)

load_dotenv()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    image_path: Optional[str] = None
    has_plot: bool = False
    image_base64: Optional[str] = None  # Added for base64 image data

class HealthResponse(BaseModel):
    status: str
    message: str

# Global variables to store initialized components
df = None
db = None
llm = None
agent_executor_SQL = None
pandas_agent = None

router = APIRouter(
    prefix="/api",
    tags=["main"],
)

logger.info("SQL Agent Router Mounted")


##############################################################################
# Name : startup_event
# Description : Initialize database components on startup
# Parameters : None
# Return Values : None
#############################################################################
async def startup_event():
    """Initialize database components on startup."""
    global df, db, llm, agent_executor_SQL, pandas_agent
    
    try:
        if not validate_configuration():
            raise Exception("Configuration validation failed")
            
        df, db, llm, agent_executor_SQL, pandas_agent = initialize_database_components()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


##############################################################################
# Name : encode_image_to_base64
# Description : Convert image file to base64 string
# Parameters : 
#     image_path (str): Path to the image file
# Return Values : Base64 encoded string or None if error
#############################################################################
def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Convert image file to base64 string."""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"
        return None
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        return None


##############################################################################
# Name : health_check
# Description : Health check endpoint to verify service status
# Parameters : None
# Return Values : HealthResponse indicating service status
#############################################################################
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global agent_executor_SQL, pandas_agent
    
    if agent_executor_SQL is None or pandas_agent is None:
        return HealthResponse(
            status="unhealthy",
            message="Agents not initialized"
        )
    
    return HealthResponse(
        status="healthy",
        message="SQL Agent service is running"
    )


##############################################################################
# Name : chat
# Description : Handles chat requests, processes user questions, and returns answers with optional plots
# Parameters : 
#     request (Request): The incoming request object
#     data (ChatRequest): The user input data containing the question
# Return Values : 
#     ChatResponse: Response containing the question, answer, plot information, and base64 image
#     Raises HTTPException: If the question is missing or if an error occurs
#############################################################################
@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, data: ChatRequest):
    """Handle chat requests and return responses with optional plots."""
    global agent_executor_SQL, pandas_agent

    if not data.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Please provide a valid question!"
        )

    # Check if agents are initialized
    if agent_executor_SQL is None or pandas_agent is None:
        await startup_event()

    try:
        final_answer, image_path = process_chat_query(
            data.question,
            agent_executor_SQL,
            pandas_agent
        )

        # --- Ensure answer is always a readable string for the response model ---
        def readable_answer(ans):
            # Remove troubleshooting links and raw tuple/list output
            if isinstance(ans, list):
                if all(isinstance(item, tuple) for item in ans):
                    return "\n".join([" - ".join(map(str, item)) for item in ans])
                elif all(isinstance(item, dict) for item in ans):
                    return "\n".join([f"{item.get('department', '')} - {item.get('count', '')} employees" for item in ans])
                else:
                    return str(ans)
            elif isinstance(ans, tuple):
                return " - ".join(map(str, ans))
            elif isinstance(ans, str):
                # Remove troubleshooting links if present
                ans = ans.split('For troubleshooting, visit:')[0].strip()
                return ans
            else:
                return str(ans)

        final_answer = readable_answer(final_answer)

        # If the answer is a generic LLM response or parsing error, return a user-friendly message
        if (
            not final_answer or
            final_answer.strip().lower().startswith("error in decision-making process") or
            "could not parse" in final_answer.lower() or
            "please provide me with a specific question" in final_answer.lower() or
            "i am an ai assistant designed to interact with a sql database" in final_answer.lower()
        ):
            final_answer = "Sorry, your query could not be processed. Please ask a specific database-related question."

        # Encode image to base64 if plot was generated
        image_base64 = None
        if image_path and os.path.exists(image_path):
            image_base64 = encode_image_to_base64(image_path)

        return ChatResponse(
            question=data.question,
            answer=final_answer,
            image_path=image_path,
            has_plot=image_path is not None,
            image_base64=image_base64
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        # Return a user-friendly error message, not raw exception
        return ChatResponse(
            question=data.question,
            answer="Sorry, there was a problem processing your request. Please try again or contact support.",
            image_path=None,
            has_plot=False,
            image_base64=None
        )


##############################################################################
# Name : get_plot_image
# Description : Serves the generated plot image
# Parameters : None
# Return Values : FileResponse with the plot image or 404 if not found
#############################################################################
@router.get("/plot")
async def get_plot_image():
    """Serve the generated plot image."""
    if os.path.exists('img.png'):
        return FileResponse(
            'img.png', 
            media_type='image/png',
            filename='plot.png'
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot image not found"
        )


##############################################################################
# Name : get_plot_base64
# Description : Returns the plot image as base64 encoded string
# Parameters : None
# Return Values : JSON response with base64 encoded image
#############################################################################
@router.get("/plot/base64")
async def get_plot_base64():
    """Return the plot image as base64 encoded string."""
    if os.path.exists('img.png'):
        try:
            image_base64 = encode_image_to_base64('img.png')
            if image_base64:
                return JSONResponse(content={
                    "image": image_base64,
                    "filename": "plot.png"
                })
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error encoding image"
                )
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing image"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plot image not found"
        )


##############################################################################
# Name : upload_csv
# Description : Upload a new CSV file to replace the current dataset
# Parameters : 
#     file (UploadFile): The CSV file to upload
# Return Values : JSON response indicating success or failure
#############################################################################
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a new CSV file to replace the current dataset."""
    global df, db, llm, agent_executor_SQL, pandas_agent
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Reinitialize with new CSV
        df, db = setup_database(file_path, DATABASE_FILE_PATH)
        
        # Update global CSV path for future use
        global CSV_FILE_PATH
        CSV_FILE_PATH = file_path
        
        logger.info(f"Successfully uploaded and processed: {file.filename}")
        
        return JSONResponse(content={
            "message": f"Successfully uploaded {file.filename}",
            "records_loaded": len(df)
        })
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing uploaded file: {str(e)}"
        )


##############################################################################
# Name : get_database_info
# Description : Get information about the current database
# Parameters : None
# Return Values : JSON response with database information
#############################################################################
@router.get("/database-info")
async def get_database_info():
    """Get information about the current database."""
    global df, db
    
    if df is None or db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    
    try:
        table_names = db.get_usable_table_names()
        
        # Get basic info about the main table
        table_info = {}
        if 'all_states_history' in table_names:
            table_info['all_states_history'] = {
                'columns': list(df.columns),
                'row_count': len(df),
                'data_types': df.dtypes.to_dict()
            }
        
        return JSONResponse(content={
            "tables": table_names,
            "table_info": table_info,
            "database_path": DATABASE_FILE_PATH
        })
        
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving database information: {str(e)}"
        )


##############################################################################
# Name : reset_agents
# Description : Reset and reinitialize the agents
# Parameters : None
# Return Values : JSON response indicating success
#############################################################################
@router.post("/reset-agents")
async def reset_agents():
    """Reset and reinitialize the agents."""
    global df, db, llm, agent_executor_SQL, pandas_agent
    
    try:
        df, db, llm, agent_executor_SQL, pandas_agent = initialize_database_components()
        
        return JSONResponse(content={
            "message": "Agents successfully reset and reinitialized"
        })
        
    except Exception as e:
        logger.error(f"Error resetting agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting agents: {str(e)}"
        )