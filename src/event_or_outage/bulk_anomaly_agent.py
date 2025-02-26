from smolagents import CodeAgent, LiteLLMModel, tool, LogLevel
from .llm_utils import LLMUtils
from .tools.holidays_api_tool import HolidaysAPITool
from .tools.calendarific_api_tool import CalendarificAPITool
from halo import Halo
from logging import Logger
from .utils import Utils
import os

# TODO: Inherit from CodeAgent
class BulkAnomalyAgent:

    LLM_LOGLEVEL = LogLevel.OFF
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
        if os.getenv('HOLIDAY_API_KEY'):
            tools.append(HolidaysAPITool())
        if os.getenv('CALENDARIFIC_API_KEY'):
            tools.append(CalendarificAPITool())

        agent = CodeAgent(
            tools=tools,
            model=model,
            additional_authorized_imports=[
                "datetime",
                "requests"
            ],
            verbosity_level = self.LLM_LOGLEVEL,
            max_steps=self.LLM_MAX_STEPS_OVERRIDE,
            planning_interval=3
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
                # result = {'analysis': {'US': {'2024-10-19': [{'event': 'Sweetest Day', 'probability': 0.2}], '2024-10-21': [{'event': 'Possible effects of Sweetest Day', 'probability': 0.2}], '2024-10-24': [{'event': 'Shmini Atzeret', 'probability': 0.3}], '2024-10-25': [{'event': 'Halloween preparations', 'probability': 0.6}], '2024-10-31': [{'event': 'Halloween', 'probability': 0.9}], '2024-11-01': [{'event': 'Post-Halloween', 'probability': 0.6}], '2024-11-07': [{'event': 'Unidentified event', 'probability': 0.1}], '2024-11-09': [{'event': 'Unidentified event', 'probability': 0.1}], '2024-11-10': [{'event': "Veteran's Day observed", 'probability': 0.7}], '2024-11-11': [{'event': "Veteran's Day", 'probability': 0.8}], '2024-11-12': [{'event': "Post-Veteran's Day", 'probability': 0.6}]}, 'IN': {'2024-11-02': [{'event': 'Govardhan Puja', 'probability': 0.7}]}}, 'summary': "The traffic drops on Oct 19, Oct 21 and Oct 24 in US are tentatively attributed to Sweetest Day and Shmini Atzeret with probabilities 20% and 30% respectively. The drop on Oct 25 and Nov 1 are likely related to Halloween with a probability of 60%. The traffic drop on Nov 10 and Nov 12 are probably due to Veteran's Day with a probability of 80%. For the date with traffic drop in India, Nov 2, we identified Govardhan Puja as a possible cause with a probability of 70%. Note that these are educated suggestions and further analysis may be required for precise conclusions."}
                spinner.stop()
                all_results.append(result)
            except Exception as e:
                spinner.fail(f'Analysis failed for batch {i+1}')
                continue

        # Combine results from all batches
        combined_result = {
            'analysis': {},
            'summary': []
        }
        for result in all_results:
            try:
                if result.get('analysis'):
                    combined_result['analysis'].update(result['analysis'])
                if result.get('summary'):
                    combined_result['summary'].append(result['summary'])
            except Exception as e:
                self.logger.error(f"Error updating combined result: {e}")
                self.logger.error(f"result was: {result}")
        return combined_result