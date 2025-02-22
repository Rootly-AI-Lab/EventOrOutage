import pandas as pd
import numpy as np

class NaiveAnomalyDetecter:
    def __init__(self):
        pass

    
    def get_anomalies(self, df):
        """Analyze passed in dataframe object to detect anomalies and patterns.
        
        Args:
            df: pandas DataFrame containing the website metrics data

        Returns:
            dict: Analysis results including:
                - Website
                - Geo(s)
                - Dates of anomalies
        """
        results = {}
        for geo in df['geo'].unique():
            # Create a copy of the filtered data to avoid SettingWithCopyWarning
            geo_data = df[df['geo'] == geo].copy()
            # Convert dates to datetime
            geo_data['date'] = pd.to_datetime(geo_data['date'])
            # Split into last month and month before based on max date
            max_date = geo_data['date'].max()
            last_month_data = geo_data[geo_data['date'] >= (max_date - pd.Timedelta(days=30))]
            month_before_data = geo_data[geo_data['date'] < (max_date - pd.Timedelta(days=30))]

            # Calculate day-over-day growth rates comparing same days of week
            growth_rates = []
            for date in last_month_data['date'].unique():
                # Get data for current date
                growth_rate = self.compare_to_previous_month(date, last_month_data, month_before_data)
                if growth_rate == 0:
                    continue
                growth_rates.append(growth_rate)

            if len(growth_rates) == 0:
                continue

            # Find the base growth rate by identifying cluster of most common growth rates
            growth_rates = np.array(growth_rates)
            hist, bins = np.histogram(growth_rates, bins=50)
            most_common_bin_idx = np.argmax(hist)
            
            # Get growth rates in and around the most common bin
            base_growth_rates = growth_rates[
                (growth_rates >= bins[most_common_bin_idx-1]) &
                (growth_rates <= bins[most_common_bin_idx+1])
            ]
            base_growth_rate = np.mean(base_growth_rates)

            # Find anomalous days where growth rate significantly differs from base rate
            anomalous_dates = []
            for date in last_month_data['date'].unique():

                actual_growth = self.compare_to_previous_month(date, last_month_data, month_before_data)
                if actual_growth == 0:
                    continue
                current_day_data = last_month_data[last_month_data['date'] == date]
                if len(current_day_data) == 0:
                    continue
                
                month_ago_date = date - pd.Timedelta(days=30)
                matching_prev_data = month_before_data[
                    (month_before_data['date'].dt.dayofweek == date.dayofweek) &
                    (abs((month_before_data['date'] - month_ago_date).dt.days) <= 3)
                ]
                
                if len(matching_prev_data) > 0:
                    prev_pageviews = matching_prev_data['pageviews'].iloc[0]
                    current_pageviews = current_day_data['pageviews'].iloc[0]
                    actual_growth = ((current_pageviews - prev_pageviews) / prev_pageviews) * 100
                    
                    # If growth rate deviates significantly from base rate, mark as anomaly
                    if abs(actual_growth - base_growth_rate) > 20:  # 20% threshold
                        anomalous_dates.append(date.strftime('%Y-%m-%d'))

            if len(anomalous_dates) > 0:
                if geo not in results:
                    results[geo] = []
                results[geo].extend(anomalous_dates)
        return results
    

    def compare_to_previous_month(self, date, last_month_data, month_before_data):
        """Compare the growth rate of a given date to the growth rate of the same date last month.
        
        Args:
            date: pandas Timestamp object representing the date to compare
            last_year_data: DataFrame containing the last year's data
            year_before_data: DataFrame containing the previous year's data

        Returns:
            float: Growth rate of the date compared to the same date last year
        """
        # Get data for current date and matching previous year date
        current_day_data = last_month_data[last_month_data['date'] == date]
        if len(current_day_data) == 0:
            return 0
        # Find matching day from previous year (same day of week)
        day_of_week = date.dayofweek
        month_ago_date = date - pd.Timedelta(days=30)
        matching_prev_data = month_before_data[
            (month_before_data['date'].dt.dayofweek == day_of_week) &
            (abs((month_before_data['date'] - month_ago_date).dt.days) <= 3)
        ]
        
        if len(matching_prev_data) > 0:
            prev_pageviews = matching_prev_data['pageviews'].iloc[0]
            current_pageviews = current_day_data['pageviews'].iloc[0]
            growth_rate = ((current_pageviews - prev_pageviews) / prev_pageviews) * 100
            return growth_rate
        return 0
    
    def compare_previous_year(self,date, last_year_data, year_before_data):
        """Compare the growth rate of a given date to the growth rate of the same date last year.
        
        Args:
            date: pandas Timestamp object representing the date to compare
            last_year_data: DataFrame containing the last year's data
            year_before_data: DataFrame containing the previous year's data
        """
        raise NotImplementedError("Not implemented yet")
