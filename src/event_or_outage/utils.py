from dotenv import load_dotenv
import os
import yaml
from smolagents import LiteLLMModel
class Utils:
    def __init__(self):
        pass
    @staticmethod
    def load_dotenv():
        # Load environment variables from .env file in current working directory
        env_path = os.path.join(os.getcwd(), '.env')
        load_dotenv(env_path)
        # FIXME: how to load env variables for includes.
        # Set default environment variables
        if os.getenv("OPENAI_API_KEY"):
            os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        if os.getenv("ANTHROPIC_API_KEY"):
            os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
        if os.getenv("GEMINI_API_KEY"):
            os.environ.setdefault("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        if os.getenv("HOLIDAY_API_KEY"):
            os.environ.setdefault("HOLIDAY_API_KEY", os.getenv("HOLIDAY_API_KEY"))
        if os.getenv("CALENDARIFIC_API_KEY"):
            os.environ.setdefault("CALENDARIFIC_API_KEY", os.getenv("CALENDARIFIC_API_KEY"))

    @staticmethod
    def load_templates():
        # Load prompt templates
        # Get the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, 'prompt_templates.yaml')
        with open(template_path, 'r') as file:
            prompt_templates = yaml.safe_load(file)

        # Get templates
        return {
            'single_event_template': prompt_templates['single_event']['template'],
            'bulk_analysis_template': prompt_templates['bulk_analysis']['template']
        }


        