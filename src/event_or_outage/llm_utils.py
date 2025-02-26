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
                if os.environ["ANTHROPIC_API_KEY"] is None:
                    raise ValueError(
                        "ANTHROPIC_API_KEY is not set. "
                        "Either set it as an environment variable "
                        "or add it to a .env file in the directory "
                        "you are executing from."
                    )
                return LiteLLMModel(
                    model="anthropic/" + model,
                    api_key=os.environ["ANTHROPIC_API_KEY"],
                    temperature=0.2
                )
            case model if model.startswith("gpt"):
                if os.environ["OPENAI_API_KEY"] is None:
                    raise ValueError(
                        "OPENAI_API_KEY is not set. "
                        "Either set it as an environment variable "
                        "or add it to a .env file in the directory "
                        "you are executing from."
                    )
                return LiteLLMModel(
                    model_id=model,
                    api_base="https://api.openai.com/v1",
                    api_key=os.environ["OPENAI_API_KEY"],
                    temperature=0.2
                )
            case model if model.startswith("gemini"):
                if os.environ["GEMINI_API_KEY"] is None:
                    raise ValueError(
                        "GEMINI_API_KEY is not set. "
                        "Either set it as an environment variable "
                        "or add it to a .env file in the directory "
                        "you are executing from."
                    )
                return LiteLLMModel(
                    model="google/" + model,
                    api_key=os.environ["GEMINI_API_KEY"],
                    temperature=0.2
                )
            case _:
                raise ValueError(f"Unsupported model type: {model}")