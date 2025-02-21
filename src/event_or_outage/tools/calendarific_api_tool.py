from smolagents import Tool
import requests
import os


class CalendarificAPITool(Tool):

    name = "calendarific_api_tool"
    description = """
    This is a tool that fetches holidays from Calendarific for a specific date."""
    inputs = {
        "country": {
            "type": "string",
            "description": "the country to fetch holidays for"
        },
        "year": {
            "type": "integer",
            "description": "the year to fetch holidays for"
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
        """    
        Raises:
            Exception: If API call fails or returns an error
        """
        api_key = os.getenv("CALENDARIFIC_API_KEY")
        if not api_key:
            raise ValueError("CALENDARIFIC_API_KEY environment variable is not set")
            
        base_url = "https://calendarific.com/api/v2/holidays"
        params = {
            "api_key": api_key,
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
