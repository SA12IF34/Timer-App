import time
import json


seconds = 0
hours_time = 0
minutes_time = 0
seconds_time = 0
hours_input = '00'
minutes_input = '00'
seconds_input = '00'
count_event = None
count_thread = None
stop_flag = False
pomodoro_thread = None

def set_time(time):
    
    return time

def convert_seconds(countdown_amount):
    global seconds
    global hours_time
    global minutes_time
    global seconds_time

    if len(countdown_amount) > 0 and len(countdown_amount.split(':')) == 3:
        slipted_time = countdown_amount.split(':')

        seconds = 0

        for i in range(len(slipted_time)):
            if int(slipted_time[i]) == 0:
                continue

            int_time = int(slipted_time[i])
            if i == 0:
                seconds += int_time*60*60
                hours_time = int_time*60*60
            elif i == 1:
                seconds += int_time*60
                minutes_time = int_time*60

            elif i == 2:
                seconds += int_time
                seconds_time = int_time

        return seconds, hours_time, minutes_time, seconds_time


def set_stop_flag(value):
    global stop_flag
    stop_flag = value
    return 0

def get_count_thread(thread):
    global count_thread
    count_thread = thread
    return

def get_pomodoro_thread(thread):
    global pomodoro_thread
    pomodoro_thread = thread
    return

def countdown_seconds(seconds_range, countdown_amount):
    global seconds
    global seconds_input
    global count_event
    global count_thread

    
    for i in range(seconds_range):
        global stop_flag
        if stop_flag:
            return -1
        
        count_event.wait()
        if count_event.is_set():
            time.sleep(1)
            seconds -= 1

            if type(countdown_amount) == str:
                countdown_amount = countdown_amount.split(':')

            val = str(int(countdown_amount[2])-1)
            val = val if len(val) == 2 else '0'+val
            countdown_amount[2] = val
            countdown_amount = ':'.join(countdown_amount)

            seconds_input.delete('1.0', 'end')
            seconds_input.insert('end', val)

            if seconds == 0:
                if count_thread is not None:
                    count_thread.raise_exception()
                    count_thread.join()
                    count_thread = None



def countdown_minutes(minutes_range, countdown_amount):
    global minutes_input
    global seconds_input
    global stop_flag


    for i in range(minutes_range):
        if stop_flag:
            return -1
        if type(countdown_amount) == str:
            countdown_amount = countdown_amount.split(':')
        
        minutes_range -= 1

        val = str(minutes_range)
        val = val if len(val) == 2 else '0'+val
        countdown_amount[1] = val
        countdown_amount[2] = '60'

        minutes_input.delete('1.0', 'end')
        minutes_input.insert('end', val)

        seconds_input.delete('1.0', 'end')
        seconds_input.insert('end', '60')

        countdown_seconds(60, countdown_amount)


def countdown_hours(hours_range, countdown_amount):
    global hours_input
    global minutes_input
    global stop_flag

    

    for i in range(hours_range):
        if stop_flag:
            return -1
        
        if type(countdown_amount) == str:
            countdown_amount = countdown_amount.split(':')

        hours_range -= 1
        val = str(hours_range)
        val = val if len(val) == 2 else '0'+val
        countdown_amount[0] = val
        countdown_amount[1] = '60'

        hours_input.delete('1.0', 'end')
        hours_input.insert('end', val)

        minutes_input.delete('1.0', 'end')
        minutes_input.insert('end', '60')

        countdown_minutes(60, countdown_amount)


def start_count(countdown_amount, h_input, m_input, s_input, event):
    global seconds
    global seconds_time
    global minutes_time
    global hours_time
    global hours_input
    global minutes_input
    global seconds_input
    global count_event
    global stop_flag

    hours_input = h_input
    minutes_input = m_input
    seconds_input = s_input

    count_event = event
    

    if seconds == 0:
        return -1

    if seconds_time > 0 and (seconds - seconds_time) == (hours_time+minutes_time):
        countdown_seconds(seconds_time, countdown_amount)
        
    if minutes_time > 0 and (seconds - minutes_time) == (hours_time):
        num_of_mins = int(minutes_time/60)

        countdown_minutes(num_of_mins, countdown_amount)
            
    if hours_time > 0 and (seconds - hours_time) == 0:
        num_of_hours = int((hours_time/60)/60)

        countdown_hours(num_of_hours, countdown_amount)

    if stop_flag:
        return -1

def pomodoro_counter(s_hr_field, s_min_field, s_sec_field, b_hr_field, b_min_field, b_sec_field, s_num_field, event, session_time='00:30:00', break_time='00:10:00', sessions_number=4, break_start_callback=None, session_start_callback=None):
    global pomodoro_thread
    global count_thread

    count_thread = None

    i=0
    while i < sessions_number:

        convert_seconds(session_time)
        start_count(session_time, s_hr_field, s_min_field, s_sec_field, event)
        s_num_field.delete('1.0', 'end')
        s_num_field.insert('end', str(sessions_number-(i+1)))

        if i < sessions_number-1:
            
            if break_start_callback:
                break_start_callback()

            convert_seconds(break_time)
            start_count(break_time, b_hr_field, b_min_field, b_sec_field, event)
        
        if session_start_callback and i < sessions_number-1:
            session_start_callback(i+2)

        i+=1
    

    if pomodoro_thread:
        pomodoro_thread.raise_exception()
        pomodoro_thread = None
        
        
    

def save_pomodoro(session_time='00:30:00', break_time='00:10:00', sessions_number=4):
    try:
                
        data: list = json.load(open('pomodoro.json', 'r'))
        
        data.append({
            'session_time': session_time,
            'break_time': break_time,
            'sessions_number': sessions_number
        })

        with open('pomodoro.json', 'w') as file:
            json.dump(data, file, indent=2)
            print('file edited')

        return 1

    except FileNotFoundError:
        
        with open('pomodoro.json', 'w') as file:
            json.dump([
                {
                'session_time': session_time,
                'break_time': break_time,
                'sessions_number': sessions_number
                }
            ], file, indent=2)
        print('file created')
        
        return 1

def get_pomodoros():

    try:
        data = json.load(open('pomodoro.json', 'r'))
        return data

    except json.decoder.JSONDecodeError:
        return []
    
    except FileNotFoundError:
        return []
    

