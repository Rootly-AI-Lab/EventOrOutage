from smolagents import Tool
import requests
import os
from termcolor import colored
from logging import Logger

class HolidaysAPITool(Tool):

    name = "holidays_api_tool"
    description = """
    This is a tool that fetches holidays from Holidays API for a specific date."""
    inputs = {
        "country": {
            "type": "string",
            "description": "the country to fetch holidays for",
        },
        "year": {
            "type": "integer",
            "description": "the year to fetch holidays for",
        },
        "month": {
            "type": "integer",
            "description": "the month to fetch holidays for",
        },
        "day": {
            "type": "integer",
            "description": "the day to fetch holidays for",
        }
    }
    output_type = "object"
    
    def forward(self, country: str, year: int, month: int, day: int):
        self.logger = Logger('default')
        """    
        Raises:
            Exception: If API call fails or returns an error
        """
        if self.disabled:
            return {
                "error": "Tool is not configured. Do not call this tool."
            }
        api_key = os.getenv("HOLIDAY_API_KEY")
        if not api_key:
            self.logger.error(
                "HOLIDAY_API_KEY environment variable is not set"
                "Disabling tool"
            )
            self.disabled = True
            return {
                "error": "Tool is not configured. Do not call this tool."
            }
            
        base_url = "https://holidayapi.com/v1/holidays"
        params = {
            "key": api_key,
            "country": country,
            "year": year,
            "month": month,
            "day": day
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch holidays: {str(e)}")
