import os

import uvicorn
from main import app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"Starting Digital Sarathi API on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
