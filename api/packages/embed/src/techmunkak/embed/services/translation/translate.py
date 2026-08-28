from langchain.chat_models import init_chat_model
from langchain_mistralai import ChatMistralAI
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

model = init_chat_model(
    model="ministral-14b-2512",
    model_provider="mistralai",
    temperature=0,
)

class TranslationOutput(BaseModel):
    translated_text: str = Field(description="The translated text to English")
    source_language: str = Field(description="The source language")
    
def translate(text: str) -> TranslationOutput:
    response = model.with_structured_output(TranslationOutput).invoke(
        f"Translate the following text to English. Text: '{text}'",
    )
    return response