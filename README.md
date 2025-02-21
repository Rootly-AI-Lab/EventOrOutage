# EventOrOutage
EventOrOutage

Analyze website traffic and geo-location events.

## Example Usage from command line

### Analyze an incident today
`src/event_or_outage/cli.py`

### Override the model and provide a date in the past
`src/event_or_outage/cli.py -d "February 14, 2025" -m "gpt-4o"`

### Provide a location and a date
`src/event_or_outage/cli.py -d "October 2024" -l India`

### Analyze logs from a csv file
`src/event_or_outage/cli.py -f "traffic_events.csv"`

### Generate synthetic data and accompanying charts

`src/event_or_outage/synthetic_data_generator.py`

## Possible Future Improvements
- You can add more tools to fetch events from other sources such as everyeventapi, google calendar api for holidays etc
- Data from logging tools such as loggly, splunk etc can be used to analyze anomalies

## Development

### Install dependencies
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
create a .env file with the following:
OPENAI_API_KEY=[your-openai-key]





