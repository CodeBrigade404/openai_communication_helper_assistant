from fastapi import FastAPI
import uvicorn

from server.api.v1.auth_routes import router as auth_router
from server.api.v1.chat_routes import router as chat_router
from server.api.v1.user_routes import router as user_router

app = FastAPI(
    title="LangChain Chatbot",
    version="1.0",
    description="A chatbot with memory using LangChain and FastAPI"
)

@app.get("/")
async def health_check():
    return "Health check is successful"

# Include routers from the api module
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(user_router, prefix="/api/v1", tags=["user"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

# localhost
# if __name__ == "__main__":
#     uvicorn.run(app, host="localhost", port=9000)

# live
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
