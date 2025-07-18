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
    
@mcp.tool()
async def news_search(query: str, num_results: int = DEFAULT_RESULTS_LIMIT, ctx: Context = None) -> Dict[str, Any]:
    """
    Realiza una búsqueda de noticias utilizando SerpApi.
    """
    
    await ctx.info(f"Realizando búsqueda de noticias para: {query} con {num_results} resultados")

    try:
        params = {
        "q": query,
        "num": num_results,
        "engine": "google_news"
        }

        response_data = await make_serpapi_request(ctx, params)

        news_results = response_data.get("news_results", [])
        if not news_results:
            await ctx.info("No se encontraron resultados de noticias.")
            return "No se encontraron resultados de noticias."
        
        formatted_results = []
        for i, result in enumerate(news_results[:num_results]):
            formatted_results.append(
                f"## {i+1}. {result.get('title', 'Sin título')}\n"
                f"**Source**: {result.get('source', 'Sin fuente')}\n"
                f"**Date**: {result.get('date', 'Sin fecha')}\n"
                f"**Link**: {result.get('link', 'Sin enlace')}\n"
                f"**Snippet**: {result.get('snippet', 'Sin resumen')}\n"
            )
        await ctx.info(f"Se encontraron {len(news_results)} resultados de noticias.")
        return "\n\n".join(formatted_results)
    except Exception as e:
        await ctx.error(f"Error al realizar la búsqueda de noticias: {str(e)}")
        return f"Error al realizar la búsqueda de noticias: {str(e)}"

@mcp.tool()
async def product_search(query: str, num_results: int = DEFAULT_RESULTS_LIMIT, ctx: Context = None) -> Dict[str, Any]:
    """
    Realiza una búsqueda de productos utilizando SerpApi.
    """
    
    await ctx.info(f"Realizando búsqueda de productos para: {query} con {num_results} resultados")

    try:
        params = {
            "q": query,
            "num": num_results,
            "engine": "google_shopping",
            "shopping_intent": "high"
        }

        response_data = await make_serpapi_request(ctx, params)

        product_results = response_data.get("shopping_results", [])
        if not product_results:
            await ctx.info("No se encontraron resultados de productos.")
            return "No se encontraron resultados de productos."
        
        formatted_results = []
        for i, result in enumerate(product_results[:num_results]):
            formatted_results.append(
                f"## {i+1}. {result.get('title', 'Sin título')}\n"
                f"**Price**: {result.get('price', 'Sin precio')}\n"
                f"**Rating**: {result.get('rating', 'Sin calificación')}\n"
                f"({result.get('reviews', 'Sin reseñas')})\n"
                f"**Source**: {result.get('source', 'Sin fuente')}\n"
                f"**Link**: {result.get('link', 'Sin enlace')}\n"
            )
        await ctx.info(f"Se encontraron {len(product_results)} resultados de productos.")
        return "\n\n".join(formatted_results)
    except Exception as e:
        await ctx.error(f"Error al realizar la búsqueda de productos: {str(e)}")
        return f"Error al realizar la búsqueda de productos: {str(e)}"

@mcp.tool()
async def qna(question: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Realiza una búsqueda de preguntas y respuestas utilizando SerpApi.
    """
    
    await ctx.info(f"Realizando búsqueda de preguntas y respuestas para: {question}")

    try:
        params = {
            "q": question,
            "engine": "google",
        }

        response_data = await make_serpapi_request(ctx, params)

        answer_results = response_data.get("answer_box", {})

        if answer_results:
            await ctx.info("Se encontró una respuesta directa.")
            if "answer" in answer_results:
                return f"**Respuesta**: {answer_results['answer']}\n\n"
            elif "snippet" in answer_results:
                return f"**Respuesta**: {answer_results['snippet']}\n\n"
            elif "snippet_highlighted_words" in answer_results:
                return f"**Respuesta**: {' '.join(answer_results['snippet_highlighted_words'])}\n\n"
        
        knowledge_results = response_data.get("knowledge_graph", {})
        if knowledge_results and "description" in knowledge_results:
            await ctx.info("Se encontró información en el grafo de conocimiento.")
            return f"**Descripción**: {knowledge_results['description']}\n\n"
        
        if "featured_snippet" in response_data:
            featured_snippet = response_data["featured_snippet"]
            if "text" in featured_snippet:
                await ctx.info("Se encontró un fragmento destacado.")
                return f"**Fragmento destacado**: {featured_snippet['text']}\n\n"
        
        related_questions = response_data.get("related_questions", [])
        if related_questions:
            await ctx.info("Se encontraron preguntas relacionadas.")
            formatted_questions = []
            for i, question in enumerate(related_questions):
                formatted_questions.append(
                    f"## {i+1}. {question.get('question', 'Sin pregunta')}\n"
                    f"**Link**: {question.get('link', 'Sin enlace')}\n"
                )
            return "\n\n".join(formatted_questions)
        
        organic_results = response_data.get("organic_results", [])
        if organic_results:
            await ctx.info("Se encontraron resultados orgánicos.")
            formatted_results = []
            for i, result in enumerate(organic_results[:5]):
                formatted_results.append(
                    f"## {i+1}. {result.get('title', 'Sin título')}\n"
                    f"**Link**: {result.get('link', 'Sin enlace')}\n"
                    f"**Snippet**: {result.get('snippet', 'Sin resumen')}\n"
                )
            return "\n\n".join(formatted_results)
    except Exception as e:
        await ctx.error(f"Error al realizar la búsqueda de preguntas y respuestas: {str(e)}")
        return f"Error al realizar la búsqueda de preguntas y respuestas: {str(e)}"