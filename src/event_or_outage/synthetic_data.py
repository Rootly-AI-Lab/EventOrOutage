import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from smolagents import CodeAgent, LiteLLMModel
from logging import Logger
import os
from markdown_generator import MarkdownGenerator
from utils import Utils
from smolagents import LogLevel
class SyntheticData:
    LLM_LOGLEVEL = LogLevel.INFO
    def __init__(self):
        self.logger = Logger('default')
        Utils.load_dotenv()
        OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")

    def generate(self, output_dir: str):
        # Constants
        WEBSITES = [
            "runbook.com"
        ]
        GEOS = ["US", "India"] 
        # ["US", "India", "UK", "Canada", "Australia", "New Zealand", 
        # "Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru", 
        # "Venezuela", "Ecuador", "Paraguay", "Uruguay", "Bolivia", 
        # "Costa Rica", "Dominican Republic", "El Salvador", "Guatemala", 
        # "Honduras", "Nicaragua", "Panama", "Puerto Rico", "Trinidad and Tobago", 
        # "Uruguay", "Venezuela"]

        INDUSTRIES = ["finance", "retail", "healthcare", "technology", "hospitality", "education"]

        # Generate website metadata
        website_data = {}
        for website in WEBSITES:
            website_data[website] = {
                'industry': random.choice(INDUSTRIES),
                'geos': GEOS, #random.sample(GEOS, random.randint(3, 6)),
                'base_pageviews': random.randint(1000000, 300000000),
                'growth_rates': {}
            }
            for geo in website_data[website]['geos']:
                website_data[website]['growth_rates'][geo] = random.uniform(0.02, 0.20)

        # Set end date to November 1, 2025
        end_date = datetime(2025, 11, 1)

        # Pick a random month in the past 12 months
        # end_date = datetime.now() - timedelta(days=random.randint(0, 365))

        end_date = end_date.replace(day=random.randint(1, 28))  # Avoid invalid dates
        mid_date = end_date - timedelta(days=29)
        start_date = end_date - timedelta(days=60)  # Changed from 730 to 60 days
        dates = pd.date_range(start=start_date, end=end_date, freq='D')



        # Generate data
        data = []
        for website in WEBSITES:
            model = LiteLLMModel(
                model_id="gpt-4",
                api_base="https://api.openai.com/v1",
                api_key=os.environ["OPENAI_API_KEY"]
            )
            agent = CodeAgent(
                tools=[],
                model=model,
                additional_authorized_imports=[
                    "datetime",
                    "requests"
                ],
                verbosity_level=self.LLM_LOGLEVEL
            )
            prompt = f"""
                generate a few dates between {mid_date} and {end_date} which are holidays or events.
                Specify a % for which each holiday may affect traffic. Also specify which geos out of {website_data[website]['geos']} 
                would be most affected by each holiday.
                Filter events to only include those with probability > 50%
                return as a list of dictionaries with the following keys: geo, date, event_name, probability
                """
            events = agent.run(prompt)
            self.logger.info(events)
            
            for geo in website_data[website]['geos']:
                base_pv = website_data[website]['base_pageviews']
                growth_rate = website_data[website]['growth_rates'][geo]
                for date in dates:
                    # Changed year check to month check
                    month = 1 if date >= (end_date - timedelta(days=30)) else 0
                    
                    # Base pageviews with random variation
                    daily_pv = int(base_pv * (1 + random.uniform(-0.1, 0.1)))
                    anomaly = ""
                    if month == 1:  # Changed from year to month
                        # Apply growth rate with noise
                        growth_noise = growth_rate * random.uniform(-0.1, 0.1)
                        daily_pv = int(daily_pv * (1 + growth_rate + growth_noise))
                        
                        # Random traffic drops
                        if random.random() < 0.03:
                            daily_pv = int(daily_pv * random.uniform(0.5, 0.9))
                            anomaly = "random"
                        
                        
                        # Holiday effects
                        # Check if current date has any events for this geo
                        for event in events:
                            event_date = event['date']
                            # LLMS can be inconsistent with date format
                            if isinstance(event_date, str):
                                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
                            else:
                                event_date = event_date.date()
                            if event['geo'] == geo and event_date == date.date():
                                daily_pv = int(daily_pv * random.uniform(0.3, 0.7))
                                anomaly = event['event_name']
                                break
                    # Error counts
                    errors_5xx = int(daily_pv * 0.01 * random.uniform(0.8, 1.2))
                    errors_4xx = int(errors_5xx * 4 * random.uniform(0.9, 1.1))
                    errors_3xx = int(errors_5xx * 0.1 * random.uniform(0.8, 1.2))
                    
                    # Calculate MoM (Month over Month) growth instead of YoY
                    mom_growth = 0
                    if month == 1:
                        prev_month_date = date - timedelta(days=30)  # Changed from 365 to 30
                        prev_month_data = [row for row in data if row[0] == website and row[2] == geo and row[3].date() == prev_month_date.date()]
                        if prev_month_data:
                            mom_growth = ((daily_pv - prev_month_data[0][4]) / prev_month_data[0][4]) * 100
                    
                    data.append([
                        website,
                        website_data[website]['industry'],
                        geo,
                        date,
                        daily_pv,
                        errors_5xx,
                        errors_4xx,
                        errors_3xx,
                        mom_growth,  # Changed from yoy_growth to mom_growth
                        anomaly
                    ])

        
        MarkdownGenerator.generate_traffic_csv(data, output_dir)
        MarkdownGenerator.generate_traffic_markdown(WEBSITES, data, website_data, start_date, end_date, output_dir)
