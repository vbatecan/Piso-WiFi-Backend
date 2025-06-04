import os

import controllers.device_controller as device_controller
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# * Routers
app.include_router(device_controller.router, prefix="/device", tags=["devices"])

if __name__ == '__main__':
    if not os.path.exists("database.db"):
        print("Database not found! Please go to config folder and run init.py to initialize database.")
        exit(1)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)