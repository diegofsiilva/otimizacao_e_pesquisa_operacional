import uvicorn
from pathlib import Path
from config import APP_HOST, APP_PORT

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True,
        reload_dirs=[str(Path(__file__).resolve().parent)],
        app_dir=str(Path(__file__).resolve().parent),
    )
