# Function to get current age

# Function to check if within time frame returns true if works, false if not
def check_time(appointment_time, volunteer_time):
    a_times = appointment_time.split("-")
    format_num = a_times[0].split(":")
    a_time_start = float(format_num[0]) + float(format_num[1])/100
    format_num = a_times[1].split(":")
    a_time_end = float(format_num[0]) + float(format_num[1]) / 100

    v_times = volunteer_time.split("-")
    format_num = v_times[0].split(":")
    v_time_start = float(format_num[0]) + float(format_num[1])/100
    format_num = v_times[1].split(":")
    v_time_end = float(format_num[0]) + float(format_num[1])/100
    if v_time_start < a_time_start < v_time_end and v_time_start < a_time_end < v_time_end:
        return True
    else:
        return False


