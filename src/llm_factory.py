import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler
from .config import config

class LLMFactory:
    def __init__(self):
        # Check env var set by app.py or .env
        env_trace = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
        self.tracing = env_trace
        self.handler = None
        
        if self.tracing:
            pk = os.getenv("LANGFUSE_PUBLIC_KEY")
            sk = os.getenv("LANGFUSE_SECRET_KEY")
            if pk and sk:
                try:
                    self.handler = CallbackHandler()
                    print("✅ Langfuse Tracing Initialized")
                except Exception as e:
                    print(f"⚠️ Langfuse Init Failed: {e}")
                    self.tracing = False

    def get_llm(self, provider: str, model_name: str):
        api_key = config.get_api_key(provider)
        callbacks = [self.handler] if self.handler and self.tracing else []
        
        if provider == "groq":
            return ChatGroq(model=model_name, groq_api_key=api_key, callbacks=callbacks, temperature=0.2)
        elif provider == "google":
            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, callbacks=callbacks)
        
        # Fallback
        return ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=config.get_api_key("groq"), callbacks=callbacks)

    def is_tracing_enabled(self):
        return self.tracing

llm_factory = LLMFactory()