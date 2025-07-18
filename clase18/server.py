import os
import json
import httpx
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

logging.basicConfig(
    level=logging.INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    logger.error("La variable de SERPAPI_KEY no fue encontrada. Por favor, configura tu llave de SerpApi en el archivo .env.")
    raise EnvironmentError("SERPAPI_KEY environment variable ir required")

SERPAPI_BASE_URL = "https://serpapi.com/search"
DEFAULT_TIMEOUT = 10.0
DEFAULT_RESULTS_LIMIT = 5

mcp = FastMCP("WebSearchServer")

async def make_serpapi_request (ctx: Context, params: Dic[str, Any]) -> Dict[str, Any]:
    """
    Realiza una solicitud a la API de SerpApi.
    """
    request_params = {**params, "api_key": SERPAPI_KEY}
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            await ctx.info(f"Making SerpAPI request with engine: {params.get('engine', 'google')}")
            response = await client.get(SERPAPI_BASE_URL, params=request_params)
            response.raise_for_status()
            data = response.json()
            await ctx.info(f"Received response from SerpAPI")
            return data
    except httpx.TimeoutException:
        await ctx.error("La solicitud a SerpApi ha excedido el tiempo de espera.")
        raise Exception("Request to SerpApi timed out")
    except httpx.RequestError as e:
        await ctx.error(f"Error al realizar la solicitud a SerpApi: {e}")
        raise Exception(f"Request to SerpApi failed: {e}")
    except httpx.HTTPStatusError as e:
        await ctx.error(f"Error de estado HTTP al realizar la solicitud a SerpApi: {e.response.status_code} - {e.response.text}")
        raise Exception(f"HTTP error from SerpApi: {e.response.status_code}")
    except json.JSONDecodeError:
        await ctx.error("Error al decodificar la respuesta JSON de SerpApi.")
        raise Exception("Failed to decode JSON response from SerpApi")
    
@mcp.action()
async def general_search(query: str, num_results: int = DEFAULT_RESULTS_LIMIT, ctx: Context = None) -> Dict[str, Any]:
    """
    Realiza una búsqueda general en la web utilizando SerpApi.
    """
    params = {
        "q": query,
        "num": num_results,
        "engine": "google"
    }
    
    await ctx.info(f"Realizando búsqueda general para: {query} con {num_results} resultados")

    try:
        params = {
            "q": query,
            "num": num_results,
            "engine": "google"
        }

        response_data = await make_serpapi_request(ctx, params)

        organic_results = response_data.get("organic_results", [])
        if not organic_results:
            await ctx.info("No se encontraron resultados orgánicos.")
            return "No se encontraron resultados orgánicos."
        
        formatted_results = []
        for i, result in enumerate(organic_results[:num_results]):
            formatted_results.append(
                f"## {i+1}. {result.get('title', 'Sin título')}\n"
                f"**Link**: {result.get('link', 'Sin enlace')}\n"
                f"**Snippet**: {result.get('snippet', 'Sin resumen')}\n"
            )
        await ctx.info(f"Se encontraron {len(organic_results)} resultados orgánicos.")
        return "\n\n".join(formatted_results)
    except Exception as e:
        await ctx.error(f"Error al realizar la búsqueda general: {str(e)}")
        return f"Error al realizar la búsqueda general: {str(e)}"