
# EventOrOutage 🥳☄️
![Made by Rootly AI Lab](https://img.shields.io/badge/Made%20by%20-%20Rootly%20AI%20Lab-blue?style=flat-square)
![Gemini logo](https://img.shields.io/badge/library-smolagents-purple?style=flat-square&logoColor=#b600d](https://img.shields.io/badge/Gemini_Compatible-Compatible?style=flat-square&logo=googlegemini&labelColor=black&color=%238E75B2
))
![Anthropic logo]([https://img.shields.io/badge/Anthropic_Compatible-Compatible?style=flat-square&logo=anthropic&labelColor=black&color=black](https://img.shields.io/badge/Anthropic_Compatible-Compatible?style=flat-square&logo=anthropic&labelColor=black&color=white
))
![OpenAI logo](https://img.shields.io/badge/OpenAI_Compatible-Compatible?style=flat-square&logo=openai&labelColor=black&color=white)
<a href="https://www.youtube.com/@rootlyhq/">
    <img src="https://img.shields.io/badge/youtube-d95652.svg?style=flat-square&logo=youtube" alt="youtube" style="height: 20px;">
  </a>

EventOrOutage is leveraging LLMs to help SREs understand if a drop in traffic is due to an external event (holiday, election, sport event...) instead of an outage. For each event, it shows the probably that the event could have an impact on traffic, which geographies are impacted and how many people may be involved.

This standalone prototype shows how such feature could be  useful as part of an AI SRE or an embeded in a monitoring tool.

```
$ eventoroutage -d "february 9th, 2025"

Super Bowl LVIII – 85%:

-   Number of people involved: Over 100 million
-   Countries involved: United States

Lunar New Year Celebrations – 80%:

-   Number of people involved: Approximately 1.5 billion
-   Countries involved: China, Singapore, Malaysia, Indonesia, Philippines
```

## Get started 🚀
**Requirements:**
* Python > 3.10
* A `.env` file with OpenAPI/Gemini/Anthropic API Key (at least one)

**Optional:**
* A `HOLIDAY_API_KEY` in the `.env` file [Holiday API](https://holidayapi.com/)
* A `CALENDARIFIC_API_KEY` in the `.even` file [Calendrific](https://calendarific.com/)

```
python -m venv .venv
source .venv/bin/activate
pip install .
analyze -f artifacts/website_metrics_labelled.csv
```

## Examples 📖
Here are a few ways you can use EventOrOutage:
* `eventoroutage` – will look for events happening today
* `eventoroutage -d "February 14, 2025" -m "gpt-4o"` – look for events at a specific date, using a specific model
* `eventoroutage -l IN` – look for events in a specific location, here India
* `eventoroutage -f "artifacts/traffic_events.csv"` – analyze traffic logs from a file
* ` generatedata -d .` – generates synthetic traffic logs

## Stack 🛠️
-   **LLMs:** GPT-4, Claude, Gemini and self-hosted (Deepseek). 
-   **Agent:** HuggingFace smolagents
-   **Data Sources:** External APIs for holidays, news, and event tracking
 
## Backstory 
Back when [Jeba](https://www.linkedin.com/in/graydot/) and [Sylvain](https://www.linkedin.com/in/sylvainkalache/) were working at LinkedIn, they faced a situation where a large chunk of the site traffic was gone. Leadership panicked, engineering could not find the cause. 

Turns out a major holiday was happening in India and people were busy celebrating, instead of browsing LinkedIn. Knowing about every potential major event in every country your product is used for isn’t possible, but LLMs are great at this type of task.

## Future Improvements 
- Add support for additional data sources such as everyeventapi, Google Calendar API for holidays etc
- Integration in data from logging tools such as Loggly, Splunk to analyze traffic anomalies

## About the Rootly AI Lab
This project was developed by the Rootly AI Lab. The AI Lab is a fellow-led program designed to redefine reliability and system operations. We develop innovative prototypes, create open-source tools, and produce research reports we share with the community. 
![Rootly AI logo](Rootly_AI_Logo_White.png)

