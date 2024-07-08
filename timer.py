import tkinter as tk
from tkinter import messagebox
import customtkinter
from timer_library import convert_seconds, get_count_thread, get_pomodoro_thread, start_count, pomodoro_counter, save_pomodoro, get_pomodoros
import threading
import ctypes


class ThreadChan(threading.Thread):

    def __init__(self, callback_func, thread_name, **kwargs):
        # super(threading.Thread, self).__init__(**kwargs)
        threading.Thread.__init__(self, **kwargs)
        self.callback_func = callback_func
        self.thread_name = thread_name

    def get_id(self):
 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
        
    def raise_exception(self, forced=False):
        if not forced:
            self.callback_func(msg='Counter done!') if self.thread_name == 'countdown' else self.callback_func(msg='Pomodoro done!')
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

        

class Timer:

    def __init__(self):
        
        self.countdown_amount = '00:00:00'
        self.seconds = 0
        self.hours_time = 0
        self.minutes_time = 0
        self.seconds_time = 0

        self.root = tk.Tk()
        self.root.geometry('800x500')
        self.root.title('Timer Chan')

        self.layout = tk.Frame(self.root, background='#ff0000')
        self.layout.columnconfigure(0, weight=1)
        self.layout.columnconfigure(1, weight=1)
        self.layout.columnconfigure(2, weight=1)
        self.layout.columnconfigure(3, weight=1)

        self.layout.rowconfigure(0, weight=1)


        self.layout.pack(fill='both', expand=True)

        self.side = tk.Frame(self.layout, background='#242424')
        self.side.grid(column=0, row=0, sticky='wesn')

        self.countdown_btn = tk.Button(self.side, text='Countdown', font=('Arial', 16), height=3, command=self.open_countdown, background='#383838', fg='white')
        self.pomodoro_btn = tk.Button(self.side, text='Pomodoro', font=('Arial', 16), height=3, command=self.open_pomodoro, background='#383838', fg='white')
        self.countdown_btn.pack(fill='x')
        self.pomodoro_btn.pack(fill='x')

        self.main = tk.Frame(self.layout, background='#383838')
        self.main.grid(column=1,columnspan=3, row=0, sticky='nsew')
        
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        

        self.open_countdown()


    def open_countdown(self):
        children = self.main.winfo_children()
        if len(children) > 0:
            for child in children:
                child.destroy()

        self.label = tk.Label(self.main, text='CountDown', font=('Arial', 18), height=3, background='#383838', fg='white')
        self.label.pack(fill='x')

        self.container = tk.Frame(self.main, background='#383838')
        self.container.pack(fill='both', expand=True)

        
        self.time_container = tk.Frame(self.container, background='#383838')
        self.time_container.pack(padx=20, pady=20, fill='x', expand=True,  anchor='ne')

        self.time_container.columnconfigure(0, weight=1)
        self.time_container.columnconfigure(1, weight=1)
        self.time_container.columnconfigure(2, weight=1)

        self.hours_field = tk.Text(self.time_container, font=('Arial', 60), height=1, width=2, padx=5, pady=5, background='#242424', fg='white')
        self.hours_field.insert(tk.END, '00')
        self.hours_field.grid(column=0, row=0)
        
        self.minutes_field = tk.Text(self.time_container, font=('Arial', 60), height=1, width=2, padx=5, pady=5, background='#242424', fg='white')
        self.minutes_field.insert(tk.END, '00')
        self.minutes_field.grid(column=1, row=0)

        self.seconds_field = tk.Text(self.time_container, font=('Arial', 60), height=1, width=2, padx=5, pady=5, background='#242424', fg='white')
        self.seconds_field.insert(tk.END, '00')
        self.seconds_field.grid(column=2, row=0)

        self.btns_container = tk.Frame(self.container, background='#383838', height=10)
        self.btns_container.pack(padx=20, pady=30, fill='x', expand=True, anchor='se')

        self.btns_container.columnconfigure(0, weight=1)
        self.btns_container.columnconfigure(1, weight=1)
        self.btns_container.columnconfigure(2, weight=1)

        self.start_btn = tk.Button(self.btns_container, text='Start Count', padx=5, pady=5, font=('Arial', 14), background='#242424', fg='white', height=1, command=self.start_counter)
        self.start_btn.grid(column=0, row=0)

        self.pause_btn = tk.Button(self.btns_container, text='Pause Count', padx=5, pady=5, font=('Arial', 14), background='#242424', fg='white', height=1, command=self.pause_count)
        self.pause_btn.grid(column=1, row=0)

        self.reset_btn = tk.Button(self.btns_container, text='Reset Count', padx=5, pady=5, font=('Arial', 14), background='#242424', fg='white', height=1, command=self.reset_count)
        self.reset_btn.grid(column=2, row=0)

        self.count_started = False

    def start_counter(self):

        if self.count_started and self.count_event and not self.count_event.is_set():
            self.count_event.set()
            return

        hours = self.hours_field.get('1.0', tk.END)
        minutes = self.minutes_field.get('1.0', tk.END)
        seconds = self.seconds_field.get('1.0', tk.END)
        count_time = f'{hours[:-1]}:{minutes[:-1]}:{seconds[:-1]}'


        seconds_time = convert_seconds(count_time)[0]
        if seconds_time > 0:
            self.count_event = threading.Event()
            self.count_thread = ThreadChan(target=start_count, args=(count_time, self.hours_field, self.minutes_field, self.seconds_field, self.count_event), callback_func=self.handle_stop_count, thread_name='countdown')
            
            get_count_thread(self.count_thread)
            
            self.count_thread.start()
            self.count_event.set()
            self.count_started = True


    def pause_count(self):
        if self.count_event and self.count_event.is_set():
            self.count_event.clear()

            self.pause_btn.config(text='Resume Count')
        
        elif self.count_event and not self.count_event.is_set() and self.count_started:
            self.count_event.set()
            
            self.pause_btn.config(text='Pause Count')
    
    def reset_count(self):
        
        if not self.count_event.is_set():
            self.count_event.set()

        self.count_thread.raise_exception()
        self.count_thread.join()

        self.hours_field.delete('1.0', 'end')
        self.minutes_field.delete('1.0', 'end')
        self.seconds_field.delete('1.0', 'end')


        self.hours_field.insert('end', '00')
        self.minutes_field.insert('end', '00')
        self.seconds_field.insert('end', '00')

    def handle_stop_count(self, msg):

        messagebox.showinfo(title='Finished', message=msg)
        
        try:
            if self.count_thread:
                self.count_started = False            
                self.start_btn.configure(text='Start Count')
        except:
            try:
                if self.pomodoro_thread:
                    self.pomodoro_started = False
                    self.start_btn.configure(text='Start Pomodoro')
            except:
                pass
        
        self.count_event = None
        self.count_thread = None
        self.pomodoro_event = None
        self.pomodoro_thread = None

    def open_pomodoro(self):
        children = self.main.winfo_children()
        if len(children) > 0:
            for child in children:
                child.destroy()
        
        self.label = tk.Label(self.main, text='Pomodoro', font=('Arial', 18), height=3, background='#383838', fg='white')
        self.label.pack(fill='x')

        self.container = tk.Frame(self.main, background='#383838')
        self.container.pack(fill='both', expand=True)
        
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.container.columnconfigure(2, weight=1)

        self.container.rowconfigure(0, weight=1)

        self.settings_container = tk.Frame(self.container, background='#383838')
        self.settings_container.grid(column=0, columnspan=2, row=0, sticky='wens')

        self.saved_settings = tk.Frame(self.container, background='#242424')
        self.saved_settings.grid(column=2, row=0, sticky='wens')

        self.session_label = tk.Label(self.settings_container, text='Session time', font=('Arial', 16), background='#383838', fg='white')
        self.session_label.pack(padx=10, pady=10, anchor='nw')

        self.session_settings_container = tk.Frame(self.settings_container, background='#383838', height=10)
        self.session_settings_container.pack(padx=10, pady=0, anchor='nw', fill='x')

        self.session_settings_container.columnconfigure(0, weight=1)
        self.session_settings_container.columnconfigure(1, weight=1)
        self.session_settings_container.columnconfigure(2, weight=1)

        self.session_hours_field = tk.Text(self.session_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.session_hours_field.insert(tk.END, '00')
        self.session_hours_field.grid(column=0, row=0)

        self.session_minutes_field = tk.Text(self.session_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.session_minutes_field.insert(tk.END, '00')
        self.session_minutes_field.grid(column=1, row=0)
        
        self.session_seconds_field = tk.Text(self.session_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.session_seconds_field.insert(tk.END, '00')
        self.session_seconds_field.grid(column=2, row=0)

        self.break_label = tk.Label(self.settings_container, text='Break time', font=('Arial', 16), background='#383838', fg='white')
        self.break_label.pack(padx=10, pady=(30, 10), anchor='w')
        self.break_settings_container = tk.Frame(self.settings_container, background='#383838', height=10)
        self.break_settings_container.pack(padx=10, pady=0, fill='x')

        self.break_settings_container.columnconfigure(0, weight=1)
        self.break_settings_container.columnconfigure(1, weight=1)
        self.break_settings_container.columnconfigure(2, weight=1)    

        self.break_hours_field = tk.Text(self.break_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.break_hours_field.insert(tk.END, '00')
        self.break_hours_field.grid(column=0, row=0)

        self.break_minutes_field = tk.Text(self.break_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.break_minutes_field.insert(tk.END, '00')
        self.break_minutes_field.grid(column=1, row=0)
        
        self.break_seconds_field = tk.Text(self.break_settings_container, width=2, height=1, background='#242424', fg='white', font=('Arial', 30))
        self.break_seconds_field.insert(tk.END, '00')
        self.break_seconds_field.grid(column=2, row=0)


        self.sessions_number_container = tk.Frame(self.settings_container, background='#383838')
        self.sessions_number_container.pack(padx=10, pady=(30, 10), fill='x')


        self.sessions_number_label = tk.Label(self.sessions_number_container, text='Sessions number: ', font=('Arial', 16), background='#383838', fg='white')
        self.sessions_number_label.pack(side='left')

        self.sessions_number_field = tk.Text(self.sessions_number_container, font=('Arial', 18), height=1, width=1, padx=5, pady=0, background='#242424', fg='white')
        self.sessions_number_field.insert(tk.END, '4')
        self.sessions_number_field.pack(side='left')

        self.btns_container = tk.Frame(self.settings_container, background='#383838', height=10)
        self.btns_container.pack(padx=10, pady=10, side='bottom', fill='x')

        self.btns_container.columnconfigure(0, weight=1)
        self.btns_container.columnconfigure(1, weight=1)

        self.start_btn = tk.Button(self.btns_container, text='Start Pomodoro', font=('Arial', 16), background='#242424', fg='white', command=self.start_pomodoro)
        self.start_btn.grid(column=0, row=0)

        self.save_btn = tk.Button(self.btns_container, text='Save', font=('Arial', 16), background='#242424', fg='white', command=self.save_pomodoro)
        self.save_btn.grid(column=1, row=0)


        self.saved_settings_label = tk.Label(self.saved_settings, text='Saved Pomodoro', font=('Arial', 16), padx=10, pady=10, background='#242424', fg='white', border=1, borderwidth=1, highlightthickness=1)
        self.saved_settings_label.config(highlightbackground='white', highlightcolor='white')
        self.saved_settings_label.pack(fill='x')

        self.saved_settings_container = customtkinter.CTkScrollableFrame(self.saved_settings,  fg_color='#242424', corner_radius=0)
        self.saved_settings_container.pack(fill='both', expand=True)

        self.saved_pomodoros_data = self.get_saved_pomodoros()

        for p in self.saved_pomodoros_data:
            container = tk.Frame(self.saved_settings_container, background='#383838', border=1, borderwidth=1, highlightthickness=1)
            session_label = tk.Label(container, text=f'Session time: {p["session_time"]}', font=('Arial', 16), background='#383838', fg='white')
            break_label = tk.Label(container, text=f'Break time: {p["break_time"]}', font=('Arial', 16), background='#383838', fg='white')
            sessions_num_label = tk.Label(container, text=f'Sessions Num: {p["sessions_number"]}', font=('Arial', 16), background='#383838', fg='white')

            container.pack(fill='x', expand=True)
            session_label.pack(fill='x', padx=10, pady=10)
            break_label.pack(fill='x', padx=10, pady=10)
            sessions_num_label.pack(fill='x', padx=10, pady=10)

            container.bind('<Button-1>',lambda e, s=p["session_time"], b=p["break_time"], ss=p["sessions_number"]: self.set_pomodoro(e, s, b, ss))


        self.pomodoro_started = False

    def set_pomodoro(self, e, session_time, break_time, sessions_number):

        if self.pomodoro_started:
            return

        s_hr = session_time.split(':')[0]
        s_min = session_time.split(':')[1]
        s_sec = session_time.split(':')[2]

        b_hr = break_time.split(':')[0]
        b_min = break_time.split(':')[1]
        b_sec = break_time.split(':')[2]

        self.session_hours_field.delete('1.0', 'end')
        self.session_minutes_field.delete('1.0', 'end')
        self.session_seconds_field.delete('1.0', 'end')
        self.break_hours_field.delete('1.0', 'end')
        self.break_minutes_field.delete('1.0', 'end')
        self.break_seconds_field.delete('1.0', 'end')
        self.sessions_number_field.delete('1.0', 'end')

        self.session_hours_field.insert('end', s_hr)
        self.session_minutes_field.insert('end', s_min)
        self.session_seconds_field.insert('end', s_sec)
        self.break_hours_field.insert('end', b_hr)
        self.break_minutes_field.insert('end', b_min)
        self.break_seconds_field.insert('end', b_sec)
        self.sessions_number_field.insert('end', str(sessions_number))

    def start_pomodoro(self):

        if self.pomodoro_started:
            self.pomodoro_thread.raise_exception(forced=True)
            self.pomodoro_thread.join()

            self.session_hours_field.delete('1.0', 'end')
            self.session_minutes_field.delete('1.0', 'end')
            self.session_seconds_field.delete('1.0', 'end')
            self.break_hours_field.delete('1.0', 'end')
            self.break_minutes_field.delete('1.0', 'end')
            self.break_seconds_field.delete('1.0', 'end')
            self.sessions_number_field.delete('1.0', 'end')

            self.session_hours_field.insert('end', '00')
            self.session_minutes_field.insert('end', '00')
            self.session_seconds_field.insert('end', '00')
            self.break_hours_field.insert('end', '00')
            self.break_minutes_field.insert('end', '00')
            self.break_seconds_field.insert('end', '00')
            self.sessions_number_field.insert('end', '0')
        
            self.start_btn.config(text='Start Pomodoro')

            self.pomodoro_started = False

            return 1

        self.pomodoro_started = True
        session_hours = self.session_hours_field.get('1.0', 'end')
        session_minutes = self.session_minutes_field.get('1.0', 'end')
        session_seconds = self.session_seconds_field.get('1.0', 'end')
        self.session_time = f'{session_hours[:-1]}:{session_minutes[:-1]}:{session_seconds[:-1]}'

        break_hours = self.break_hours_field.get('1.0', 'end')
        break_minutes = self.break_minutes_field.get('1.0', 'end')
        break_seconds = self.break_seconds_field.get('1.0', 'end')
        self.break_time = f'{break_hours[:-1]}:{break_minutes[:-1]}:{break_seconds[:-1]}'

        self.sessions_number = int(self.sessions_number_field.get('1.0', 'end'))

        self.pomodoro_event = threading.Event()
        self.pomodoro_thread = ThreadChan(target=pomodoro_counter, args=(self.session_hours_field, self.session_minutes_field, self.session_seconds_field, self.break_hours_field, self.break_minutes_field, self.break_seconds_field, self.sessions_number_field, self.pomodoro_event, self.session_time, self.break_time, self.sessions_number, self.break_start_msg, self.session_start_msg), callback_func=self.handle_stop_count, thread_name='pomodoro')

        get_pomodoro_thread(self.pomodoro_thread)

        self.start_btn.config(text='Stop Pomodoro')

        self.pomodoro_thread.start()
        self.pomodoro_event.set()


    def break_start_msg(self):
        messagebox.showinfo(title='Break time!', message='Break time!')

    def session_start_msg(self, session_num):
        messagebox.showinfo(title='Session Start', message=f'Session {session_num} started!')

    def save_pomodoro(self):

        if not self.pomodoro_started:
            session_hours = self.session_hours_field.get('1.0', 'end')
            session_minutes = self.session_minutes_field.get('1.0', 'end')
            session_seconds = self.session_seconds_field.get('1.0', 'end')
            session_time = f'{session_hours[:-1]}:{session_minutes[:-1]}:{session_seconds[:-1]}'

            break_hours = self.break_hours_field.get('1.0', 'end')
            break_minutes = self.break_minutes_field.get('1.0', 'end')
            break_seconds = self.break_seconds_field.get('1.0', 'end')
            break_time = f'{break_hours[:-1]}:{break_minutes[:-1]}:{break_seconds[:-1]}'

            sessions_number = int(self.sessions_number_field.get('1.0', 'end'))
        else:
            session_time = self.session_time
            break_time = self.break_time
            sessions_number = self.sessions_number

        session_seconds = convert_seconds(session_time)[0]
        break_seconds = convert_seconds(break_time)[0]

        if session_seconds > 0 and break_seconds > 0 and sessions_number > 0:
            save_pomodoro(session_time, break_time, sessions_number)

            self.saved_pomodoros_data = self.get_saved_pomodoros()

            for child in self.saved_settings_container.winfo_children():
                child.destroy()

            for p in self.saved_pomodoros_data:
                container = tk.Frame(self.saved_settings_container, background='#383838', border=1, borderwidth=1, highlightthickness=1)
                session_label = tk.Label(container, text=f'Session time: {p["session_time"]}', font=('Arial', 16), background='#383838', fg='white')
                break_label = tk.Label(container, text=f'Break time: {p["break_time"]}', font=('Arial', 16), background='#383838', fg='white')
                sessions_num_label = tk.Label(container, text=f'Sessions Num: {p["sessions_number"]}', font=('Arial', 16), background='#383838', fg='white')

                container.pack(fill='x', expand=True)
                session_label.pack(fill='x', padx=10, pady=10)
                break_label.pack(fill='x', padx=10, pady=10)
                sessions_num_label.pack(fill='x', padx=10, pady=10)

                container.bind('<Button-1>',lambda e, s=p["session_time"], b=p["break_time"], ss=p["sessions_number"]: self.set_pomodoro(e, s, b, ss))


            return 1



    def get_saved_pomodoros(self):
        pomodoros = get_pomodoros()

        return pomodoros

    def on_close(self):
        try:
            if self.count_event and self.count_thread:
                self.count_event.set()
                self.count_thread.raise_exception()
                self.count_thread.join()
        except AttributeError:
            
            try:
                if self.pomodoro_event and self.pomodoro_started:
                    self.pomodoro_event.set()
                    self.pomodoro_thread.raise_exception()
                    self.pomodoro_thread.join()
            except AttributeError:
                pass

        self.root.destroy()

    def run(self):
        self.root.mainloop()


Timer().run()