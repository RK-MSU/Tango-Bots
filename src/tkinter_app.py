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
    details_frame: ttk.Frame
    up_button: ttk.Button
    down_button: ttk.Button
    delete_button: ttk.Button
    edit_button: ttk.Button
    event_number_label: ttk.Label
    event_type_label: ttk.Label
    time_details_label: ttk.Label
    step_level_details_label: ttk.Label
    speak_text_details_label: ttk.Label

    # constructor
    def __init__(self, bot_event):
        super().__init__(EVENTS_VIEW_PORT_FRAME)
        self.bot_event: BotEvent = bot_event

        # Event Number Label
        # ---------------------------------------
        self.event_number_label = ttk.Label(self, anchor=tk.CENTER)

        # Up/Down Button Controls
        # ---------------------------------------
        self.up_button = ttk.Button(self)
        self.down_button = ttk.Button(self)
        self.up_button.config(command=lambda : self.moveBotEventUp())
        self.down_button.config(command=lambda : self.moveBotEventDown())
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
        # if self.bot_event.time_interval is not None:
        self.time_details_label = ttk.Label(self.details_frame)
        self.time_details_label.config(text="Time: %s seconds" % self.bot_event.time_interval)
        self.time_details_label.config(anchor=tk.W)
        # self.time_details_label.pack(expand=True, fill='x')
        # Speed (step) Level Label
        # if self.bot_event.speed_step is not None:
        self.step_level_details_label = ttk.Label(self.details_frame)
        self.step_level_details_label.config(text='Speed Level: %s' % self.bot_event.speed_step)
        self.step_level_details_label.config(anchor=tk.W)
        # self.step_level_details_label.pack(expand=True, fill='x')
        # Robot Speak Text
        # if self.bot_event.speak_text is not None:
        self.speak_text_details_label = ttk.Label(self.details_frame)
        self.speak_text_details_label.config(text="Text: \"%s\"" % self.bot_event.speak_text)
        # self.speak_text_details_label.pack()


        # Event Commands
        # ---------------------------------------
        self.delete_button = ttk.Button(self, text='Delete')
        self.delete_button.config(command=lambda : self.deleteBotEvent())
        self.edit_button = ttk.Button(self, text='edit')
        self.edit_button.config(command=lambda : self.editBotEvent())



        # Add items
        # ---------------------------------------
        self.event_number_label.grid(column=0, row=0, rowspan=2, padx=5, pady=5)
        self.up_button.grid(column=1, row=0)
        self.down_button.grid(column=1, row=1)
        self.details_frame.grid(column=2, row=0, rowspan=2, sticky=tk.NW, padx=5, pady=5)
        self.delete_button.grid(column=3, row=0, sticky=tk.E)
        self.edit_button.grid(column=3, row=1, sticky=tk.E)

        self.columnconfigure(3, weight=1)

        # add self to parent
        # self.grid(column=0, row=self.row, sticky=tk.EW, padx=5, pady=5)

    @property
    def row(self):
        return self.bot_event.row

    @property
    def event_num(self):
        return self.row + 1

    @property
    def event_name(self):
        return self.bot_event.event_type.value

    def render(self):
        self.grid_forget()
        self.time_details_label.pack_forget()
        self.step_level_details_label.pack_forget()
        self.speak_text_details_label.pack_forget()
        self.edit_button.grid_forget()

        self.event_number_label.config(text=self.event_num)

        if self.bot_event.has_time_interval:
            self.time_details_label.config(text="Time: %s seconds" % self.bot_event.time_interval)
            self.time_details_label.pack()
        if self.bot_event.has_speed_step:
            self.step_level_details_label.config(text='Speed Level: %s' % self.bot_event.speed_step)
            self.step_level_details_label.pack()

        if self.bot_event.has_event_settings:
            self.edit_button.grid(column=3, row=1, sticky=tk.E)

        self.grid(column=0, row=self.row, sticky=tk.EW, padx=5, pady=5)

    def deleteBotEvent(self):
        self.grid_forget()
        if self.bot_event in EVENTS_DATA:
            EVENTS_DATA.remove(self.bot_event)
        for event in EVENTS_DATA:
            event.widget.render()
        self.destroy()

    def editBotEvent(self):
        APP_INST.frames['event_settings'].bot_event = self.bot_event
        APP_INST.showFrame('event_settings')

    def moveBotEventUp(self):
        row = self.row
        if row < 1: return
        new_row = row - 1
        EVENTS_DATA.remove(self.bot_event)
        EVENTS_DATA.insert(new_row, self.bot_event)
        for event in EVENTS_DATA: event.widget.render()

    def moveBotEventDown(self):
        row = self.row
        if len(EVENTS_DATA) - 1 <= row: return
        new_row = row + 1
        EVENTS_DATA.remove(self.bot_event)
        EVENTS_DATA.insert(new_row, self.bot_event)
        for event in EVENTS_DATA: event.widget.render()

class BotEvent:
    # properties
    event_type: BotEventType
    __time_interval: int = 1
    __speed_step: int = 1
    speak_text: str = None
    widget: BotEventFrame = None

    # constructor
    def __init__(self, event_type: BotEventType, time_interval: int = None, speed_step: int = None):
        self.event_type = event_type
        self.time_interval = time_interval
        self.speed_step = speed_step
        self.widget = BotEventFrame(bot_event=self)
        # global EVENTS_DATA
        # EVENTS_DATA.append(self)

    @property
    def row(self):
        global EVENTS_DATA
        if self not in EVENTS_DATA:
            return None
        return EVENTS_DATA.index(self)

    @property
    def has_time_interval(self):
        valid_types = [
            BotEventType.Forward,
            BotEventType.Reverse
        ]
        if self.event_type in valid_types:
            return True
        return False

    @property
    def has_speed_step(self):
        valid_types = [
            BotEventType.Forward,
            BotEventType.Reverse,
            BotEventType.TurnLeft,
            BotEventType.TurnRight,
            BotEventType.WaistLeft,
            BotEventType.WaistRight,
            BotEventType.HeadUp,
            BotEventType.HeadDown,
            BotEventType.HeadLeft,
            BotEventType.HeadRight
        ]
        if self.event_type in valid_types:
            return True
        return False

    @property
    def has_event_settings(self):
        if self.has_time_interval or self.has_speed_step:
            return True
        return False

    @property
    def time_interval(self):
        return self.__time_interval

    @time_interval.setter
    def time_interval(self, time):
        if time is not None:
            self.__time_interval = time

    @property
    def speed_step(self):
        return self.__speed_step

    @speed_step.setter
    def speed_step(self, step):
        if step is not None:
            self.__speed_step = step

    def createWidget(self):
        self.widget = BotEventFrame(bot_event=self)

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

class ArrowDirectionControlsFrame(ttk.Frame):
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
        self.__configureCells()
        self.__fetchButtonImages()

        self.up_button = ttk.Button(self, image=self.up_arrow_image, command=lambda : print('Up'))
        self.down_button = ttk.Button(self, image=self.down_arrow_image, command=lambda : print('Down'))
        self.left_button = ttk.Button(self, image=self.left_arrow_image, command=lambda : print('Left'))
        self.right_button = ttk.Button(self, image=self.right_arrow_image, command=lambda : print('Right'))
        self.center_button = ttk.Button(self, image=self.center_image, command=lambda : print('Center'))

        self.up_button.grid(column=1, row=0, sticky=tk.EW)
        self.down_button.grid(column=1, row=2, sticky=tk.EW)
        self.left_button.grid(column=0, row=1, sticky=tk.EW)
        self.right_button.grid(column=2, row=1, sticky=tk.EW)
        self.center_button.grid(column=1, row=1, sticky=tk.EW)

    def __configureCells(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

    def __fetchButtonImages(self):
        self.up_arrow_image = fetchTkImage(self.arrow_image_file)
        self.down_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_180)
        self.left_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_90)
        self.right_arrow_image = fetchTkImage(self.arrow_image_file, transpose=Image.ROTATE_270)
        self.center_image = fetchTkImage(self.center_image_file)

class EventSettingsFrame(ttk.Frame):
    # properties
    __bot_event: BotEvent
    settings_label: ttk.Label
    time_variable: tk.StringVar
    step_selection: tk.StringVar
    _time_value: int
    _step_value: int

    # constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.time_variable = tk.StringVar()
        self.step_selection = tk.StringVar()

        # self.time_value = 1
        # self.step_value = 1
        # TODO - if bot_event.time_interval is not None?

        self.settings_label = ttk.Label(self)
        self.settings_label.config(text='Event Settings')
        self.settings_label.grid(column=0, row=0)

        # time entry
        self.time_input_frame = ttk.Frame(self)
        self.time_entry = tk.Entry(self.time_input_frame)
        self.time_entry.config(textvariable=self.time_variable)
        self.time_entry.config(justify='center')
        self.time_entry.config(font=('Helvetica', 15))
        self.time_entry.config(state='disabled')
        self.time_entry.config(disabledbackground="white")
        self.time_entry.config(disabledforeground="black")
        # time up/down buttons
        self.time_up_button = ttk.Button(self.time_input_frame, text='Up', command=self.increaseTimeValue)
        self.time_down_button = ttk.Button(self.time_input_frame, text='Down', command=self.decreaseTimeValue)
        # add input_frame items
        self.time_entry.grid(column=0, row=0, rowspan=2, sticky=tk.NS)
        self.time_up_button.grid(column=1, row=0)
        self.time_down_button.grid(column=1, row=1)
        # self.time_input_frame.grid(column=0, row=1)


        # step inputs
        self.step_input_frame = ttk.Frame(self)
        speed_one_option = ttk.Radiobutton(self.step_input_frame, text='Level One', value=1, variable=self.step_selection, command=self.stepValueChange)
        speed_two_option = ttk.Radiobutton(self.step_input_frame, text='Level Two', value=2, variable=self.step_selection, command=self.stepValueChange)
        speed_three_option = ttk.Radiobutton(self.step_input_frame, text='Level Three', value=3, variable=self.step_selection, command=self.stepValueChange)
        ttk.Label(self.step_input_frame, text='What level of speed?').pack(anchor='w')
        speed_one_option.pack(anchor='w')
        speed_two_option.pack(anchor='w')
        speed_three_option.pack(anchor='w')
        # self.step_input_frame.grid(column=0, row=2)


        self.settings_actions_frame = ttk.Frame(self)
        save_button = ttk.Button(self.settings_actions_frame, text='Save', command=self.saveButtonAction)
        cancel_button = ttk.Button(self.settings_actions_frame, text='Cancel', command=self.cancelButtonAction)
        save_button.grid(column=0, row=0)
        cancel_button.grid(column=1, row=0)
        self.settings_actions_frame.grid(column=0, row=3)

    @property
    def bot_event(self):
        return self.__bot_event

    @bot_event.setter
    def bot_event(self, bot_event: BotEvent):
        self.__bot_event = bot_event
        if bot_event is None:
            return
        self.settings_label.config(text='Event Settings: %s' % bot_event.event_type.value)
        self.time_value = self.bot_event.time_interval
        self.step_value = self.bot_event.speed_step
        # time intercal entry input
        if bot_event.has_time_interval:
            self.time_input_frame.grid(column=0, row=1)
        else:
            self.time_input_frame.grid_forget()
        # speed step radio buttons
        if bot_event.has_speed_step:
            self.step_input_frame.grid(column=0, row=2)
        else:
            self.step_input_frame.grid_forget()

    @property
    def time_value(self):
        return self.bot_event.time_interval

    @time_value.setter
    def time_value(self, time: int):
        if time < 1: time = 1
        # self._time_value = time
        self.bot_event.time_interval = int(time)
        self.time_variable.set(f"{self.time_value} seconds")

    @property
    def step_value(self):
        return self.bot_event.speed_step

    @step_value.setter
    def step_value(self, step: int):
        self.bot_event.speed_step = int(step)
        if str(self.step_selection.get()) != str(self.step_value):
            self.step_selection.set(int(step))

    # called on RadioButton change
    def stepValueChange(self):
        self.step_value = self.step_selection.get()

    def increaseTimeValue(self):
        self.time_value += 1

    def decreaseTimeValue(self):
        self.time_value -= 1

    def saveButtonAction(self):
        # if self.show_time:
        #     self.bot_event.time_interval = self.time_value
        # if self.show_step:
        #     self.bot_event.speed_step = self.step_value
        # self.bot_event.createWidget()
        # print(self.bot_event.time_interval, self.bot_event.speed_step)
        if self.bot_event not in EVENTS_DATA:
            EVENTS_DATA.append(self.bot_event)
        self.bot_event.widget.render()

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

class EventControlsSettingsFrame(ttk.Frame):

    title_label: ttk.Label
    # event_options_frame: ttk.Frame
    action_buttons_frame: ttk.Frame
    save_button: ttk.Button
    cancel_button: ttk.Button

    # constructor
    def __init__(self, container):
        super().__init__(container)

        self.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(self, font=('Helvetica', 15))

        self.action_buttons_frame = ttk.Frame(self)

        self.save_button = ttk.Button(self.action_buttons_frame, text='Save')
        self.cancel_button = ttk.Button(self.action_buttons_frame, text='Cancel')
        self.cancel_button.config(command=lambda : APP_INST.showFrame('main'))
        self.save_button.grid(column=0, row=0)
        self.cancel_button.grid(column=1, row=0)

        self.title_label.grid(column=0, row=0, pady=10)
        self.action_buttons_frame.grid(column=0, row=2, pady=10)

    def newBotEventSettings(self, bot_event_type: BotEventType):
        bot_event = BotEvent(event_type=bot_event_type)
        if bot_event.has_event_settings:
            APP_INST.frames['event_settings'].bot_event = bot_event
            APP_INST.showFrame('event_settings')
        else:
            if bot_event not in EVENTS_DATA:
                EVENTS_DATA.append(bot_event)
            bot_event.widget.render()
            APP_INST.showFrame('main')

class HeadEventSettingsFrame(EventControlsSettingsFrame):
     # constructor
    def __init__(self, container):
        super().__init__(container)
        self.title_label.config(text='Head Event')

        self.action_buttons_frame = ArrowDirectionControlsFrame(self)
        self.action_buttons_frame.grid(column=0, row=1)

        self.action_buttons_frame.up_button.config(command=lambda : self.newBotEventSettings(BotEventType.HeadUp))
        self.action_buttons_frame.down_button.config(command=lambda : self.newBotEventSettings(BotEventType.HeadDown))
        self.action_buttons_frame.left_button.config(command=lambda : self.newBotEventSettings(BotEventType.HeadLeft))
        self.action_buttons_frame.right_button.config(command=lambda : self.newBotEventSettings(BotEventType.HeadRight))
        self.action_buttons_frame.center_button.config(command=lambda : self.newBotEventSettings(BotEventType.HeadCenter))

class WaistEventSettingsFrame(EventControlsSettingsFrame):
     # constructor
    def __init__(self, container):
        super().__init__(container)
        self.title_label.config(text='Waist Event')

        self.action_buttons_frame = ArrowDirectionControlsFrame(self)
        self.action_buttons_frame.grid(column=0, row=1)

        self.action_buttons_frame.up_button.grid_forget()
        self.action_buttons_frame.down_button.grid_forget()

        self.action_buttons_frame.left_button.config(command=lambda : self.newBotEventSettings(BotEventType.WaistLeft))
        self.action_buttons_frame.right_button.config(command=lambda : self.newBotEventSettings(BotEventType.WaistRight))
        self.action_buttons_frame.center_button.config(command=lambda : self.newBotEventSettings(BotEventType.WaistCenter))

class WheelEventSettingsFrame(EventControlsSettingsFrame):
    # properties
    stop_image: ImageTk.PhotoImage

     # constructor
    def __init__(self, container):
        super().__init__(container)

        self.title_label.config(text='Wheel/Motor Event')

        self.action_buttons_frame = ArrowDirectionControlsFrame(self)
        self.action_buttons_frame.grid(column=0, row=1)

        self.stop_image = fetchTkImage('./assets/stop.png')
        self.action_buttons_frame.center_button.config(command=lambda : print('Stop'))
        self.action_buttons_frame.center_button.config(image=self.stop_image)

        self.action_buttons_frame.up_button.config(command=lambda : self.newBotEventSettings(BotEventType.Forward))
        self.action_buttons_frame.down_button.config(command=lambda : self.newBotEventSettings(BotEventType.Reverse))
        self.action_buttons_frame.left_button.config(command=lambda : self.newBotEventSettings(BotEventType.TurnLeft))
        self.action_buttons_frame.right_button.config(command=lambda : self.newBotEventSettings(BotEventType.TurnRight))
        self.action_buttons_frame.center_button.config(command=lambda : self.newBotEventSettings(BotEventType.Stop))

class SpeakEventSettingsFrame(EventControlsSettingsFrame):
     # constructor
    def __init__(self, container):
        super().__init__(container)
        self.title_label.config(text='Speak Event')

        self.action_buttons_frame = ttk.Frame(self)
        self.action_buttons_frame.grid(column=0, row=1)

        ttk.Label(self.action_buttons_frame, text='Input what you want the robot to say').pack()

        self.text = tk.Text(self.action_buttons_frame, height=5)
        self.text.pack()

class MainFrame(ttk.Frame):
    # toolbar properties
    # -------------------------------------------
    toolbar_frame: ttk.Frame
    play_image: ImageTk.PhotoImage
    head_image: ImageTk.PhotoImage
    waist_image: ImageTk.PhotoImage
    wheels_image: ImageTk.PhotoImage
    speaker_image: ImageTk.PhotoImage
    mic_image: ImageTk.PhotoImage
    clear_image: ImageTk.PhotoImage
    play_button: ttk.Button
    head_button: ttk.Button
    waist_button: ttk.Button
    wheels_button: ttk.Button
    speak_button: ttk.Button
    speech2text_button: ttk.Button
    clear_button: ttk.Button
    # events display properties
    # -------------------------------------------
    events_display: ttk.Frame
    canvas: tk.Canvas
    viewPort: tk.Frame
    vsb: tk.Scrollbar

    # constructor
    def __init__(self, container):
        super().__init__(container)

        # toolbar frame
        self.__buildToolbar()
        # events display frame
        self.__buildEventsDisplay()

        # self.toolbar_frame = ToolBarFrame(self)
        # controls frame
        # self.controls_frame = ControlsFrame(self)
        # events frame
        # self.events_frame = EventsFrame(self)

        # self.pack(expand=True, fill='both')

    def __buildToolbar(self):
        self.toolbar_frame = ttk.Frame(self)

        # images
        self.play_image = fetchTkImage('./assets/play.png', size=20)
        self.head_image = fetchTkImage('./assets/head.png', size=20)
        self.waist_image = fetchTkImage('./assets/waist.png', size=20)
        self.wheels_image = fetchTkImage('./assets/wheel.png', size=20)
        self.speaker_image = fetchTkImage('./assets/megaphone.png', size=20)
        self.mic_image = fetchTkImage('./assets/mic.png', size=20)
        self.clear_image = fetchTkImage('./assets/clear.png', size=20)

        # buttons
        self.play_button = ttk.Button(self.toolbar_frame, image=self.play_image)
        self.head_button = ttk.Button(self.toolbar_frame, image=self.head_image)
        self.waist_button = ttk.Button(self.toolbar_frame, image=self.waist_image)
        self.wheels_button = ttk.Button(self.toolbar_frame, image=self.wheels_image)
        self.speak_button = ttk.Button(self.toolbar_frame, image=self.speaker_image)
        self.speech2text_button = ttk.Button(self.toolbar_frame, image=self.mic_image)
        self.clear_button = ttk.Button(self.toolbar_frame, image=self.clear_image)
        # button commands
        self.head_button.config(command=lambda : APP_INST.showFrame('new_head_event'))
        self.waist_button.config(command=lambda : APP_INST.showFrame('new_waist_event'))
        self.wheels_button.config(command=lambda : APP_INST.showFrame('new_wheel_event'))
        self.speak_button.config(command=lambda : APP_INST.showFrame('new_speak_event'))
        # TODO - implement Speech2Text
        self.speech2text_button.config(command=lambda : print('Speech2Text'))
        # TODO - implement clear
        self.clear_button.config(command=lambda : print('Clear'))


        # pack buttons
        self.play_button.pack()
        ttk.Separator(self.toolbar_frame, orient='horizontal').pack(fill='x', pady=10)
        self.head_button.pack()
        self.waist_button.pack()
        self.wheels_button.pack()
        self.speak_button.pack()
        self.speech2text_button.pack()
        ttk.Separator(self.toolbar_frame, orient='horizontal').pack(fill='x', pady=10)
        self.clear_button.pack()

        # pack toolbar_frame
        self.toolbar_frame.pack(side='left', fill='y', padx=5, pady=5)

    def __buildEventsDisplay(self):
        self.events_display = ttk.Frame(self)

        self.canvas = tk.Canvas(self.events_display, borderwidth=0, background="#ffffff")              # place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                     # place a frame on the canvas, this frame will hold the child widgets
        self.vsb = tk.Scrollbar(self.events_display, orient="vertical", command=self.canvas.yview)     # place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)                              # attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                           # pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                         # pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort") # add view port frame to canvas

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                        # bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                         # bind an event whenever the size of the canvas frame changes.

        self.viewPort.bind('<Enter>', self.onEnter)                                     # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                     # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                     # perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

        self.viewPort.columnconfigure(0, weight=1)

        global EVENTS_VIEW_PORT_FRAME
        EVENTS_VIEW_PORT_FRAME = self.viewPort

        for event in EVENTS_DATA: event.widget.render()

        self.events_display.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

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

    def showNewEventFrame(self, bot_event_type: BotEventType):
        global APP_INST
        APP_INST.showFrame('new_event')

class TkinterApp(tk.Tk):
    # properties
    __TITLE                 = 'TangoBot'    # Window Title
    __RESIZEABLE_WIDTH      = True          # Can the width of the window be resized
    __RESIZEABLE_HEIGHT     = True          # Can the height of the window be resized
    style: ttk.Style
    active_frame: ttk.Frame

    frames: dict

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
        self.frames = dict()
        self.frames['main'] = MainFrame(self)
        self.frames['new_head_event'] = HeadEventSettingsFrame(self)
        self.frames['new_waist_event'] = WaistEventSettingsFrame(self)
        self.frames['new_wheel_event'] = WheelEventSettingsFrame(self)
        self.frames['new_speak_event'] = SpeakEventSettingsFrame(self)
        # TODO - implement Speech2Text event settings frame
        self.frames['event_settings'] = EventSettingsFrame(self)
        self.active_frame = self.frames['main']
        self.packActiveFrame()

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
        self.showFrame('main')

    def packActiveFrame(self):
        self.active_frame.pack(expand=True, fill='both')

    def showFrame(self, name):
        self.active_frame.pack_forget()
        self.active_frame = self.frames[name]
        self.packActiveFrame()

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
        window_height = int(self.screen_height / 2)
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
        # file_menu.add_command(label='Clear', command=cleanEvents)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.stop)

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

APP_INST: TkinterApp = None
TANGO_BOT: TangBotController = TangBotController()
EVENTS_VIEW_PORT_FRAME = None
EVENTS_DATA: List[BotEvent] = list()
RUN_EVENTS_THREAD: threading.Thread = None

def run_app():
    global APP_INST
    APP_INST = TkinterApp()
    APP_INST.run()

# END
