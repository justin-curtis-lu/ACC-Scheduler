import datetime
from datetime import date

# Function that returns the day of the week given a date in format: mm/dd/yyyy
def get_day(date):
    month, day, year = (int(i) for i in date.split('/'))
    born = datetime.date(year, month, day)
    return born.strftime("%A").lower()

# Function to check if minor or not if minor return true else return false
def check_age(dob):
    dob_list = dob.split("/")
    today = date.today()
    age = today.year - int(dob_list[2]) - ((today.month, today.day) < (int(dob_list[0]), int(dob_list[1])))
    if age < 18:
        return True
    else:
        return False


# Function to check if volunteer is available at appointment time. Returns true if available, false if not
def check_time(appointment_time, volunteer_time):
    a_times = appointment_time.split("-")
    format_num = a_times[0].split(":")
    a_time_start = float(format_num[0]) + float(format_num[1]) / 100
    format_num = a_times[1].split(":")
    a_time_end = float(format_num[0]) + float(format_num[1]) / 100

    v_times = volunteer_time.split("-")
    format_num = v_times[0].split(":")
    v_time_start = float(format_num[0]) + float(format_num[1]) / 100
    format_num = v_times[1].split(":")
    v_time_end = float(format_num[0]) + float(format_num[1]) / 100
    if v_time_start <= a_time_start < v_time_end and v_time_start < a_time_end <= v_time_end:
        return True
    else:
        return False
