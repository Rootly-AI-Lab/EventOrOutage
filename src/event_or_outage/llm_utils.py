from smolagents import LiteLLMModel
import os

class LLMUtils:
    def __init__(self):
        pass

    def get_llm_model(model: str) -> LiteLLMModel:
        """Get the LLM model based on the model type.
        
        Args:
            model: Model type ('gpt' or 'claude')
        Returns:
            LiteLLMModel: Configured model instance
        """
        match model:
            case model if model.startswith("claude"):
                return LiteLLMModel(
                    model="anthropic/" + model,
                    api_key=os.environ["ANTHROPIC_API_KEY"]
                )
            case model if model.startswith("gpt"):
                return LiteLLMModel(
                    model_id=model,
                    api_base="https://api.openai.com/v1",
                    api_key=os.environ["OPENAI_API_KEY"]
                )
            case model if model.startswith("gemini"):
                return LiteLLMModel(
                    model="google/" + model,
                    api_key=os.environ["GEMINI_API_KEY"]
                )
            case _:
                raise ValueError(f"Unsupported model type: {model}")