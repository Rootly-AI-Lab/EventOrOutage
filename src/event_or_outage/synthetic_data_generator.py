#! /usr/bin/env python3
from synthetic_data import SyntheticData
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
    
    SyntheticData().generate(args.dir)

if __name__ == "__main__":
    main()