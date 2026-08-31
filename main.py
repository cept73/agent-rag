import os
import asyncio
import json
import re
from dotenv import load_dotenv
try:
    from llama_index import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
    )
    from llama_index.core.agent import FunctionAgent
    from llama_index.core.tools import QueryEngineTool
except ImportError:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        Settings,
    )
    from llama_index.core.agent import FunctionAgent
    from llama_index.core.tools import QueryEngineTool

from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.groq import Groq

def output(success, answer=None, answers=None):
    result = {"success": success}
    if answers is not None:
        result["answers"] = answers
    else:
        result["answer"] = answer or ""
    print(json.dumps(result, ensure_ascii=False))


def clean_answer(value):
    text = str(value).strip()
    text = re.sub(r"^assistant:\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def friendly_error(exc, phase):
    text = str(exc).lower()
    if isinstance(exc, (ConnectionError, TimeoutError)) or any(
        marker in text for marker in ("connection", "connect", "timed out", "timeout", "refused", "unreachable", "502", "503", "504")
    ):
        if phase == "startup":
            return "Не удалось подключиться к Ollama. Запустите Ollama и убедитесь, что модель nomic-embed-text установлена."
        return "Не удалось получить ответ от внешнего сервиса. Проверьте подключение к Groq и Ollama."
    if "api key" in text or "authentication" in text or "401" in text:
        return "Не удалось подключиться к Groq: проверьте переменную GROQ_API_KEY."
    if "429" in text or "rate limit" in text:
        return "Сервис Groq временно ограничил запросы. Повторите попытку позже."
    if isinstance(exc, TypeError):
        if phase == "startup":
            return "Не удалось подключиться к Ollama. Запустите Ollama и убедитесь, что модель nomic-embed-text установлена."
        return "Не удалось получить ответ от внешнего сервиса. Проверьте подключение к Groq."
    if phase == "startup":
        return "Не удалось запустить RAG-сервис. Проверьте настройки Groq, Ollama и доступность модели."
    return "Не удалось обработать запрос. Проверьте настройки внешних сервисов."


async def run_agent(queries):
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        load_dotenv(dotenv_path=env_path)
        Settings.llm = Groq(
            model="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=512,
            reasoning_effort="low",
        )
        Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
        documents = SimpleDirectoryReader("./data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine(similarity_top_k=5)
        rag_tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            name="project_rag_tool",
            description="Search Project documents for facts about its lead, goals, timeline, or technical details.",
        )
        agent = FunctionAgent(
            tools=[rag_tool],
            llm=Settings.llm,
            system_prompt="Answer briefly and accurately in Russian. Use project_rag_tool for Project questions. Return only the final answer.",
            verbose=False,
            streaming=False,
            timeout=60,
            allow_parallel_tool_calls=False,
            early_stopping_method="generate",
        )
    except Exception as exc:
        output(False, friendly_error(exc, "startup"))
        return

    answers = []
    for query in queries:
        try:
            response = await agent.run(user_msg=query, max_iterations=3)
            answers.append(clean_answer(getattr(response, "response", response)))
        except Exception as exc:
            output(False, friendly_error(exc, "query"))
            return

    if len(answers) == 1:
        output(True, answer=answers[0])
    else:
        output(True, answers=answers)

queries = [
    "Кто руководит проектом?",
    "На сколько лет Сара младше Ясмины?",
]
# Run the async function
asyncio.run(run_agent(queries))
