import pandas as pd
from datetime import datetime, timedelta
from file_utils import FileUtils
import os

class MarkdownGenerator:
    def __init__(self):
        self.markdown = ""

        
    def generate_anomaly_markdown(
            traffic_data: pd.DataFrame, 
            anomaly_candidates: dict, 
            analysis_results: dict, 
            output_dir: str):
        """Generate charts of the analysis results.
        
        Args:
            data_frame: Original data frame with the traffic data
            anomaly_candidates: Dictionary of detected anomalies
            analysis_output: Analysis output from the LLM
        """
        # Generate Mermaid charts markdown
        markdown_content = "# Website Traffic Anomaly Analysis\n\n"

        # Get unique list of websites from the dataframe
        websites = traffic_data['website'].unique().tolist()
        
        
        # FIXME: Duplicate code between this and generate_traffic_markdown
        for website in websites:
            markdown_content += f"## {website}\n\n"
            website_df = traffic_data[traffic_data['website'] == website]
            
            for geo in website_df['geo'].unique():
                markdown_content += f"### {geo}\n\n"
                markdown_content += "## Daily View\n\n"
                geo_df = website_df[website_df['geo'] == geo]
                iter_date = pd.to_datetime(geo_df['date'])
                end_date = iter_date.max()
                month1_data = geo_df[iter_date < (end_date - timedelta(days=30))]
                month2_data = geo_df[iter_date >= (end_date - timedelta(days=30))]
                
                min_pv = min(geo_df['pageviews'])
                max_pv = max(geo_df['pageviews'])
                
                markdown_content += "```mermaid\n"
                markdown_content += "xychart-beta\n"
                markdown_content += "title Traffic Analysis\n"
                markdown_content += f"x-axis [" + ",".join([f'"{d}"' for d in month2_data['date']]) + "]\n"
                markdown_content += f"y-axis \"Pageviews\" 0--> {max_pv}\n"
                
                # Add data lines
                markdown_content += f"line [" + ",".join(map(str, month1_data['pageviews'].tolist())) + "]\n"
                markdown_content += f"line [" + ",".join(map(str, month2_data['pageviews'].tolist())) + "]\n"
                markdown_content += "```\n\n"

                # Add anomaly statistics section
                markdown_content += "## Anomaly Statistics\n\n"
        
                total_anomalies = 0
                triaged_anomalies = 0
                
                # Get anomaly candidates for current website and geo
                geo_anomaly_candidates = anomaly_candidates.get(website, {}).get(geo, {})
                if geo_anomaly_candidates:
                    markdown_content += "<details>\n\n"
                    markdown_content += "<summary>Detected Anomalies</summary>\n"
                    total_anomalies = len(geo_anomaly_candidates)
                    for index, date in enumerate(geo_anomaly_candidates):
                        is_triaged = analysis_results.get(website, {}).get(geo, {}).get(date, {})
                        
                        if is_triaged:
                            triaged_anomalies += 1
                            markdown_content += f"{index + 1}. {date} "
                            events = []
                            for event in is_triaged:
                                events.append(f"🔥 {event['event']} (Probability: {event['probability']})")
                            markdown_content += f" - " + ", ".join(events)
                        else:
                            markdown_content += f"{index + 1}. {date} - "
                        markdown_content += "\n\n"
                    markdown_content += "</details>\n\n"
                else:
                    markdown_content += "No anomalies detected for this website/geo combination.\n\n"
                    total_anomalies = 0
                
                
            
                markdown_content += f"> Total Anomalies Detected: {total_anomalies}\n\n"
                markdown_content += f"> Anomalies Triaged: {triaged_anomalies}\n\n"
                markdown_content += f"> Triage Coverage: {(triaged_anomalies/total_anomalies*100):.1f}% \n\n\n" if total_anomalies > 0 else "- No anomalies detected\n\n"

        # Save markdown file
        if not os.path.exists(output_dir):
            raise FileNotFoundError(f"Base path {output_dir} does not exist")
        os.makedirs(os.path.join(output_dir, "artifacts"), exist_ok=True)

        os.makedirs("artifacts", exist_ok=True)
        output_filepath = os.path.join(output_dir, "artifacts", f"anomaly_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        FileUtils.save_markdown(output_filepath, markdown_content)

    def generate_traffic_csv(traffic_data: pd.DataFrame, output_dir: str):
        df = pd.DataFrame(traffic_data, columns=['website', 'industry', 'geo', 'date', 'pageviews', '5xx', '4xx', '3xx', 'mom_growth', 'anomaly'])
        if not os.path.exists(output_dir):
            raise FileNotFoundError(f"Base path {output_dir} does not exist")
        os.makedirs(os.path.join(output_dir, "artifacts"), exist_ok=True)
        df.to_csv(os.path.join(output_dir, 'artifacts', 'website_metrics_labelled.csv'), index=False)
        df_unlabelled = df.drop('anomaly', axis=1)
        df_unlabelled.to_csv(os.path.join(output_dir, 'artifacts', 'website_metrics_unlabelled.csv'), index=False)

    # FIXME: passing a date here is pretty ugly
    def generate_traffic_markdown(
            websites: list, 
            traffic_data: pd.DataFrame, 
            website_data: dict, 
            start_date: datetime, 
            end_date: datetime,
            output_dir: str):
        """Generate charts of the analysis results.
        
        Args:
            data_frame: Original data frame with the traffic data

        Returns:
            markdown_content: Markdown content
        """
        df = pd.DataFrame(traffic_data, columns=['website', 'industry', 'geo', 'date', 'pageviews', '5xx', '4xx', '3xx', 'mom_growth', 'anomaly'])
        df.to_csv('website_metrics_labelled.csv', index=False)
        df_unlabelled = df.drop('anomaly', axis=1)
        df_unlabelled.to_csv('website_metrics_unlabelled.csv', index=False)

        # Generate Mermaid charts markdown
        markdown_content = "# Website Traffic Analysis\n\n"

        for website in websites:
            markdown_content += f"## {website}\n\n"
            website_df = df[df['website'] == website]

            for geo in website_data[website]['geos']:
                markdown_content += f"### {geo}\n\n"
                markdown_content += "## Daily View\n\n"
                geo_df = website_df[website_df['geo'] == geo]
                month1_data = geo_df[geo_df['date'] < (end_date - timedelta(days=30))]
                month2_data = geo_df[geo_df['date'] >= (end_date - timedelta(days=30))]
                min_pv = min(geo_df['pageviews'])
                max_pv = max(geo_df['pageviews'])
                

                markdown_content += "```mermaid\n"
                markdown_content += "xychart-beta\n"
                markdown_content += "title Traffic Analysis\n"
                markdown_content += f"x-axis [" + ",".join([f'"{d.strftime("%Y-%m-%d")}"' for d in month1_data['date']]) + "]\n"
                markdown_content += f"y-axis \"Pageviews\" 0--> {max_pv}\n"
                
                # Add data lines
                markdown_content += f"line [" + ",".join(map(str, month1_data['pageviews'].tolist())) + "]\n"
                markdown_content += f"line [" + ",".join(map(str, month2_data['pageviews'].tolist())) + "]\n"
                markdown_content += "```\n\n"

        if not os.path.exists(output_dir):
            raise FileNotFoundError(f"Base path {output_dir} does not exist")
        os.makedirs(os.path.join(output_dir, "artifacts"), exist_ok=True)
        FileUtils.save_markdown(os.path.join(output_dir, 'artifacts', 'traffic_analysis.md'), markdown_content)