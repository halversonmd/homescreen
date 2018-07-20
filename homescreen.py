# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow

from tkinter import *
from tkinter import font
import locale, threading, time, requests, json, traceback, feedparser
from datetime import datetime as dt
import datetime
from pytz import timezone
from PIL import Image, ImageTk
from contextlib import contextmanager
from utils import trains, uber, mta, config

LOCALE_LOCK = threading.Lock()

tz = timezone('US/Eastern')
ui_locale = ''
time_format = 12 
date_format = "%b %d, %Y" 
news_country_code = 'us'
weather_api_token = config["DARKSKY_KEY"]
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast
weather_unit = 'us' 
latitude = None 
longitude = None 
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 34
small_text_size = 18
font_color = 'white'
ui_font = 'Didot'
background_color = 'black'

@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png",  # hail
    'q_train': 'assets/Q.png',
    '6_train': 'assets/6.png'
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg=background_color)
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=(ui_font, large_text_size), fg=font_color, bg=background_color)
        self.timeLbl.pack(side=TOP, anchor=W)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=(ui_font, medium_text_size), fg=font_color, bg=background_color)
        self.dayOWLbl.pack(side=TOP, anchor=W)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=(ui_font, medium_text_size), fg=font_color, bg=background_color)
        self.dateLbl.pack(side=TOP, anchor=W)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = dt.now(tz).strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = dt.now(tz).strftime('%H:%M') #hour in 24h format

            day_of_week2 = dt.now(tz).strftime('%A')
            date2 = dt.now(tz).strftime(date_format)
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            self.timeLbl.after(200, self.tick)

class Commute(Frame):
    def __init__(self, parent, *args, **kwargs):

        Frame.__init__(self, parent, bg=background_color)
        # self.trains = trains
        # self.cmt_times = self.trains()

        self.cmtLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, text='Commute:')
        self.cmtLbl.pack(side=TOP, anchor=W)

        self.mikeVar = StringVar()
        self.mikecmtLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, textvariable=self.mikeVar)
        self.mikecmtLbl.pack(side=TOP, anchor=W)

        self.anneVar = StringVar()
        self.annecmtLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, textvariable=self.anneVar)
        self.annecmtLbl.pack(side=TOP, anchor=W)

        self.update()

    def update(self):
        
        cmt_times = trains()
        self.mikeVar.set('Husband, {} minutes'.format(cmt_times['mike']))
        self.anneVar.set('Wife, {} minutes'.format(cmt_times['anne']))
        self.cmtLbl.after(60000, self.update)


class Uber(Frame):
    def __init__(self, parent, name, root, *args, **kwargs):

        Frame.__init__(self, parent, bg=background_color)
        self.name = name

        if self.name == 'anne':
            title = 'Wife'
        else:
            title = 'Husband'

        self.uberLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, text='{} Uber:'.format(title))
        self.uberLbl.pack(side=TOP, anchor=W)

        self.estVar = StringVar()
        self.estLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, textvariable=self.estVar)
        self.estLbl.pack(side=TOP, anchor=W)

        self.durVar = StringVar()
        self.durLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, textvariable=self.durVar)
        self.durLbl.pack(side=TOP, anchor=W)

        self.waitVar = StringVar()
        self.waitLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color, textvariable=self.waitVar)
        self.waitLbl.pack(side=TOP, anchor=W)

        self.update()

    def update(self):
        uber_data = uber()
        self.estVar.set('{}'.format(uber_data[self.name]['estimate']))
        self.durVar.set('{} min ride'.format(uber_data[self.name]['duration']))
        self.waitVar.set('{} min wait'.format(uber_data[self.name]['wait_time']))
        self.uberLbl.after(60000, self.update)


class MTA(Frame):
    def __init__(self, parent, name, root, *args, **kwargs):
        Frame.__init__(self, parent, bg=background_color)
        self.name = name

        if self.name == 'anne':
            train = '6_train'
            anchor = W
        else:
            train = 'q_train'
            anchor = W

        self.trainLbl = Label(self, bg=background_color)
        self.trainLbl.pack(side=TOP, anchor=anchor)
        self.Lb1 = Listbox(self, borderwidth=0, highlightthickness=0, background=background_color, fg=font_color, font=(ui_font, 22))
        self.Lb1.pack(padx=1, pady=1)
        self.Lb1.config(width=8)
        image = Image.open(icon_lookup[train])
        image = image.resize((100, 100))
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.trainLbl.config(image=photo)
        self.trainLbl.image = photo

        self.update()

    def update(self):

        self.Lb1.delete(0, END)
        now = dt.now()
        mta_data = mta()
        for idx, train_time in enumerate(mta_data[self.name]):
            if now < train_time:
                self.Lb1.insert(idx, '{} min'.format((train_time-now).seconds // 60))
            if idx == 4:
                break
        self.Lb1.after(60000, self.update)



class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg=background_color)
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg=background_color)
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=(ui_font, xlarge_text_size), fg=font_color, bg=background_color)
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg=background_color)
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=(ui_font, medium_text_size), fg=font_color, bg=background_color)
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=(ui_font, small_text_size), fg=font_color, bg=background_color, wraplength=400, justify=LEFT)
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=(ui_font, small_text_size), fg=font_color, bg=background_color)
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:

            if latitude is None and longitude is None:
                # get location
                location_req_url = "https://json.geoiplookup.io/{}".format(self.get_ip())
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)
                # print(json.dumps(location_obj, indent=2))

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)
            # print(json.dumps(weather_obj, indent=2))

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print("Error: %s. Cannot get weather." % e)

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32


class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=(ui_font, small_text_size), fg=font_color, bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLbl = Label(self, text=self.title, font=(ui_font, medium_text_size), fg=font_color, bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.get_events()

    def get_events(self):
        #TODO: implement this method
        # reference https://developers.google.com/google-apps/calendar/quickstart/python

        # remove all children
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        calendar_event = CalendarEvent(self.calendarEventContainer)
        calendar_event.pack(side=TOP, anchor=E)
        pass


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=(ui_font, small_text_size), fg=font_color, bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)


class FullscreenWindow:

    def __init__(self):

        self.tk = Tk()
        self.tk.configure(background=background_color)
        self.topFrame = Frame(self.tk, background = background_color)
        self.bottomFrame = Frame(self.tk, background = background_color)
        self.leftFrame = Frame(self.tk, background = background_color)
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.leftFrame.pack(side = LEFT, fill=BOTH, expand = YES)
        self.state = True
        self.tk.bind("<Return>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)


        # clock
        self.clock = Clock(self.topFrame)
        self.clock.pack(side=LEFT, anchor=N, padx=100, pady=60)
        # weather
        self.weather = Weather(self.bottomFrame)
        self.weather.pack(side=LEFT, anchor=S, padx=100, pady=(0,150))

        #commutes
        self.commutes = Commute(self.topFrame)
        self.commutes.pack(side=RIGHT, anchor=S, padx=100, pady=60, fill=Y)

        #ubers
        self.mike_uber = Uber(self.bottomFrame, 'mike', self.tk)
        self.mike_uber.pack(side = RIGHT, anchor=S, padx=100, pady=60)

        self.anne_uber = Uber(self.bottomFrame, 'anne', self.tk)
        self.anne_uber.pack(side = RIGHT, anchor=S, padx=100, pady=60)

        #trains
        self.mike_mta = MTA(self.topFrame, 'mike', self.tk)
        self.mike_mta.pack(side = RIGHT, anchor=S, padx=100, pady=60)

        self.anne_mta = MTA(self.topFrame, 'anne', self.tk)
        self.anne_mta.pack(side = RIGHT, anchor=S, padx=100, pady=60)
        self.tk.attributes("-fullscreen", True)


    def toggle_fullscreen(self, event=None):
        self.state = not self.state  
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()



