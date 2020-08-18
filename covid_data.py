"""---------------------------------------------------------------------------------------------------------------------
  File Name:   covid_data.py
  End Result:  A series of classes to retrieve and manipulate COVID-19 from multiple datasets and multiple geographies
  Outline:     1) JHUDataset: Retrieves and manipulates data from Johns Hopkins Univ. COVID-19 dataset
               2) SCDHECOpenDataset: Retrieves and manipulates data from SC DHEC COVID-19 ArcGIS Open dataset
               3) StateData: A subclass of JHUDataset which provides COVID-19 data for a specified state
               4) CountyData: A subclass of JHUDataset which provides COVID-19 data for a specified county
               5) ZIPCodeData: A subclass of SCDHECOpenDataset which provides COVID-19 data for a specified ZIP code
               6) ZIPCodeGroupData: A subclass of SCDHECOpenDataset which provides data for a combination of ZIP codes
  Author:      Connor Cozad (23ccozad@gmail.com)
  Created:     August 16, 2020
---------------------------------------------------------------------------------------------------------------------"""

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)


class JHUDataset:
    """Retrieves and manipulates data from Johns Hopkins Univ. COVID-19 dataset"""

    cases_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

    def __init__(self):
        """Retrieves COVID-19 data from Johns Hopkins Univ. and prepares the data to be queried by geography"""

        ##### Manipulate dataframe for COVID-19 cases -----------------------------------------------------------------

        # Read the data into a dataframe
        cases = pd.read_csv(self.cases_url)

        # Transpose (turn rows into columns and columns into rows) the data and fix the resulting column titles
        cases = cases.transpose()
        cases.rename(columns=cases.iloc[0], inplace=True)
        cases = cases[1:]

        # Create a dataframe for metadata, which matches each county with its unique ID number (UID)
        cases_meta = cases[:10]
        cases_meta = cases_meta.transpose()

        # Data from Johns Hopkins provides the cumulative number of cases each day. Using diff() gives us the number of
        # new cases per day instead
        cases = cases[10:].diff()

        # Ensure that the dataframe rows are sorted in date order
        cases.index = pd.to_datetime(cases.index)
        cases.sort_index(inplace=True)

        # Set our two dataframes as attributes
        self.cases = cases
        self.cases_meta = cases_meta

        ##### Manipulate dataframe for COVID-19 deaths -----------------------------------------------------------------

        # Read the data into a dataframe
        deaths = pd.read_csv(self.deaths_url)

        # Transpose (turn rows into columns and columns into rows) the data and fix the resulting column titles
        deaths = deaths.transpose()
        deaths.rename(columns=deaths.iloc[0], inplace=True)
        deaths = deaths[1:]

        # Create a dataframe for metadata, which matches each county with its unique ID number (UID)
        deaths_meta = deaths[:11]
        deaths_meta = deaths_meta.transpose()

        # Data from Johns Hopkins provides the cumulative number of deaths each day. Using diff() gives us the number
        # of new deaths per day instead
        deaths = deaths[11:].diff()

        # Ensure that the dataframe rows are sorted in date order
        deaths.index = pd.to_datetime(deaths.index)
        deaths.sort_index(inplace=True)

        # Set our two dataframes as attributes
        self.deaths = deaths
        self.deaths_meta = deaths_meta

    def get_uid(self, variable, state=None, county=None):
        """Get the UID for a particular state or county."""

        # Decide whether to search for the UID for a county or state from the cases dataframe or deaths dataframe
        # Note: The UIDs currently are the same for any given state/county in both dataframes, so it wouldn't matter if
        # you chose 'cases' or 'deaths'. This may not always be the case in the future though.
        if variable is 'cases':
            dataframe = self.cases_meta
        elif variable is 'deaths':
            dataframe = self.deaths_meta

        # Get the list of UID's for all the counties in a state, or the UID for one county
        # Note: When searching for a county, you also need to specify the state, since there are some counties with the
        # same name in different states
        if state is not None and county is None:
            state_dataframe = dataframe.loc[dataframe['Province_State'] == state]
            return list(state_dataframe.index.values)
        elif state is not None and county is not None:
            county_dataframe = dataframe.loc[(dataframe['Admin2'] == county) & (dataframe['Province_State'] == state)]
            return county_dataframe.index.values


class SCDHECOpenDataset:
    """Retrieves and manipulates data from SC DHEC COVID-19 ArcGIS Open dataset"""

    cases_url = "https://opendata.arcgis.com/datasets/0b01284bff1f479d9fba1a8c516c3d97_0.csv"

    def __init__(self):
        """Retrieves COVID-19 data from SC DHEC and prepares the data to be queried by geography"""
        # Read the data into dataframe, sort by date, and set as an attribute
        cases = pd.read_csv(self.cases_url)
        cases['Date'] = pd.to_datetime(cases['Date'])
        cases.sort_values(by=['Date'], inplace=True)
        self.cases = cases


class StateData(JHUDataset):
    """A subclass of JHUDataset which provides COVID-19 data for a specified state"""
    # Future Note: Additional state-level data available at https://api.covidtracking.com/v1/states/sc/daily.csv

    def __init__(self, state):
        """Get the COVID-19 data from JHUDataset for the specified state"""
        super().__init__()
        self.state = state
        self.state_cases = self.cases[self.get_uid('cases', state=state)].sum(axis=1).astype(int)
        self.state_deaths = self.deaths[self.get_uid('deaths', state=state)].sum(axis=1).astype(int)

    def get_total_cases(self):
        """Return the total number of COVID-19 cases for the state"""
        return self.state_cases.sum()

    def get_daily_cases(self):
        """Return a pandas series containing the number of new cases each day for the state"""
        return self.state_cases

    def get_daily_cases_moving_avg(self, days):
        """Return a pandas series containing the moving average for new cases per day for the state"""
        return self.state_cases.rolling(days).mean()

    def get_total_deaths(self):
        """Return the total number of COVID-19 deaths for the state"""
        return self.state_deaths.sum()

    def get_daily_deaths(self):
        """Return a pandas series containing the number of deaths each day for the state"""
        return self.state_deaths

    def get_daily_deaths_moving_avg(self, days):
        """Return a pandas series containing the moving average for deaths per day for the state"""
        return self.state_deaths.rolling(days).mean()


class CountyData(JHUDataset):
    """A subclass of JHUDataset which provides COVID-19 data for a specified county"""

    def __init__(self, county, state):
        """Get the COVID-19 data from JHUDataset for the specified county"""
        super().__init__()
        self.county = county
        self.state = state
        self.county_cases = self.cases[self.get_uid('cases', county=county, state=state)].sum(axis=1).astype(int)
        self.county_deaths = self.deaths[self.get_uid('deaths', county=county, state=state)].sum(axis=1).astype(int)

    def get_total_cases(self):
        """Return the total number of COVID-19 cases for the county"""
        return self.county_cases.sum()

    def get_daily_cases(self):
        """Return a pandas series containing the number of new cases each day for the county"""
        return self.county_cases

    def get_daily_cases_moving_avg(self, days):
        """Return a pandas series containing the moving average for new cases per day for the county"""
        return self.county_cases.rolling(days).mean()

    def get_total_deaths(self):
        """Return the total number of COVID-19 deaths for the county"""
        return self.county_deaths.sum()

    def get_daily_deaths(self):
        """Return a pandas series containing the number of deaths each day for the county"""
        return self.county_deaths

    def get_daily_deaths_moving_avg(self, days):
        """Return a pandas series containing the moving average for deaths per day for the county"""
        return self.county_deaths.rolling(days).mean()


class ZIPCodeData(SCDHECOpenDataset):
    """A subclass of SCDHECOpenDataset which provides COVID-19 data for a specified ZIP code"""

    def __init__(self, zip_code):
        """Get the COVID-19 data from SCDHECOpenDataset for the specified ZIP code"""
        super().__init__()
        self.zip_code = zip_code
        cases = self.cases[self.cases['Zip'] == zip_code]
        self.zip_code_cases = pd.Series(cases['Total_Cases'].values, cases['Date']).diff()[1:].astype(int)

    def get_total_cases(self):
        """Return the total number of COVID-19 cases for the ZIP code"""
        return self.zip_code_cases.sum()

    def get_daily_cases(self):
        """Return a pandas series containing the number of new cases each day for the ZIP code"""
        return self.zip_code_cases

    def get_daily_cases_moving_avg(self, days):
        """Return a pandas series containing the moving average for new cases per day for the ZIP code"""
        return self.zip_code_cases.rolling(days).mean()


class ZIPCodeGroupData(SCDHECOpenDataset):
    """A subclass of SCDHECOpenDataset which provides COVID-19 data for a combination of ZIP codes"""

    def __init__(self, zip_code_group):
        """Get the COVID-19 data from SCDHECOpenDataset across all the specified ZIP codes listed in zip_code_group"""
        super().__init__()
        self.zip_code_group = zip_code_group
        cases = self.cases.loc[self.cases['Zip'].isin(zip_code_group)]
        cases = pd.Series(cases['Total_Cases'].values, cases['Date']).groupby(['Date']).sum()
        self.zip_code_group_cases = cases.diff()[1:].astype(int)

    def get_total_cases(self):
        """Return the total number of COVID-19 cases across the combined ZIP codes"""
        return self.zip_code_group_cases.sum()

    def get_daily_cases(self):
        """Return a pandas series containing the number of new cases each day across the combined ZIP codes"""
        return self.zip_code_group_cases

    def get_daily_cases_moving_avg(self, days):
        """Return a pandas series containing the moving average for new cases per day across the combined ZIP codes"""
        return self.zip_code_group_cases.rolling(days).mean()