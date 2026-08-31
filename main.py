import os
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.groq import Groq

# --- Загрузка переменных окружения и настройка параметров ---
load_dotenv()

Settings.llm = Groq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY")
)

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text"
)

# --- Загрузка пользовательских данных ---
print("📂 Loading custom documents about project...")
documents = SimpleDirectoryReader("./data").load_data()
print(f"✅ Loaded {len(documents)} document(s).")

# --- Создание индекса и движка запросов ---
print("📊 Creating index and query engine...")
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(similarity_top_k=1)
print("✅ Basic RAG Pipeline is Ready.")

# --- Тестирование ---
response = query_engine.query("Кто такая Сара?")

print("\n--- Query ---")
print("Кто такая Сара?")

print("\n--- Response ---")
print(response)
