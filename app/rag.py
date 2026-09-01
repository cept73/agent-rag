import os
import re
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.agent import FunctionAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.groq import Groq
from . import db


def clean_answer(value):
    return re.sub(r"^assistant:\s*", "", str(value).strip(), flags=re.I).strip()


async def search(slot, queries):
    rows = db.get_slot_materials(slot)
    if not rows:
        return {"success": False, "answer": f"В слоте '{slot}' нет материалов."}
    Settings.llm = Groq(
        model="openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=512,
        reasoning_effort="low",
    )
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    docs = [
        Document(text=row["content"], metadata={"name": row["name"], "slot": slot})
        for row in rows
    ]
    index = VectorStoreIndex.from_documents(docs)
    tool = QueryEngineTool.from_defaults(
        query_engine=index.as_query_engine(similarity_top_k=5),
        name="slot_rag_tool",
        description=f"Search only materials in slot '{slot}'.",
    )
    agent = FunctionAgent(
        tools=[tool],
        llm=Settings.llm,
        system_prompt="Answer briefly and accurately in Russian using only the selected slot materials. Return only the final answer.",
        verbose=False,
        streaming=False,
        timeout=60,
        allow_parallel_tool_calls=False,
        early_stopping_method="generate",
    )
    answers = []
    for query in queries:
        response = await agent.run(user_msg=query, max_iterations=3)
        answers.append(clean_answer(getattr(response, "response", response)))
    return {"success": True, "answers": answers}
