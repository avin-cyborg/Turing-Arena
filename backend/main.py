# backend/main.py
import uvicorn

if __name__ == "__main__":
    # This is the entry point to run our backend server.
    # It tells uvicorn where to find our FastAPI application instance.
    # "api.main:app" means: In the 'api' package, inside the 'main' module,
    # find the object named 'app'.
    # reload=True will automatically restart the server when you change the code.
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
