from smolagents import CodeAgent, LiteLLMModel, tool, LogLevel
from dotenv import load_dotenv
from utils import Utils
import os
from llm_utils import LLMUtils
from tools.holidays_api_tool import HolidaysAPITool
from tools.calendarific_api_tool import CalendarificAPITool
from halo import Halo
from logging import Logger


# TODO: Inherit from CodeAgent
class SingleAnomalyAgent:
    """
    Agent for handling single anomaly detection and analysis.
    """
    LLM_LOGLEVEL = LogLevel.INFO
    
    
    def __init__(self):
        super().__init__()
        self.logger = Logger('default')
        Utils.load_dotenv()
        Utils.load_templates()['single_event_template']

        
    def troubleshoot(self, duration: str, location: str, industry: str, model: str):
        """
        Process a single anomaly instance.
        
        Args:
            duration: Time period/date to analyze
            location: location/geo of anomaly. Leave blank for worldwide
            model: Model to use for analysis. Supported models are gpt and claude.
        """
        
        model = LLMUtils.get_llm_model(model)
        tools = []
        tools.append(HolidaysAPITool())
        tools.append(CalendarificAPITool())
        agent = CodeAgent(
            tools=tools,
            model=model,
            additional_authorized_imports=[
                "datetime",
                "requests"
            ],
            verbosity_level=self.LLM_LOGLEVEL
        )
        if (single_event_template := Utils.load_templates()['single_event_template']):
            prompt = single_event_template.format(industry=industry, duration = duration, location = location)
        else:
            raise ValueError("Single event template not found")
        spinner = Halo(text='Analyzing anomaly...', spinner='dots')
        self.logger.info(prompt)
        
        spinner.start()
        try:
            result = agent.run(prompt)
            spinner.stop()

        except Exception as e:
            spinner.fail(f'Analysis failed')    
        
        return result