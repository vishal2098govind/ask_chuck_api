from fastapi import FastAPI
from ask_chuck_api.rag.serving_system import handle_query

app = FastAPI()


@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello World"}


@app.get("/query")
async def query(query: str):
    response = await handle_query(query)
    return {
        "response": response,
    }
