"""Project launcher. All backend implementation lives in backend/app.py."""
import os

from backend.app import app


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
