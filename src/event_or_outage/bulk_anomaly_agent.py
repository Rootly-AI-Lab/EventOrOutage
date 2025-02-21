from smolagents import CodeAgent, LiteLLMModel, tool, LogLevel
from llm_utils import LLMUtils
from tools.holidays_api_tool import HolidaysAPITool
from tools.calendarific_api_tool import CalendarificAPITool
from halo import Halo
from logging import Logger
from utils import Utils

# TODO: Inherit from CodeAgent
class BulkAnomalyAgent:

    LLM_LOGLEVEL = LogLevel.INFO
    BULK_ANOMALY_PROPERTY_LIMIT = 1
    BULK_ANOMALY_LIMIT = 10 # total anomalies per property
    BULK_ANOMALY_GEO_LIMIT = 3 # total geos (to stagger anomalies across geos else a geo may consume the BULK_ANOMALY_LIMIT, fairly hackish)
    LLM_MAX_STEPS_OVERRIDE = 6
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
        anomaly_property_count = 0
        for website, geo_data in anomaly_candidates.items(): 
            anomaly_geo_count = 0
            if anomaly_property_count >= self.BULK_ANOMALY_PROPERTY_LIMIT:
                    break
            for geo, dates in geo_data.items():
                if anomaly_geo_count >= self.BULK_ANOMALY_GEO_LIMIT:
                    break
                anomaly_count = 0
                for date in dates:
                    property_list.append(f"Website: {website}, Geo: {geo}, Date: {date}")
                    anomaly_count += 1
                    if anomaly_count >= self.BULK_ANOMALY_LIMIT:
                        break
            anomaly_property_count += 1

        model = LLMUtils.get_llm_model(model)
        
        # Split property list 
        batches = [property_list[i:i + self.BULK_LLM_BATCH_SIZE] for i in range(0, len(property_list), self.BULK_LLM_BATCH_SIZE)]
        
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
            if result.get('analysis'):
                combined_result['analysis'].update(result['analysis'])
        return combined_result