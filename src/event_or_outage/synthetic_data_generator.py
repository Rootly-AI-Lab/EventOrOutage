#! /usr/bin/env python3
from datetime import datetime
from .synthetic_data import SyntheticData
from .markdown_generator import MarkdownGenerator
import argparse
class SyntheticDataGenerator:
    def parse_arguments():
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='Generates synthetic traffic data')
        
        # Add arguments
        parser.add_argument('-d', '--dir', type=str, help='Output directory')
        # Parse arguments
        args = parser.parse_args()
        return args
    


def main():
    # Get command line arguments
    args = SyntheticDataGenerator.parse_arguments()
    if args.dir is None:
        raise ValueError("Output directory is required")
    
    output_dir = args.dir
    data = SyntheticData().generate(datetime(2024, 11, 1))
    MarkdownGenerator.generate_traffic_csv(data, output_dir)
    MarkdownGenerator.generate_traffic_markdown(data, output_dir)
    print(data)

if __name__ == "__main__":
    main()