from fastapi import FastAPI, UploadFile, File
from mcp.server.fastmcp import FastMCP
from PIL import Image

import numpy as np

app = FastAPI()
mcp = FastMCP("MultimodalServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}!"

@mcp.post("/mcp/image/brightness")
async def analyze_brightness(file: UploadFile = File(...)):
    """Analyze the brightness of an uploaded image."""
    image = Image.open(file.file).convert("L")
    np_image = np.array(image)
    brightness = np.mean(np_image)
    return {"brightness": brightness, "message": "Image brightness analyzed successfully."}

app.mount("/mcp", mcp)