# tkinter_app

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo
from PIL import Image, ImageTk
from typing import List
import threading
import platform
from time import sleep
from .tango_bot import TangBotController
from .log import log
from enum import Enum


class BotEventType(Enum):
    HeadUp      = 'HEAD UP'
    HeadDown    = 'HEAD DOWN'
    HeadLeft    = 'HEAD LEFT'
    HeadRight   = 'HEAD RIGHT'
    HeadCenter  = 'HEAD CENTER'
    WaistLeft   = 'WAIST LEFT'
    WaistRight  = 'WAIST RIGHT'
    WaistCenter = 'WAIST CENTER'
    Forward     = 'FORWARD'
    Reverse     = 'REVERSE'
    TurnLeft    = 'TURN LEFT'
    TurnRight   = 'TURN RIGHT'
    Stop        = 'STOP'
    Speak       = 'SPEAK'

""" BotEventFrame

    Layouts
    -------------------------------------------------------------
    | event # | up/down buttons | event details | event options |
    -------------------------------------------------------------

"""
class BotEventFrame(ttk.Frame):
    # properties
    # bot_event: BotEvent
    event_number_label: ttk.Label

    # constructor
    def __init__(self, bot_event):
        super().__init__(EVENTS_VIEW_PORT_FRAME)
        self.bot_event: BotEvent = bot_event

        # Event Number Label
        # ---------------------------------------
        self.event_number_label = ttk.Label(self, text=self.event_num, anchor=tk.CENTER)

        # Up/Down Button Controls
        # ---------------------------------------
        self.up_button = ttk.Button(self)
        self.down_button = ttk.Button(self)
        self.up_button.config(command=lambda x = self.bot_event : moveEventUp(x))
        self.down_button.config(command=lambda x = self.bot_event : moveEventDown(x))
        # button images
        self.up_image = fetchTkImage('./assets/arrow.png', size=15)
        self.down_image = fetchTkImage('./assets/arrow.png', size=15, transpose=Image.ROTATE_180)
        self.up_button.config(image=self.up_image)
        self.down_button.config(image=self.down_image)

        # Event Details
        # ---------------------------------------
        self.details_frame = ttk.Frame(self)
        self.event_type_label = ttk.Label(self.details_frame)
        self.event_type_label.config(font=('Helvetica', 15))
        self.event_type_label.config(text=self.event_name)
        self.event_type_label.config(anchor=tk.W)
        self.event_type_label.pack(expand=True, fill='x')
        # time interval details
        if self.bot_event.time_interval is not None:
            self.time_details_label = ttk.Label(self.details_frame)
            self.time_details_label.config(text="Time: %s seconds" % self.bot_event.time_interval)
            self.time_details_label.config(anchor=tk.W)
            self.time_details_label.pack(expand=True, fill='x')
        # Speed (step) Level Label
        if self.bot_event.speed_step is not None:
            self.step_level_details_label = ttk.Label(self.details_frame)
            self.step_level_details_label.config(text='Speed Level: %s' % self.bot_event.speed_step)
            self.step_level_details_label.config(anchor=tk.W)
            self.step_level_details_label.pack(expand=True, fill='x')
        # Robot Speak Text
        if self.bot_event.speak_text is not None:
            self.speak_text_details_label = ttk.Label(self.details_frame)
            self.speak_text_details_label.config(text="Text: \"%s\"" % self.bot_event.speak_text)
            self.speak_text_details_label.pack()


        # Event Commands
        # ---------------------------------------
        self.delete_button = ttk.Button(self, text='Delete')
        self.delete_button.config(command=lambda x=self.bot_event : deleteEvent(x))


        # Add items
        # ---------------------------------------
        self.event_number_label.grid(column=0, row=0, rowspan=2, padx=5, pady=5)
        self.up_button.grid(column=1, row=0)
        self.down_button.grid(column=1, row=1)
        self.details_frame.grid(column=2, row=0, rowspan=2, sticky=tk.NW, padx=5, pady=5)
        self.delete_button.grid(column=3, row=0, sticky=tk.E)

        self.columnconfigure(3, weight=1)

        # add self to parent
        self.grid(column=0, row=self.row, sticky=tk.EW, padx=5, pady=5)



        # container = ttk.Frame(self, style='EventContainer.TFrame')
        # container.columnconfigure(2, weight=1)
        # # container.columnconfigure(1, weight=1)

        # num_label = ttk.Label(container, text=self.event_num, borderwidth=1, relief='solid', anchor="center")
        # num_label.grid(column=0, row=0, padx=5, pady=5, ipadx=5, ipady=5, sticky=tk.E)

        # details_frame = tk.Frame(container, bg='white')
        # details_frame.grid(column=2, row=0, padx=5, sticky=tk.W)

        # controls_frame = tk.Frame(container, bg='white')
        # controls_frame.grid(column=1, row=0)

        # type_label = tk.Label(details_frame, text=self.event_name, bg='white', font=('Helvetica', 20))
        # type_label.grid(column=0, row=0, sticky=tk.W)

        # if hasattr(self.bot_event, 'time_interval'):
        #     time_label = tk.Label(details_frame, text="%s seconds" % self.bot_event.time_interval, bg='white')
        #     time_label.grid(column=0, row=1, sticky=tk.W)

        # self.up_arrow_image = fetchTkImage('./assets/arrow.png', size=10)
        # self.down_arrow_image = fetchTkImage('./assets/arrow.png', size=10, transpose=Image.ROTATE_180)

        # up_button = ttk.Button(controls_frame, text='Up', command=lambda x = self.bot_event : moveEventUp(x))
        # down_button = ttk.Button(controls_frame, text='Down', command=lambda x = self.bot_event : moveEventDown(x))


        # up_button.config(image=self.up_arrow_image)
        # down_button.config(image=self.down_arrow_image)

        # up_button.pack()
        # down_button.pack()

        # delete_button = ttk.Button(container, text='Delete', command=lambda x = self.bot_event : deleteEvent(x))

        # delete_button.grid(column=3, row=0, sticky=tk.W)

        # container.grid(column=0, row=0, sticky=tk.EW)
        # self.grid(row=self.row, column=0, padx=5, pady=5, sticky=tk.EW)

    @property
    def row(self):
        return self.bot_event.row

    @property
    def event_num(self):
        return self.row + 1

    @property
    def event_name(self):
        return self.bot_event.event_type.value

class BotEvent:
    # properties
    event_type: BotEventType
    _time_interval: int = None
    _speed_step: int = None
    speak_text: str = None
    widget: BotEventFrame = None

    # constructor
    def __init__(self, event_type: BotEventType, time_interval: int = None, speed_step: int = None):
        self.event_type = event_type
        self.time_interval = time_interval
        self.speed_step = speed_step
        global EVENTS_DATA
        EVENTS_DATA.append(self)

    @property
    def time_interval(self):
        return self._time_interval

    @time_interval.setter
    def time_interval(self, time):
        self._time_interval = time

    @property
    def speed_step(self):
        return self._speed_step

    @speed_step.setter
    def speed_step(self, step):
        if step is None:
            self._speed_step == None
        else:
            step = int(step)
            possible_steps = [1, 2, 3]
            if step not in possible_steps:
                step = 1
            self._speed_step = step

    def createWidget(self):
        self.widget = BotEventFrame(bot_event=self)

    @property
    def row(self):
        global EVENTS_DATA
        return EVENTS_DATA.index(self)

    # TODO - implement speed step
    # TODO - implement time_interval
    def execute(self):
        # TODO - implement BotEventType.Speak
        if self.event_type == BotEventType.HeadUp:
            TANGO_BOT.moveHeadUp()
        elif self.event_type == BotEventType.HeadDown:
            TANGO_BOT.moveHeadDown()
        elif self.event_type == BotEventType.HeadLeft:
            TANGO_BOT.moveHeadLeft()
        elif self.event_type == BotEventType.HeadRight:
            TANGO_BOT.moveHeadRight()
        elif self.event_type == BotEventType.HeadCenter:
            TANGO_BOT.centerHead()
        elif self.event_type == BotEventType.WaistCenter:
            TANGO_BOT.centerWaist()
        elif self.event_type == BotEventType.WaistLeft:
            TANGO_BOT.moveWaistLeft()
        elif self.event_type == BotEventType.WaistRight:
            TANGO_BOT.moveWaistRight()
        elif self.event_type == BotEventType.Forward:
            TANGO_BOT.increaseWheelSpeed()
        elif self.event_type == BotEventType.Reverse:
            TANGO_BOT.decreaseWheelSpeed()
        elif self.event_type == BotEventType.TurnLeft:
            TANGO_BOT.turnLeft()
        elif self.event_type == BotEventType.TurnRight:
            TANGO_BOT.turnRight()
        elif self.event_type == BotEventType.Stop:
            TANGO_BOT.stop()


class ToolBarFrame(ttk.Frame):
    # properties
    play_image_file = './assets/play.png'
    stop_image_file = './assets/stop.png'
    play_image: ImageTk.PhotoImage
    stop_image: ImageTk.PhotoImage
    play_button: ttk.Button
    stop_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.play_image = fetchTkImage(self.play_image_file)
        self.stop_image = fetchTkImage(self.stop_image_file)

        self.play_button = ttk.Button(self, image=self.play_image, text='Play', compound=tk.LEFT, command=runEvents)
        self.stop_button = ttk.Button(self, image=self.stop_image, text='Stop', compound=tk.LEFT, command=stopRobot)


        self.play_button.pack(ipadx=5,expand=True, side='left')
        self.stop_button.pack(ipadx=5,expand=True, side='left')

        self.pack(padx=5)

class HeadControlsFrame(ttk.Frame):
    # properties
    arrow_image_file: str = './assets/arrow.png'
    center_image_file: str = './assets/center.png'
    up_arrow_image: ImageTk.PhotoImage
    down_arrow_image: ImageTk.PhotoImage
    left_arrow_image: ImageTk.PhotoImage
    right_arrow_image: ImageTk.PhotoImage
    center_image: ImageTk.PhotoImage
    up_button: ttk.Button
    down_button: ttk.Button
    left_button: ttk.Button
    right_button: ttk.Button
    center_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.up_arrow_image = fetchTkImage(self.arrow_image_file)
        self.down_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_180)
        self.left_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_90)
        self.right_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_270)
        self.center_image = fetchTkImage(self.center_image_file)

        self.up_button = ttk.Button(self, image=self.up_arrow_image, command=makeEventCreateCallback(BotEventType.HeadUp))
        self.down_button = ttk.Button(self, image=self.down_arrow_image, command=makeEventCreateCallback(BotEventType.HeadDown))
        self.left_button = ttk.Button(self, image=self.left_arrow_image, command=makeEventCreateCallback(BotEventType.HeadLeft))
        self.right_button = ttk.Button(self, image=self.right_arrow_image, command=makeEventCreateCallback(BotEventType.HeadRight))
        self.center_button = ttk.Button(self, image=self.center_image, command=makeEventCreateCallback(BotEventType.HeadCenter))

        self.up_button.grid(column=1, row=0, sticky=tk.EW)
        self.down_button.grid(column=1, row=2, sticky=tk.EW)
        self.left_button.grid(column=0, row=1, sticky=tk.EW)
        self.right_button.grid(column=2, row=1, sticky=tk.EW)
        self.center_button.grid(column=1, row=1, sticky=tk.EW)

        self.pack(expand=True, fill='both', padx=5, pady=5)

class WaistControlsFrame(ttk.Frame):
    # properties
    arrow_image_file: str = './assets/arrow.png'
    center_image_file: str = './assets/center.png'
    left_arrow_image: ImageTk.PhotoImage
    right_arrow_image: ImageTk.PhotoImage
    center_image: ImageTk.PhotoImage
    left_button: ttk.Button
    center_button: ttk.Button
    right_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.left_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_90)
        self.right_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_270)
        self.center_image = fetchTkImage(self.center_image_file)

        self.left_button = ttk.Button(self, image=self.left_arrow_image)
        self.center_button = ttk.Button(self, image=self.center_image)
        self.right_button = ttk.Button(self, image=self.right_arrow_image)

        self.left_button.config(command=makeEventCreateCallback(BotEventType.WaistLeft))
        self.center_button.config(command=makeEventCreateCallback(BotEventType.WaistCenter))
        self.right_button.config(command=makeEventCreateCallback(BotEventType.WaistRight))

        self.left_button.grid(column=0, row=0, sticky=tk.EW)
        self.center_button.grid(column=1, row=0, sticky=tk.EW)
        self.right_button.grid(column=2, row=0, sticky=tk.EW)

        self.pack(expand=True, fill='both', padx=5, pady=5)

class WheelControlsFrame(ttk.Frame):
    # properties
    arrow_image_file: str = './assets/arrow.png'
    center_image_file: str = './assets/center.png'
    up_arrow_image: ImageTk.PhotoImage
    down_arrow_image: ImageTk.PhotoImage
    left_arrow_image: ImageTk.PhotoImage
    right_arrow_image: ImageTk.PhotoImage
    center_image: ImageTk.PhotoImage
    forward_button: ttk.Button
    reverse_button: ttk.Button
    turn_left_button: ttk.Button
    turn_right_button: ttk.Button
    stop_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.forward_button = ttk.Button(self, text='Forwards')
        self.reverse_button = ttk.Button(self, text='Reverse')
        self.turn_left_button = ttk.Button(self, text='Turn Left')
        self.turn_right_button = ttk.Button(self, text='Turn Right')
        self.stop_button = ttk.Button(self, text='Stop')

        self.forward_button.config(command=lambda : makeCreateWheelEventSettingsFrame(event_type=BotEventType.Forward))
        self.reverse_button.config(command=lambda : makeCreateWheelEventSettingsFrame(event_type=BotEventType.Reverse))
        self.turn_left_button.config(command=lambda : makeCreateWheelEventSettingsFrame(event_type=BotEventType.TurnLeft))
        self.turn_right_button.config(command=lambda : makeCreateWheelEventSettingsFrame(event_type=BotEventType.TurnRight))
        self.stop_button.config(command=makeEventCreateCallback(BotEventType.Stop))

        self.up_arrow_image = fetchTkImage(self.arrow_image_file)
        self.down_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_180)
        self.left_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_90)
        self.right_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_270)
        self.center_image = fetchTkImage(self.center_image_file)

        self.forward_button.config(image=self.up_arrow_image)
        self.reverse_button.config(image=self.down_arrow_image)
        self.turn_left_button.config(image=self.left_arrow_image)
        self.turn_right_button.config(image=self.right_arrow_image)
        self.stop_button.config(image=self.center_image)

        self.forward_button.grid(column=1, row=0, sticky=tk.EW)
        self.reverse_button.grid(column=1, row=2, sticky=tk.EW)
        self.turn_left_button.grid(column=0, row=1, sticky=tk.EW)
        self.turn_right_button.grid(column=2, row=1, sticky=tk.EW)
        self.stop_button.grid(column=1, row=1, sticky=tk.EW)

        self.pack(expand=True, fill='both', padx=5, pady=5)

class EventSettingsFrame(ttk.Frame):
    # properties
    bot_event: BotEvent
    show_time: bool
    show_step: bool
    time_variable: tk.StringVar
    step_selection: tk.StringVar
    _time_value: int
    _step_value: int

    # constructor
    def __init__(self, bot_event: BotEvent, show_time: bool = False, show_step: bool = False):
        super().__init__(APP_INST)
        self.bot_event = bot_event
        self.show_time = show_time
        self.show_step = show_step
        self.time_variable = tk.StringVar()
        self.step_selection = tk.StringVar()

        print(self.show_time)

        self.time_value = 1
        self.step_value = 1
        # TODO - if bot_event.time_interval is not None?

        self.settings_label = ttk.Label(self)
        self.settings_label.config(text='Event Settings: %s' % self.bot_event.event_type.value)

        # time entry
        time_input_frame = ttk.Frame(self)
        self.time_entry = tk.Entry(time_input_frame)
        self.time_entry.config(textvariable=self.time_variable)
        self.time_entry.config(justify='center')
        self.time_entry.config(font=('Helvetica', 15))
        self.time_entry.config(state='disabled')
        self.time_entry.config(disabledbackground="white")
        self.time_entry.config(disabledforeground="black")
        # time up/down buttons
        self.time_up_button = ttk.Button(time_input_frame, text='Up', command=self.increaseTimeValue)
        self.time_down_button = ttk.Button(time_input_frame, text='Down', command=self.decreaseTimeValue)

        # step inputs
        step_input_frame = ttk.Frame(self)
        speed_one_option = ttk.Radiobutton(step_input_frame, text='Level One', value=1, variable=self.step_selection, command=self.stepValueChange)
        speed_two_option = ttk.Radiobutton(step_input_frame, text='Level Two', value=2, variable=self.step_selection, command=self.stepValueChange)
        speed_three_option = ttk.Radiobutton(step_input_frame, text='Level Three', value=3, variable=self.step_selection, command=self.stepValueChange)
        ttk.Label(step_input_frame, text='What level of speed?').pack(anchor='w')
        speed_one_option.pack(anchor='w')
        speed_two_option.pack(anchor='w')
        speed_three_option.pack(anchor='w')
        # add input_frame items
        self.time_entry.grid(column=0, row=0, rowspan=2, sticky=tk.NS)
        self.time_up_button.grid(column=1, row=0)
        self.time_down_button.grid(column=1, row=1)

        settings_actions_frame = ttk.Frame(self)
        save_button = ttk.Button(settings_actions_frame, text='Save', command=self.saveButtonAction)
        cancel_button = ttk.Button(settings_actions_frame, text='Cancel', command=self.cancelButtonAction)
        save_button.grid(column=0, row=0)
        cancel_button.grid(column=1, row=0)

        # add items
        self.settings_label.pack()
        if self.show_time:
            time_input_frame.pack()
        if self.show_step:
            step_input_frame.pack()
        settings_actions_frame.pack()

        self.pack()

    @property
    def time_value(self):
        return self._time_value

    @time_value.setter
    def time_value(self, time: int):
        if time < 1: time = 1
        self._time_value = time
        self.time_variable.set(f"{self._time_value} seconds")

    @property
    def step_value(self):
        return self._step_value

    @step_value.setter
    def step_value(self, step):
        self._step_value = int(step)
        if self.step_selection.get() != self._step_value:
            self.step_selection.set(step)

    # called on RadioButton change
    def stepValueChange(self):
        self.step_value = self.step_selection.get()

    def increaseTimeValue(self):
        self.time_value += 1

    def decreaseTimeValue(self):
        self.time_value -= 1

    def saveButtonAction(self):
        if self.show_time:
            self.bot_event.time_interval = self.time_value
        if self.show_step:
            self.bot_event.speed_step = self.step_value
        self.bot_event.createWidget()
        APP_INST.showMainFrame()

    def cancelButtonAction(self):
        APP_INST.showMainFrame()

class RobotSpeakSettingsFrame(ttk.Frame):
    # properties
    bot_event : BotEvent = None
    event_type: BotEventType = None
    text_input: tk.Text

    # constructor
    # TODO - hande event_type v.s. bot_event
    def __init__(self, bot_event: BotEvent = None, event_type: BotEventType = None):
        super().__init__(APP_INST)
        self.event_type = event_type
        self.text_variable = tk.StringVar()

        self.settings_label = ttk.Label(self)
        self.settings_label.config(text='Event Settings: %s' % self.event_type.value)


        self.prompt_label = ttk.Label(self, text='Input text for the robot to say.')
        self.text_input = tk.Text(self)

        settings_actions_frame = ttk.Frame(self)
        save_button = ttk.Button(settings_actions_frame, text='Save', command=self.saveButtonAction)
        cancel_button = ttk.Button(settings_actions_frame, text='Cancel', command=self.cancelButtonAction)
        save_button.grid(column=0, row=0)
        cancel_button.grid(column=1, row=0)


        self.settings_label.pack()
        self.prompt_label.pack()
        self.text_input.pack()
        settings_actions_frame.pack()
        self.pack()

    def saveButtonAction(self):
        if self.bot_event is None:
            self.bot_event = BotEvent(event_type=self.event_type)
            self.bot_event.speak_text = self.text_input.get('1.0','end')
        self.bot_event.createWidget()
        APP_INST.showMainFrame()

    def cancelButtonAction(self):
        APP_INST.showMainFrame()


class ControlsFrame(ttk.Frame):
    # properties
    head_controls_label_frame: ttk.LabelFrame
    waist_controls_label_frame: ttk.LabelFrame
    wheel_controls_label_frame: ttk.LabelFrame

    head_controls_frame: HeadControlsFrame
    waist_controls_frame: WaistControlsFrame
    wheel_controls_frame: WheelControlsFrame

    mic_image_file = './assets/mic.png'
    mic_image: ImageTk.PhotoImage
    mic_button: ttk.Button

    speaker_image_file = './assets/speaker.png'
    speaker_image: ImageTk.PhotoImage
    speak_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(0, weight=1)

        # init label frames
        self.head_controls_label_frame = ttk.LabelFrame(self, text='Head')
        self.waist_controls_label_frame = ttk.LabelFrame(self, text='Waist')
        self.wheel_controls_label_frame = ttk.LabelFrame(self, text='Wheels')

        self.head_controls_frame = HeadControlsFrame(self.head_controls_label_frame)
        self.waist_controls_frame = WaistControlsFrame(self.waist_controls_label_frame)
        self.wheel_controls_frame = WheelControlsFrame(self.wheel_controls_label_frame)

        self.head_controls_label_frame.grid(column=0, row=0, sticky=tk.EW)
        self.waist_controls_label_frame.grid(column=0, row=1, sticky=tk.EW, pady=10)
        self.wheel_controls_label_frame.grid(column=0, row=2, sticky=tk.EW)

        # TODO - speech2text command
        self.mic_image = fetchTkImage(self.mic_image_file, size=50)
        self.mic_button = ttk.Button(self, text='Speech2Text', image=self.mic_image, compound=tk.BOTTOM)
        self.mic_button.grid(column=0, row=3, sticky=tk.EW, pady=10)


        # TODO - speak command
        self.speaker_image = fetchTkImage(self.speaker_image_file, size=50)
        self.speak_button = ttk.Button(self, text='Speak', image=self.speaker_image, compound=tk.BOTTOM)
        self.speak_button.config(command=lambda : self.showSpeakSettings())
        self.speak_button.grid(column=0, row=4, sticky=tk.EW, pady=10)

        self.pack(side='left', fill='y', padx=10)

    def showSpeakSettings(self):
        global APP_INST
        APP_INST.active_view.pack_forget()
        APP_INST.active_view = RobotSpeakSettingsFrame(event_type=BotEventType.Speak)

"""EventsDisplayFrame
https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01
"""
class EventsFrame(tk.Frame):
    canvas: tk.Canvas
    viewPort: tk.Frame
    vsb: tk.Scrollbar

    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")              # place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                     # place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)     # place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)                              # attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                           # pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                         # pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort") # add view port frame to canvas

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                        # bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                         # bind an event whenever the size of the canvas frame changes.

        self.viewPort.bind('<Enter>', self.onEnter)                                     # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                     # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                     # perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

        self.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.viewPort.columnconfigure(0, weight=1)

        global EVENTS_VIEW_PORT_FRAME
        EVENTS_VIEW_PORT_FRAME = self.viewPort

        renderEvents()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                     # whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)                # whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                      # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )

    def onEnter(self, event):                                                           # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                           # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

class MainFrame(ttk.Frame):
    # properties
    # toolbar_frame: ToolBarFrame
    controls_frame: ControlsFrame
    events_frame: EventsFrame

    # constructor
    def __init__(self, container):
        super().__init__(container)

        # toolbar frame
        self.toolbar_frame = ToolBarFrame(self)
        # controls frame
        self.controls_frame = ControlsFrame(self)
        # events frame
        self.events_frame = EventsFrame(self)

        self.pack(expand=True, fill='both')

class TkinterApp(tk.Tk):
    # properties
    __TITLE                 = 'TangoBot'    # Window Title
    __RESIZEABLE_WIDTH      = True          # Can the width of the window be resized
    __RESIZEABLE_HEIGHT     = True          # Can the height of the window be resized
    style: ttk.Style
    menu_bar: tk.Menu
    main_frame: MainFrame
    active_view: ttk.Frame

    # constructor
    def __init__(self):
        super().__init__()
        # ttk styles
        self.__ttkStyleSetup()
        # window settings
        self.__appWindowSettingsSetup()
        # protocols
        self.__protocolSetup()
        # menu bar
        # self.__menubarSetup()
        self.main_frame = MainFrame(self)
        self.active_view = self.main_frame

    def run(self):
        self.update_idletasks()
        self.update()
        self.mainloop()

    def stop(self, event: tk.Event = None):
        try:
            self.destroy()
        except tk.TclError as err:
            log.error(err)
        global TANGO_BOT
        TANGO_BOT.stop()

    def showMainFrame(self):
        # self.active_view.pack_forget()
        self.active_view.destroy()
        self.main_frame.pack(expand=True, fill='both')
        self.active_view = self.main_frame

    @property
    def screen_width(self):
        return self.winfo_screenwidth()

    @property
    def screen_height(self):
        return self.winfo_screenheight()

    def __ttkStyleSetup(self):
        self.style = ttk.Style(self)
        self.style.configure('.', font=('Helvetica', 12)) # Helvetica
        self.style.configure('EventContainer.TFrame', background='white') # Helvetica
        self.style.configure('EventsDisplay.TFrame', background='white')
        self.style.configure('EventInput.TEntry', font=('Helvetica', 20))

    def __appWindowSettingsSetup(self):
        # title
        self.title(self.__TITLE)
        # window size/position
        self.resizable(self.__RESIZEABLE_WIDTH, self.__RESIZEABLE_HEIGHT)
        # get the screen dimension
        window_width = int(self.screen_width / 4)
        window_height = self.screen_height
        # find the center point
        center_x = 0
        center_y = 0
        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def __protocolSetup(self):
        # make the top right close button
        self.protocol('WM_DELETE_WINDOW', self.stop)

    def __menubarSetup(self):
        self.menu_bar = tk.Menu(self, font=('Helvetica', 12))
        self.config(menu=self.menu_bar)
        # file_menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0, font=('Helvetica', 12))
        # add the File menu to the menubar
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        # add file_menu items
        file_menu.add_command(label='Play', command=runEvents)
        file_menu.add_command(label='Clear', command=cleanEvents)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.stop)

APP_INST: TkinterApp = None
TANGO_BOT: TangBotController = TangBotController()
EVENTS_VIEW_PORT_FRAME = None
EVENTS_DATA: List[BotEvent] = list()
RUN_EVENTS_THREAD: threading.Thread = None

def reRenderEventsDisplay():
    APP_INST.main_frame.events_frame.destroy()
    APP_INST.main_frame.events_frame = EventsFrame(APP_INST.main_frame)
    renderEvents()

def renderEvents():
    for event in EVENTS_DATA:
        if event.widget is not None and isinstance(event.widget, BotEventFrame):
            event.widget.destroy()
        event.createWidget()

def cleanEvents():
    global EVENTS_DATA
    EVENTS_DATA = []
    reRenderEventsDisplay()

def moveEventUp(event: BotEvent):
    row = event.row
    if row < 1: return
    new_index = row - 1
    EVENTS_DATA.remove(event)
    EVENTS_DATA.insert(new_index, event)
    renderEvents()

def moveEventDown(event: BotEvent):
    row = event.row
    if len(EVENTS_DATA) - 1 <= row: return
    new_index = row + 1
    EVENTS_DATA.remove(event)
    EVENTS_DATA.insert(new_index, event)
    renderEvents()

def deleteEvent(event: BotEvent):
    event.widget.destroy()
    EVENTS_DATA.remove(event)
    renderEvents()

def createEventSettingsFrame(bot_event: BotEvent = None, event_type: BotEventType = None, show_time: bool = False, show_step: bool = False):
    global APP_INST
    if bot_event is None and event_type is None:
        log.error('Needs a bot_event or event_type - createEventSettingsFrame')
    elif show_time is False and show_step is False:
        bot_event = BotEvent(event_type=event_type)
        return

def makeEventCreateCallback(event_type: BotEventType):
    global APP_INST
    def fnc(event = None):
        APP_INST.focus()
        event = BotEvent(event_type=event_type)
        event.createWidget()
    return fnc

def makeCreateWheelEventSettingsFrame(event_type: BotEventType):
    bot_event = BotEvent(event_type=event_type)
    show_time = False
    show_step = False
    if event_type is BotEventType.Forward or event_type is BotEventType.Reverse:
        show_time = True
        show_step = True
    if event_type is BotEventType.TurnRight or event_type is BotEventType.TurnLeft:
        show_step = True
    global APP_INST
    APP_INST.active_view.pack_forget()
    APP_INST.active_view = EventSettingsFrame(bot_event=bot_event, show_time=show_time, show_step=show_step)

def runEventsThreadFnc():
    print('Running Events...')
    global EVENTS_DATA
    for event in EVENTS_DATA:
        print(event.type.value)
        event.execute()
        sleep(0.5)
    TANGO_BOT.stop()
    global RUN_EVENTS_THREAD
    RUN_EVENTS_THREAD = None

def runEvents():
    global RUN_EVENTS_THREAD
    if RUN_EVENTS_THREAD is not None:
        print('Already Running...')
        return
    RUN_EVENTS_THREAD = threading.Thread(target=runEventsThreadFnc, daemon=True)
    RUN_EVENTS_THREAD.start()

def stopRobot():
    print('Stop Robot')
    global TANGO_BOT
    TANGO_BOT.stop()

def fetchTkImage(file: str, size: int = 20, rotate: float = None, transpose = None):
    img = Image.open(file)
    width, height = img.size
    img = img.resize((round(size/height*width) , round(size)))
    if rotate is not None:
        img = img.rotate(angle=rotate)
    if transpose is not None:
        img = img.transpose(transpose)
    return ImageTk.PhotoImage(img)

def run_app():
    global APP_INST
    APP_INST = TkinterApp()
    APP_INST.run()

# END
