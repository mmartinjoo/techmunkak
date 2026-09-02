from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from techmunkak.core.config import settings

model = init_chat_model(
    model=settings.translate_llm_model,
    model_provider=settings.translate_llm_provider,
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