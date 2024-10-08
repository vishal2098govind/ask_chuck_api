from fastapi import FastAPI
from ask_chuck_api.rag.handle_query import handle_query
from ask_chuck_api.rag.handle_conversation import handle_conversation
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello World"}


@app.get("/query")
async def query(query: str):
    response = await handle_query(query)
    return response


@app.get("/converse")
async def converse(query: str, session_id: str, user_id: str):
    response = await handle_conversation(query, session_id, user_id)
    return response
