# for a given input time data frame or array check what kind of days of week it is or annotates possible holidays
import datetime
import pandas as pd

__author__ = "Hendrik Sanhen, and Dr Nancy Retzlaff"
__copyright__ = "Copyright 2007, The Cogent Project"
__credits__ = ["Hendrik Sanhen", "Nancy Retzlaff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Dr Nancy Retzlaff"
__email__ = "retzlaff@wifa.uni-leipzig.de"
__status__ = "Prototype"

# currently, data does not precede 2019 -- needs adjustment in case of data dating further back
holidays = ["01.01.2019", "19.04.2019", "21.04.2019", "22.04.2019", "01.05.2019", "30.05.2019", "09.06.2019",
            "10.06.2019", "03.10.2019", "25.12.2019", "26.12.2019", "01.01.2020", "10.04.2020", "12.04.2020",
            "13.04.2020", "01.05.2020", "21.05.2020", "31.05.2020", "01.06.2020", "03.10.2020", "25.12.2020",
            "26.12.2020", "01.01.2021", "02.04.2021", "04.04.2021", "05.04.2021", "01.05.2021", "13.05.2021",
            "23.05.2021", "24.05.2021", "03.10.2021", "25.12.2021", "26.12.2021"]  # German holidays


def getFullDateInfo(date_and_time_df, city):
    day_of_week = []
    season = []
    kind_of_day = []  # 0 for normal day of week, 1 for Saturday and 2 for Sunday or holiday
    months = []
    quarter_of_week = []

    global holidays

    # todo add location specific holidays here
    if city == "MyCity":
        holidays += []
        # holidays specific to MyCity

    index = 0
    for date_entry in date_and_time_df[date_and_time_df.columns[0]]:
        date_string = str(date_entry).split(" ")[0]
        time_string = str(date_entry).split(" ")[1]

        day = date_string.split(".")[0]
        month = date_string.split(".")[1]
        weekday = int(pd.to_datetime(pd.Series(date_entry), format="%d.%m.%Y %H:%M").dt.dayofweek)

        hour = int(time_string.split(":")[0])
        minutes = time_string.split(":")[1]
        current_quarter = (weekday * 96) + (hour * 4)
        if minutes == "15":
            current_quarter = current_quarter + 1
        elif minutes == "30":
            current_quarter = current_quarter + 2
        elif minutes == "45":
            current_quarter = current_quarter + 3

        day_of_week.append(weekday)
        months.append(int(month))
        quarter_of_week.append(current_quarter)

        if month in ["11", "12", "01", "02"] or (month == "03" and int(day) < 21):
            season.append("winter")
        elif month in ["06", "07", "08"] or (month == "05" and int(day) > 14) or (month == "09" and int(day) < 15):
            season.append("summer")
        else:
            season.append("transition")

        # fill kindOfDay list
        if date_string in holidays or weekday == 6:
            kind_of_day.append(2)  # sundays and holidays
        elif "24.12." in date_string or "31.12." in date_string or weekday == 5:
            kind_of_day.append(1)  # according to DOI: 10.3139/104.111977
        else:
            kind_of_day.append(0)  # Mon - Fri, not holidays

        index += 1

    date_and_time_df["dayOfWeek"] = day_of_week
    date_and_time_df["season"] = season
    date_and_time_df["kindOfDay"] = kind_of_day
    date_and_time_df["months"] = months
    date_and_time_df["quarter_of_week"] = quarter_of_week

    return date_and_time_df


def get_date_info(start_date, end_date, city):
    date_df = pd.DataFrame([])
    current_date = pd.to_datetime(pd.Series(start_date), format="%d.%m.%Y")[0]
    end_date = pd.to_datetime(pd.Series(end_date), format="%d.%m.%Y")[0]
    dates = []

    while current_date <= end_date:
        dates.append(current_date.strftime("%d.%m.%Y %H:%M"))
        current_date += datetime.timedelta(days=1)

    date_df["dates"] = dates
    date_df = getFullDateInfo(date_df, city)
    print(date_df)
    return date_df


def get_time_shift_forward_dates():
    return ["31.03.2019", "29.03.2020", "28.03.2021", "27.03.2022"]


def get_time_shift_back_dates():
    return ["28.10.2018", "27.10.2019", "25.10.2020", "31.10.2021", "30.10.2022"]

