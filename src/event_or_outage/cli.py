#! /usr/bin/env python3
from .single_anomaly_agent import SingleAnomalyAgent
from .bulk_anomaly_agent import BulkAnomalyAgent
from .naive_anomaly_detecter import NaiveAnomalyDetecter
import argparse
import os
import pandas as pd
from termcolor import colored
from logging import Logger
from datetime import datetime
from .markdown_generator import MarkdownGenerator

class CLI:
    
    def parse_arguments():
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Description of your program')
        
        # Add arguments
        parser.add_argument('-d', '--duration', type=str, help='Time period/date to analyze')
        parser.add_argument('-l', '--location', type=str, help='location/geo of anomaly. Leave blank for worldwide')
        parser.add_argument('-i', '--industry', type=str, help='Industry of the website. Optional. Helps triangulate more accurately.')
        parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
        parser.add_argument('-f', '--file', type=str, help='File to analyze bulk events. Optional. If not provided, the script will use other command line arguments.')
        parser.add_argument('-m', '--model', type=str, choices=['gpt-4', 'claude-3-5-sonnet-latest', "gemini-pro"], default='gpt-4', help='Model to use for analysis. Supported models are gpt and claude.')
        # Parse arguments
        args = parser.parse_args()
        return args
    
    def load_data_file(file_path: str):
        """Load and validate the CSV data file.
        
        Args:
            file_path: Path to the CSV file to analyze
            
        Returns:
            pandas.DataFrame: The loaded CSV data
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file is not a valid CSV or is missing required columns
        """
        if not file_path:
            raise ValueError("No file path provided")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not file_path.lower().endswith('.csv'):
            raise ValueError("File must be a CSV file")
            
        try:
            df = pd.read_csv(file_path)
            required_columns = ['website', 'geo', 'date', 'pageviews']
            optional_columns = ['industry']
            missing_required = [col for col in required_columns if col not in df.columns]
            missing_optional = [col for col in optional_columns if col not in df.columns]
            if missing_optional:
                print(f"Warning: Optional column(s) missing: {', '.join(missing_optional)}")
            missing_columns = missing_required
            
            if missing_columns:
                raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}")
                
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError:
            raise ValueError("File is not a valid CSV")


def main():
    logger = Logger('default')
    # Get command line arguments
    args = CLI.parse_arguments()
    if args.file:
        if args.duration or args.location or args.industry:
            raise ValueError("Cannot specify individual event parameters (duration, location, industry) when using a bulk data file. Please either provide a file OR individual event parameters, not both.")
        
        df = CLI.load_data_file(args.file)
        
        anomaly_candidates = NaiveAnomalyDetecter().get_anomalies(df)
        output = BulkAnomalyAgent().troubleshoot(anomaly_candidates, args.model)

        output_analysis = output['analysis']
        base_path = os.path.dirname(args.file)
        MarkdownGenerator.generate_anomaly_markdown(df, anomaly_candidates, output_analysis, base_path)
        if output.get('summary'):
            print(colored('\n'.join(output['summary']), 'green'))
        else:
            logger.info(colored(output, 'yellow'))
        return
        
    # Access the arguments
    if args.verbose:
        print(f"Verbose mode enabled") # TODO: Not hooked up yet
    if args.duration == None:
        args.duration = "today"
    if args.location == None:
        args.location = ""
    output = SingleAnomalyAgent().troubleshoot(args.duration, args.location, args.industry, args.model)
    print(colored(output, 'green'))

if __name__ == "__main__":
    main()