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


def format_times(start, end):
    return str(start) + ":00" + "-" + str(end) + ":00"
# takes in a list of boolean values and formats them accordingly into a list of time frames available for the day
# ex. [True, True, False, False, True] -> ["9:00-11:00", "13:00-14:00"]
def get_timeframes(list_of_times):
    start_time = 9
    end_time = 10
    formatted_times = []
    i = 0
    while i < 5:
        if list_of_times[i]:
            if i < 4:
                while list_of_times[i + 1]:
                    end_time += 1
                    i += 1
                    if i == 4:
                        break
            formatted_times.append(format_times(start_time, end_time))
            start_time = 9 + (end_time - 10)
        i += 1
        start_time += 1
        end_time += 1
    return formatted_times


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


# Function to check if the appointment time conflicts with an appointment already assigned to the volunteer
# returns false if theres no conflict true if there is a conflict
def appointment_conflict(appointment_time, conflict_time):
    a_times = appointment_time.split("-")
    format_num = a_times[0].split(":")
    a_time_start = float(format_num[0]) + float(format_num[1]) / 100
    format_num = a_times[1].split(":")
    a_time_end = float(format_num[0]) + float(format_num[1]) / 100

    c_times = conflict_time.split("-")
    format_num = c_times[0].split(":")
    c_time_start = float(format_num[0]) + float(format_num[1]) / 100
    format_num = c_times[1].split(":")
    c_time_end = float(format_num[0]) + float(format_num[1]) / 100
    if a_time_start < a_time_end <= c_time_start < c_time_end or c_time_start < c_time_end <= a_time_start < a_time_end:
        return False
    else:
        return True
