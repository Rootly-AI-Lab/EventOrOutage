from smolagents import CodeAgent, LiteLLMModel, tool, LogLevel
from .llm_utils import LLMUtils
from .tools.holidays_api_tool import HolidaysAPITool
from .tools.calendarific_api_tool import CalendarificAPITool
from halo import Halo
from logging import Logger
from .utils import Utils

# TODO: Inherit from CodeAgent
class BulkAnomalyAgent:

    LLM_LOGLEVEL = LogLevel.INFO
    LLM_MAX_STEPS_OVERRIDE = 10
    BULK_LLM_BATCH_SIZE = 25

    def __init__(self):
        self.anomalies = []
        self.logger = Logger('default')
        Utils.load_dotenv()
        
    def troubleshoot(self, anomaly_candidates, model: str):
        """Analyze bulk anomalies and provide detailed analysis.
        
        Args:
            anomaly_candidates: Dictionary containing websites, their geos, and anomalous dates
        """
        property_list = []

        for geo, dates in anomaly_candidates.items():
            for date in dates:
                property_list.append(f"Country: {geo}, Date: {date}")

        model = LLMUtils.get_llm_model(model)
        self.logger.info(f"Analyzing {len(property_list)} anomalies")
        # Split property list 
        batches = [property_list[i:i + self.BULK_LLM_BATCH_SIZE] for i in range(0, len(property_list), self.BULK_LLM_BATCH_SIZE)]
        
        tools = []
        # tools.append(HolidaysAPITool()) # enable if you have a premium account for holidayapi.com
        tools.append(CalendarificAPITool())

        agent = CodeAgent(
            tools=tools,
            model=model,
            additional_authorized_imports=[
                "datetime",
                "requests"
            ],
            verbosity_level = self.LLM_LOGLEVEL,
            max_steps=self.LLM_MAX_STEPS_OVERRIDE
        )

        # Process each batch
        all_results = []
        
        for i, batch in enumerate(batches):
            spinner = Halo(text='Analyzing anomalies (batch ' + str(i+1) + ' of ' + str(len(batches)) + ')...', spinner='dots')
            batch_list = '\n'.join(batch)
            if (bulk_event_template := Utils.load_templates()['bulk_analysis_template']):
                prompt = bulk_event_template.format(anomalies_list=batch_list)
            else:
                raise ValueError("Single event template not found")
            self.logger.info(prompt)
            
            spinner.start()
            try:
                result = agent.run(prompt)
                spinner.stop()
                all_results.append(result)
            except Exception as e:
                spinner.fail(f'Analysis failed for batch {i+1}')
                continue

        # Combine results from all batches
        combined_result = {
            'analysis': {}
        }
        for result in all_results:
            try:
                if result.get('analysis'):
                    combined_result['analysis'].update(result['analysis'])
            except Exception as e:
                self.logger.error(f"Error updating combined result: {e}")
                self.logger.error(f"result was: {result}")
        return combined_result