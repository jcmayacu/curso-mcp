import asyncio
import os
import shutil

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

def get_azure_open_ai_client():
    """
    Crea y regresa una instancia de cliente de Azure OpenAI.
    
    Returns:
        AsyncAzureOpenAI: Configura al cliente de Azure OpenAI
    """
    load_dotenv()
    
    return AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

async def run(mcp_server: MCPServer):

    azure_open_ai_client = get_azure_open_ai_client()
    set_tracing_disabled(disabled=True)

    agent = Agent(
        name="Asistente de Archivos",
        instructions="Usa las herramientas para leer los archivos del sistema y responder preguntas basadas en esos archivos.",
        model=OpenAIChatCompletionsModel(model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"), 
                                         openai_client=azure_open_ai_client),
        mcp_servers=[mcp_server],
    )

    message = "Lee los archivos en la carpeta `sample_files` y enlista los nombres de los archivos."
    print(f"Ejecutando: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "Cuál es mi libro favorito? Mira el archivo `favorite_books.txt`."
    print(f"\n\Ejecutando: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "Mira mis canciones favoritas. Sugiere una canción que podría gustarme."
    print(f"\n\Ejecutando: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")

    async with MCPServerStdio(
        name="Filesystem Server, via npx",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())