import itertools
import pathlib
import pandas as pd
import numpy as np
import statistics as stat
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from date_and_time import getFullDateInfo
from date_and_time import get_time_shift_forward_dates
from date_and_time import get_time_shift_back_dates
from utilization import getUtilization
from utilization import getDateAndTime
from airTemperature_Parser_DWD import getData
from sklearn.linear_model import LinearRegression

__author__ = "Hendrik Sanhen, and Dr Nancy Retzlaff"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Hendrik Sanhen", "Nancy Retzlaff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Dr Nancy Retzlaff"
__email__ = "retzlaff@wifa.uni-leipzig.de"
__status__ = "Prototype"

path = '~/myPath/To/city1.csv'  # todo set correct path
city = "city1"  # todo set correct city name
plot_boolean = True

df = pd.read_csv(path, sep=";")

df.drop("To", axis=1, inplace=True)  # redundant information; already contained in "From"
df.drop(0, axis=0, inplace=True)  # German header; not part of the data

# copy time column and remove from data frame; format "dd.mm.yyyy hh:mm"
time_df = df[["From"]].copy()
time_df = getFullDateInfo(time_df, city)
df.drop("From", axis=1, inplace=True)

# number format of input is German --> switch to English and parse them as floats
df = df.apply(lambda x: x.str.replace(',', '.'))
for col in df.columns:
    df[col] = df[col].astype(float)

# first cut the end, otherwise the index of last monday is shifted
if time_df.iloc[-1]["dayOfWeek"] != 6:  # 6 is Sunday, nothing to be done
    last_monday = next(i for i, v in enumerate(reversed(time_df["dayOfWeek"]), 1) if v == 6)
    df.drop(df.tail(last_monday).index, inplace=True)
    time_df.drop(time_df.tail(last_monday).index, inplace=True)

if time_df.iloc[0]["dayOfWeek"] != 0:
    first_monday = next(i for i, v in enumerate(time_df["dayOfWeek"]) if v == 0)
    df.drop(df.head(first_monday).index, inplace=True)
    time_df.drop(time_df.head(first_monday).index, inplace=True)

number_weeks = int(len(time_df) / 672)

# set meter column --> switch for different meter
# assumption 1: first entry of time_df is a Monday 0:00
# assumption 2: last entry of time_df is a Sunday 23:45
# a1 + a2: len(midnight_quarter)::7 = 0
for meter in df.columns:
    list_min = []
    list_max = []
    list_mean = []
    list_upper_quantile = []
    list_lower_quantile = []

    quarters_copy = []  # initialize empty array for weekly quarters
    for k in range(672):
        quarters_copy.append([])
        quarters_copy[k] = df[(time_df["quarter_of_week"] == k)][meter].values.tolist()

    for quarter in quarters_copy:
        quarter_ = [b for b in quarter if not np.isnan(b)]  # ignores NaNs

        list_min.append(min(quarter_))
        list_max.append(max(quarter_))
        list_mean.append(stat.mean(quarter_))
        # influence (also works with sparse data), later use mean
        list_upper_quantile.append(np.quantile(quarter_, .95))
        list_lower_quantile.append(np.quantile(quarter_, .05))

    if plot_boolean:
        x_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        x = list(range(672))
        plt.xticks([48, 144, 240, 336, 432, 528, 624], x_labels)  # plots x_labels in the center of daily data
        # plot all weeks with quantiles
        plt.fill_between(x, list_mean, list_upper_quantile, alpha=.9, color="orange")
        plt.fill_between(x, list_mean, list_lower_quantile, alpha=.9, color="orange")
        plt.fill_between(x, list_max, list_upper_quantile, alpha=.5, color="grey")
        plt.fill_between(x, list_min, list_lower_quantile, alpha=.5, color="grey")
        plt.plot(x, list_mean, color="black", linewidth=0.7)
        plt.plot(x, list_upper_quantile, color="darkgrey", linewidth=0.7)
        plt.plot(x, list_lower_quantile, color="darkgrey", linewidth=0.7)
        plt.title(meter)
        plt.ylabel("Energy Consumption [kW]")
        # plt.show()
        pathlib.Path('plots/' + city).mkdir(parents=True, exist_ok=True)
        filename = 'plots/' + city + '/beforeCleaning/' + meter + '_beforeCleaning_.pdf'
        plt.savefig(filename, dpi=1200)
        plt.clf()

    for current_week in range(number_weeks):
        for quarter in range(672):
            if df.iloc[(current_week * 672) + quarter][meter] > list_upper_quantile[quarter]:
                df.iloc[(current_week * 672) + quarter][meter] = 'NaN'
            elif df.iloc[(current_week * 672) + quarter][meter] < list_lower_quantile[quarter]:
                df.iloc[(current_week * 672) + quarter][meter] = 'NaN'

# --------------------
# preprocessing steps until here!

meter = df.columns[0]
quarters_working_days_per_month = []
# initialize empty arrays for each quarter hour of the day
quarters_working_days = []
quarter_saturdays = []
quarter_sundays = []
for j in range(13):
    quarters_working_days.append([])
    for k in range(96):
        quarters_working_days[j].append([])
list_mean_monthly_working_days = []

# iterate over each month
for kindOfDay in range(3):
    list_mean_monthly_working_days.append([])
    for i in range(1, 13):
        working_days_this_month = df[(time_df["months"] == i) & (time_df["kindOfDay"] == kindOfDay)][meter].copy()
        working_days_all_quarters = []
        # for each day chunk day into quarters
        for day in range(int(len(working_days_this_month)/96)):
            one_working_day = working_days_this_month.head(96)
            working_days_this_month.drop(working_days_this_month.head(96).index, inplace=True)
            for j in range(96):
                if not np.isnan(one_working_day.iloc[j]):
                    quarters_working_days[i][j].append(one_working_day.iloc[j])  # add quarter to quarter list
        list_mean_ = []
        for quarter in quarters_working_days[i]:
            quarter_ = [b for b in quarter if not np.isnan(b)]  # ignores NaNs
            list_mean_.append(stat.mean(quarter_))
        list_mean_monthly_working_days[kindOfDay].append(list_mean_)

min_, max_, sum_ = 200, 0, 0
for i in range(len(list_mean_monthly_working_days)):
    for j in range(len(list_mean_monthly_working_days[i])):
        minimum = min(list_mean_monthly_working_days[i][j])
        if min_ > minimum:
            min_ = minimum
        maximum = max(list_mean_monthly_working_days[i][j])
        if max_ < maximum:
            max_ = maximum
min_ = min_ - 5
max_ = max_ + 2
gs = gridspec.GridSpec(1, 3)
labels_ = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
colors_ = ["blue", "darkblue", "indigo", "purple", "magenta", "crimson", "orangered", "orange", "yellow", "lime",
           "darkturquoise", "dodgerblue"]
x = list(range(96))
ax = plt.subplot(gs[0, 0])  # row 0, col 0
ax.set_title("Saturday")
ax.set_ylim(min_, max_)
ax.set_ylabel("Energy Consumption [kW]")
for i in range(12):
    ax.plot(x, list_mean_monthly_working_days[1][i],  label=labels_[i], color=colors_[i])
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[0:4])

ax = plt.subplot(gs[0, 1])  # row 0, col 1
ax.set_title("Sunday")
ax.set_ylim(min_, max_)
for i in range(12):
    ax.plot(x, list_mean_monthly_working_days[2][i], label=labels_[i], color=colors_[i])
ax.axes.get_yaxis().set_visible(False)
ax.legend(handles=handles[4:8])

ax = plt.subplot(gs[0, 2])  # row 1, span all columns
ax.set_title("Working Day")
ax.set_ylim(min_, max_)
for i in range(12):
    ax.plot(x, list_mean_monthly_working_days[0][i], label=labels_[i], color=colors_[i])
ax.axes.get_yaxis().set_visible(False)
# plt.show()
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[8:12])

filename = 'plots/' + city + '/monthly_profiles_.pdf'
plt.savefig(filename, dpi=1200)
plt.clf()

# new dataframe for hourly data by summing up every 4 entries in a row
hourly_data = pd.DataFrame(columns=df.columns)
for i in range(int(len(df)/4)):
    new_row = []
    for meter in df.columns:
        new_row.append(sum(df[meter][(i*4):((i+1)*4)]))
    hourly_data.loc[i] = new_row
# get correct dates from original data
hourly_data["date"] = list(itertools.islice(time_df["From"], 0, None, 4))
hourly_data["season"] = list(itertools.islice(time_df["season"], 0, None, 4))

# get weather data from DWD parser
weather_data = getData(city)

# find correct start and end dates that are in both, weather data and consumption data
start_date_weather = pd.to_datetime(pd.Series(weather_data["date"].iloc[0]), format="%Y%m%d%H")
start_date_data = pd.to_datetime(pd.Series(hourly_data["date"].iloc[0]), format="%d.%m.%Y %H:%M")
if start_date_weather[0] >= start_date_data[0]:
    start_date = start_date_weather[0].strftime('%d.%m.%Y %H:%M')
    start_date_index = next(i for i, v in enumerate(time_df["date"]) if v == start_date)
    hourly_data.drop(hourly_data.head(start_date_index).index, inplace=True)
else:
    start_date = start_date_data[0].strftime('%Y%m%d%H')
    start_date_index = next(i for i, v in enumerate(weather_data["date"]) if v == start_date)
    weather_data.drop(weather_data.head(start_date_index).index, inplace=True)

end_date_weather = pd.to_datetime(pd.Series(weather_data["date"].iloc[-1]), format="%Y%m%d%H")
end_date_data = pd.to_datetime(pd.Series(hourly_data["date"].iloc[-1]), format="%d.%m.%Y %H:%M")
if end_date_weather[0] <= end_date_data[0]:
    end_date = end_date_weather[0].strftime('%d.%m.%Y %H:%M')
    print(end_date)
    end_date_index = next(i for i, v in enumerate(reversed(hourly_data["date"]), 1) if v == end_date) - 1
    hourly_data.drop(hourly_data.tail(end_date_index).index, inplace=True)
else:
    end_date = end_date_data[0].strftime('%Y%m%d%H')
    end_date_index = next(i for i, v in enumerate(reversed(weather_data["date"]), 1) if v == end_date)
    weather_data.drop(weather_data.tail(end_date_index).index, inplace=True)

# set new indexes s.t. weather_data and hourly_data have the same index
weather_data["index"] = list(range(len(weather_data)))
weather_data = weather_data.set_index("index").rename_axis(None)
hourly_data["index"] = list(range(len(hourly_data)))
hourly_data = hourly_data.set_index("index").rename_axis(None)

print(len(weather_data["humidity"]), hourly_data)

if plot_boolean:
    print("humidity and temperature")
    for meter in df.columns:  # columns of df_copy is subset of hourly_data columns and contains only meter names
        for target_season in ["summer", "transition", "winter"]:

            testModel_humidity = LinearRegression()
            humidity = weather_data["humidity"]
            humidity_regression = humidity[(hourly_data["season"] == target_season) & (hourly_data[meter].notna())].\
                values.reshape(-1, 1)
            data_regression = hourly_data[(hourly_data["season"] == target_season) & hourly_data[meter].notna()][meter]
            testModel_humidity.fit(humidity_regression, data_regression)

            intercept = testModel_humidity.intercept_
            slope = testModel_humidity.coef_
            r_sq_hum = testModel_humidity.score(humidity_regression, data_regression)
            x = np.array(humidity_regression)
            plt.plot(humidity_regression, data_regression, 'o', color="orange")
            plt.ylabel("Energy Consumption [kW]")
            plt.plot(x, slope[0]*x+intercept, color="red")
            # todo make sure (sub-)folders exist
            pathlib.Path('plots/' + city + '/regression_humidity/').mkdir(parents=True, exist_ok=True)
            filename = 'plots/' + city + '/regression_humidity/' + meter + '_' + target_season + '_.pdf'
            plt.savefig(filename, dpi=1200)
            plt.clf()

            testModel_temperature = LinearRegression()
            temperature = weather_data["temperature"]
            temperature_regression = temperature[(hourly_data["season"] == target_season) &
                                                 (hourly_data[meter].notna())].values.reshape(-1, 1)
            testModel_temperature.fit(temperature_regression, data_regression)

            intercept = testModel_temperature.intercept_
            slope = testModel_temperature.coef_
            r_sq_temp = testModel_temperature.score(temperature_regression, data_regression)
            print(meter, round(r_sq_hum, 5), round(r_sq_temp, 5))
            x = np.array(temperature_regression)
            plt.plot(temperature_regression, data_regression, 'o', color="orange")
            plt.ylabel("Energy Consumption [kW]")
            plt.plot(x, slope[0] * x + intercept, color="red")
            pathlib.Path('plots/' + city + '/regression_temperature/').mkdir(parents=True, exist_ok=True)
            filename = 'plots/' + city + '/regression_temperature/' + meter + '_' + target_season + '_.pdf'
            plt.savefig(filename, dpi=1200)
            plt.clf()

if plot_boolean & (city == "city1"):  # todo city 1 has utilization data?
    # the quarters 2:00, 2:15, 2:30, 2:45 do not exist
    forward_dates = get_time_shift_forward_dates()
    df_copy = df.copy()
    for date in list(reversed(forward_dates)):  # start from the back otherwise indices don't match
        index = time_df.index[time_df["From"] == date + ' 01:45'].tolist()
        if index:
            empty_array = np.empty(len(df.columns))
            empty_array[:] = np.NaN  # empty array
            empty_array = pd.Series(empty_array)
            empty_df_entry = pd.DataFrame(data=[empty_array, empty_array, empty_array, empty_array],
                                          columns=df_copy.columns)
            df_copy = pd.concat([df_copy.iloc[:index[0] + 1],
                                 empty_df_entry,
                                 df_copy.iloc[index[0] + 1:]], ignore_index=True)
            empty_time_array = np.empty(len(time_df.columns))
            empty_time_array[:] = np.NaN  # empty array
            empty_time_array = pd.Series(empty_time_array)
            empty_time_df_entry = pd.DataFrame(data=[empty_time_array, empty_time_array, empty_time_array,
                                                     empty_time_array], columns=time_df.columns)
            time_df = pd.concat([time_df.iloc[:index[0] + 1],
                                 empty_time_df_entry,
                                 time_df.iloc[index[0] + 1:]], ignore_index=True)

    # the quarters 2:00, 2:15, 2:30, 2:45 occur twice -> calc average of two succeeding values
    back_dates = get_time_shift_back_dates()
    for date in back_dates:
        index = time_df.index[time_df["From"] == date + ' 01:45'].tolist()
        if index:
            temp = df_copy.iloc[index[0] + 1: index[0] + 9]
            temp = temp.groupby(np.arange(len(temp)) // 2).mean()
            df_copy = pd.concat([df_copy.iloc[:index[0] + 1],
                                 temp,
                                 df_copy.iloc[index[0] + 9:]], ignore_index=True)
            time_df = pd.concat([time_df.iloc[:index[0] + 1],
                                 time_df.iloc[index[0] + 5:]], ignore_index=True)
    # get utilization and time from modeling
    utilization = getUtilization()
    utilization_time = getDateAndTime()

    # restrict data to observation period
    observation_start_index = next(i for i, v in enumerate(time_df["From"]) if v == utilization_time[0])
    df_copy.drop(df_copy.head(observation_start_index).index, inplace=True)
    time_df.drop(time_df.head(observation_start_index).index, inplace=True)

    observation_end_index = next(i for i, v in enumerate(time_df["From"]) if v == utilization_time[-1])
    df_copy.drop(df_copy.tail(len(df_copy) - observation_end_index - 1).index, inplace=True)
    time_df.drop(time_df.tail(len(time_df) - observation_end_index - 1).index, inplace=True)

    # free some memory
    del utilization_time

    utilization = pd.DataFrame(data=utilization, columns=["utilization"], index=df_copy.index)

    for meter in df_copy.columns:
        for target_season in ["summer", "transition", "winter"]:

            testModel_humidity = LinearRegression()
            utilization_regression = utilization[(time_df["season"] == target_season) &
                                                 (df_copy[meter].notna())]["utilization"].values.reshape(-1, 1)
            data_regression = df_copy[(time_df["season"] == target_season) & df_copy[meter].notna()][meter]
            testModel_humidity.fit(utilization_regression, data_regression)

            intercept = testModel_humidity.intercept_
            slope = testModel_humidity.coef_
            r_sq = testModel_humidity.score(utilization_regression, data_regression)
            print(round(r_sq, 5))
            x = np.array(utilization_regression)
            plt.plot(utilization_regression, data_regression, 'o', color="orange")
            plt.ylabel("Energy Consumption [kW]")
            plt.plot(x, slope[0]*x+intercept, color="red")
            pathlib.Path('plots/' + city + '/regression_utilization/').mkdir(parents=True, exist_ok=True)
            filename = 'plots/' + city + '/regression_utilization/' + meter + '_' + target_season + '_.pdf'
            plt.savefig(filename, dpi=1200)
            plt.clf()
    del utilization
