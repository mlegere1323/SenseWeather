"""
    Weather Sense for Raspberry Pi Sense Hat

Author: MLegere1323 [https://github.com/mlegere1323]
Date 1/15/2017
Version 1.0

This is a program used to display live, or near-live relevant
weather information using pyowm, the Raspberry Pi Sense Hat,
the Raspberry Pi, and an internet connection.

Information is requested via pyowm as to the current conditions of weather
based on a given city id that pyowm uses. Information returned contains
a 3-hour forcast (estimates in 3-hour time intervals), and a daily forecast--
where you can specify how many days forward you'd like to have information on.
Also included are current forecasted conditions.

The information received on the weather conditions is output to the Sense Hat's
led matrix as a visual, simplistic and colorful design where one can
interpret the forecast, and current conditions from color and pixel orientation/
location.

Information from the current environment, as measured by the on board sensors
in the Sense Hat, can also be displayed from this program, as well as text
outputs of relevant forecasting information.

When using this to make weather predictions, keep in mind that the given forecast
is what is *most likely* to occur given a set of parameters. So, if it says that
for the next two consecutive 3-hour intervals that the weather will be producing
"light rain", well, have a look outside, have a look at the doppler radar, and
in conjunction with this program, make a well rounded prediciton; "light rain"
could just be indicative of a specific atmospheric pattern that generally produces
rain, not necessarily a guarantee of a little rain, or passing spotty rain.

If you want to learn more about the science of forecasting, [http://www.weather.gov/]
is a great place to start!


To make understanding the code easier, start by reading:

         [https://github.com/csparpa/pyowm]

"""

VERSION = "1.0.0"

#----------------------------------------------------------------#
#--------------------------[ IMPORTS ]---------------------------#
#----------------------------------------------------------------#
# Docs for pyowm...
# [http://pyowm.readthedocs.io/en/latest/pyowm.html]
from pyowm import OWM
from pyowm import timeutils
import datetime, time
from pytz import timezone
import time
import numpy as np
from time import sleep
from sense_emu import SenseHat as SenseHatEmu #Emus are funny-looking birds
from sense_hat import SenseHat

#----------------------------------------------------------------#
#------------------[ CONSTANTS & GLOBALS ]-----------------------#
#----------------------------------------------------------------#
#Sense Hat
hat = SenseHat()#change to SenseHatEmu() to run this on emulator

#Current x position for cursor in main menu view
curr_x = 8 

#Current sub program running is based on the state
# 0 is startup
# 1 is outdoor HUD
# 2 is indoor HUD
# 3 is 3 Hour forecast
# 4 is 8 day forecast
program_state = 0

# Per the pyowm github page:

# As the OpenWeatherMap API needs a valid API key to allow
# responses, PyOWM won't work if you don't provide one.
# This stands for both the free and paid (pro) subscription plans.

# You can signup for a free API key on the OWM website

# Please notice that the free API subscription plan is subject
# to requests throttling. FMI: [http://openweathermap.org/appid]
API_KEY = 'b328f92fcf333d818dbb1bc22478357f' #Get your own key here ^

#The city ID for SomeCity, US:
"""
To get city id, go to [http://openweathermap.org/find?q=]
and search for your city, and then navigate to its respective
page. The last part of the url will be your ID.

Ex. for London, GB: [http://openweathermap.org/city/2643743]
So, id would be "2643743"
"""
#Uncomment and replace with your city id -- TODO
SomeCity = 4975802

#Will be overwritten with each request for a weather observation
latest_obs_time = datetime.datetime.utcnow()

#------------- COLORS USED FOR LED MATRIX ------------------#
# A bit superfluous with the naming, but it made reading
#  the code easier for me

#General colors
red=[200,0,0]
orange=[200,145,0]
yellow=[200,200,0]
green=[0,200,0]
blue=[0,0,200]
violet=[75,0,130]
pink=[238,0,238]
nwhite=[205,190,80]
black=[0,0,0]
grey = [50,50,50]
white = [200,200,200]
#Forecast color groups
thunder = [102,102,0]
drizzle = [0,204,204]
rain = blue
snow = white
atmos = [70,50,100]
danger = red
clear = yellow
clouds = grey
wind = [204,153,255]
#Below 30 degrees F, temp pixel will be white
freezing = white
# Temperature colors (so you know generally
#  how hot/cold it is instantly, visually
very_cold = pink
cold = [70,130,174] #cyan/light blue
almost_ok = [0,200,150] #turquoise/blue-green
ok = green
hot = red
#Humidity indication colors
humi_low = cold
humi_ok = green
humi_hi = red
#Atmospheric pressure indicator colors
pres_low = humi_low
pres_ok = humi_ok
pres_hi = humi_hi

#--------------- MAIN MENU GRAPHICS ---------------------#

#The main menu bar (top row of led matrix, left to right)
color_indices = {0:white,
                 1:red,
                 2:orange,
                 3:yellow,
                 4:green,
                 5:blue,
                 6:violet,
                 7:pink}

#Main menu screen (Can change menu bar colors here, or background color)
bg = black #The background color of the main view
screen_main = [
    white, red,   orange, yellow, green, blue,   violet, pink,   
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg
    ]

#Welcome screen, shown only on startup
bg = blue #The background color of the welcome view
cl = white #Clouds
sn = yellow #Sun
so = orange #Sun orange
ld = green #Land
screen_welc = [
    white, red,   orange, yellow, green, blue,   violet, pink,   
    sn,    so,    bg,     bg,     bg,    bg,     cl,     cl,
    so,    so,    bg,     bg,     bg,    bg,     bg,     bg,
    bg,    bg,    bg,     bg,     cl,    cl,     bg,     bg,
    bg,    cl,    cl,     bg,     bg,    bg,     cl,     cl,
    bg,    bg,    bg,     bg,     bg,    bg,     bg,     bg,
    ld,    ld,    ld,     ld,     ld,    ld,     ld,     ld,
    ld,    ld,    ld,     ld,     ld,    ld,     ld,     ld
    ]

#Dictionary for Weather Condition Codes & colors
#KEY: a 3 digit weather code
#VALUE: A 2-dimensional array defined as:
#       [some rgb color, some short description as a string]
#       such that these elements relate to the weather code KEY
#
#  FMI about codes: [http://openweathermap.org/weather-conditions]
W_CODES = {
        #Thunderstorm group
        200:[thunder, "Tstorm w/ light rain"],
        201:[thunder,"Tstorm w/ rain"],
        202:[thunder,"Tstorm w/ heavy rain"],
        210:[thunder,"Light tstorm"],
        211:[thunder,"Thunderstorm"],
        212:[thunder,"Heavy tstorm"],
        221:[thunder,"Ragged tstorm"],
        230:[thunder,"Tstorm w/ light drizzle"],
        231:[thunder,"Tstrom w/ drizzle"],
        232:[thunder,"Tstorm w/ heavy drizzle"],
        #Drizzle group
        300:[drizzle,"Light intensity drizzle"],
        301:[drizzle,"Drizzle"],
        302:[drizzle,"Heavy intensity drizzle"],
        310:[drizzle,"Light intensity drizzle rain"],
        311:[drizzle,"Drizzle rain"],
        312:[drizzle,"Heavy intensity drizzle rain"],
        313:[drizzle,"Shower rain & drizzle"],
        314:[drizzle,"Heavy shower rain & drizzle"],
        321:[drizzle,"Shower drizzle"],
        #Rain group
        500:[rain,"Light rain"],
        501:[rain,"Moderate rain"],
        502:[rain,"Heavy intensity rain"],
        503:[rain,"Very heavy rain"],
        504:[rain,"Extreme rain"],
        511:[rain,"Freezing rain"],
        520:[rain,"Light intensity shower rain"],
        521:[rain,"Shower rain"],
        522:[rain,"Heavy intensity shower rain"],
        531:[rain,"Ragged shower rain"],
        #Snow group
        600:[snow,"Light snow"],
        601:[snow,"Snow"],
        602:[snow,"Heavy snow"],
        611:[snow,"Sleet"],
        612:[snow,"Shower sleet"],
        615:[snow,"Light rain & snow"],
        616:[snow,"Rain & snow"],
        620:[snow,"Light shower snow"],
        621:[snow,"Shower snow"],
        622:[snow,"Heavy shower snow"],
        #Atmosphere group
        701:[drizzle,"Mist"],
        711:[atmos,"Smoke"],
        721:[atmos,"Haze"],
        731:[atmos,"Sand & dust whirls"],
        741:[atmos,"Fog"],
        751:[atmos,"Sand"],
        761:[atmos,"Dust"],
        762:[atmos,"Volcanic ash"],
        771:[thunder,"Squalls"],
        781:[danger,"Tornado"],
        #Clear Sky
        800:[clear,"Clear sky"],
        #Clouds group
        801:[clouds,"Few clouds"],
        802:[clouds,"Scattered clouds"],
        803:[clouds,"Broken clouds"],
        804:[clouds,"Overcast clouds"],
        #Extreme weather group
        900:[danger,"Tornado"],
        901:[danger,"Tropical storm"],
        902:[danger,"Hurricane"],
        903:[danger,"Extreme cold"],
        904:[danger,"Extreme heat"],
        905:[danger,"Excessive wind"],
        906:[danger,"Hail"],
        #Add'l
        951:[clear,"Calm"],
        952:[wind,"Light breeze"],
        953:[wind,"Gentle breeze"],
        954:[wind,"Moderate breeze"],
        955:[wind,"Fresh breeze"],
        956:[wind,"Strong breeze"],
        957:[wind,"High wind"],
        958:[wind,"Gale-force wind"],
        959:[danger,"Severe gale-force wind"],
        960:[thunder,"Storm"],
        961:[danger,"Violent storm"],
        962:[danger,"Hurricane"]
    }
#----------------------------------------------------------------#
#--------------------------[ FUNCTIONS ]-------------------------#
#----------------------------------------------------------------#

    
#-----------------------MINI MENU IMAGES-----------------------#

# It was a creative choice to set individual pixels; that and for
#  explicit clarity so that others can understand what I did.

def show_outdoor_hud_image(hat):
    """Shows the mini image for the outdoor HUD display
        when navigating the main menu"""
    letter_color = color_indices[curr_x]
    #The letter "O" located in the top left corner
    hat.set_pixel(0,1,letter_color)
    hat.set_pixel(1,1,letter_color)
    hat.set_pixel(2,1,letter_color)
    hat.set_pixel(0,2,letter_color)
    hat.set_pixel(2,2,letter_color)
    hat.set_pixel(0,3,letter_color)
    hat.set_pixel(2,3,letter_color)
    hat.set_pixel(0,4,letter_color)
    hat.set_pixel(1,4,letter_color)
    hat.set_pixel(2,4,letter_color)
    #The letter "H" located in the bottom right corner
    hat.set_pixel(4,4,letter_color)
    hat.set_pixel(6,4,letter_color)
    hat.set_pixel(4,5,letter_color)
    hat.set_pixel(6,5,letter_color)
    hat.set_pixel(4,6,letter_color)
    hat.set_pixel(5,6,letter_color)
    hat.set_pixel(6,6,letter_color)
    hat.set_pixel(4,7,letter_color)
    hat.set_pixel(6,7,letter_color)


def show_indoor_hud_image(hat):
    """Shows the mini image for the indoor HUD display
        when navigating the main menu"""
    letter_color = color_indices[curr_x]    
    #The letter "I" located in the top left corner
    hat.set_pixel(0,1,letter_color)
    hat.set_pixel(1,1,letter_color)
    hat.set_pixel(2,1,letter_color)  
    hat.set_pixel(1,2,letter_color)
    hat.set_pixel(1,3,letter_color)
    hat.set_pixel(0,4,letter_color)
    hat.set_pixel(1,4,letter_color)
    hat.set_pixel(2,4,letter_color)
    #The letter "H" located in the bottom right corner
    hat.set_pixel(4,4,letter_color)
    hat.set_pixel(6,4,letter_color)
    hat.set_pixel(4,5,letter_color)
    hat.set_pixel(6,5,letter_color)
    hat.set_pixel(4,6,letter_color)
    hat.set_pixel(5,6,letter_color)
    hat.set_pixel(6,6,letter_color)
    hat.set_pixel(4,7,letter_color)
    hat.set_pixel(6,7,letter_color)

def show_3h_readout_image(hat):
    """Shows the mini image for the 3-hour forecast readout
       when navigating the main menu"""
    letter_color = color_indices[curr_x]
    #The number "3" in the top left corner of the screen
    hat.set_pixel(0,1,letter_color)
    hat.set_pixel(1,1,letter_color)
    hat.set_pixel(2,1,letter_color)
    hat.set_pixel(2,2,letter_color)
    hat.set_pixel(0,3,letter_color)
    hat.set_pixel(1,3,letter_color)
    hat.set_pixel(2,3,letter_color)
    hat.set_pixel(2,4,letter_color)
    hat.set_pixel(0,5,letter_color)
    hat.set_pixel(1,5,letter_color)
    hat.set_pixel(2,5,letter_color)
    #The letter "H" located in the bottom right corner
    hat.set_pixel(4,4,letter_color)
    hat.set_pixel(6,4,letter_color)
    hat.set_pixel(4,5,letter_color)
    hat.set_pixel(6,5,letter_color)
    hat.set_pixel(4,6,letter_color)
    hat.set_pixel(5,6,letter_color)
    hat.set_pixel(6,6,letter_color)
    hat.set_pixel(4,7,letter_color)
    hat.set_pixel(6,7,letter_color)

def show_8d_readout_image(hat):
    """Shows the mini image for the 8-day forecast readout
       when navigating the main menu"""
    letter_color = color_indices[curr_x]
    #The number "3" in the top left corner of the screen
    hat.set_pixel(0,1,letter_color)
    hat.set_pixel(1,1,letter_color)
    hat.set_pixel(2,1,letter_color)
    hat.set_pixel(0,2,letter_color)
    hat.set_pixel(2,2,letter_color)
    hat.set_pixel(0,3,letter_color)
    hat.set_pixel(1,3,letter_color)
    hat.set_pixel(2,3,letter_color)
    hat.set_pixel(0,4,letter_color)
    hat.set_pixel(2,4,letter_color)
    hat.set_pixel(0,5,letter_color)
    hat.set_pixel(1,5,letter_color)
    hat.set_pixel(2,5,letter_color)
    #The letter "H" located in the bottom right corner
    hat.set_pixel(4,4,letter_color)
    hat.set_pixel(5,4,letter_color)
    hat.set_pixel(4,5,letter_color)
    hat.set_pixel(6,5,letter_color)
    hat.set_pixel(4,6,letter_color)
    hat.set_pixel(5,7,letter_color)
    hat.set_pixel(6,6,letter_color)
    hat.set_pixel(4,7,letter_color)

#------------ MISC FUNCTIONS ---------------#

def get_observation(city_id, owm):
    """Get the latest observation weather data via city_id"""
    global latest_obs_time

    #Get latest observation
    obs = owm.weather_at_id(city_id)

    #Get the weather object
    w = obs.get_weather()

    #Set retrieval times
    latest_obs_time = w.get_reference_time(timeformat='date')
    #I changed the timezone to fit my own,s ince it's given as utc
    latest_obs_time = utc_to_eastern(latest_obs_time)
    
    return w

def utc_to_eastern(utc_datetime):
    """Change a UTC timezone to US/Eastern Time"""
    return utc_datetime.astimezone(timezone('US/Eastern'))               

def show_main_screen(hat):
    """Shows the main screen view"""
    global screen_main
    hat.clear()
    hat.set_pixels(screen_main)

def return_to_main_menu(hat, curr_x):
    """Takes appropriate steps to return to the main menu view"""
    display_option(curr_x,hat,color_indices)
    hat.set_pixel(curr_x,0,grey)#Reset the cursor pixel
    
def clamp(value, min_value=0, max_value=7):
    """Restrain and bound values"""
    if value == -1:
        value = 7
    if value == 8:
        value = 0
    return min(max_value, max(min_value, value))
              
def check_stick_events(hat, curr_x):
    """For reacting to stick events during main menu
       view navigation"""
    global program_state
    for event in hat.stick.get_events():
        #print(event)#FOR DEBUGGING STICK EVENTS
        if(event.action == "pressed"):
            if(event.direction == "left" or event.direction == "right"):
                move_cursor(event)
            elif(event.direction == "middle"):
                if(curr_x == 0):#If the first program loop is selected
                    program_state = 1 #Running outdoor hud
                elif(curr_x == 1):#If the second program loop is slected
                    program_state = 2 #Running indoor hud
                elif(curr_x == 2):#If the 3rd program loop is slected
                    program_state = 3 #Running 3 hour readout
                elif(curr_x == 3):#If the 4th program loop is slected
                    program_state = 4 #Running 8 day readout

def check_stick_events_2(hat):
    """Check stick events specifically for sub programs
       and returning to the main menu"""
    for event in hat.stick.get_events():
        #print(event)#FOR DEBUGGING STICK EVENTS
        if(event.action == "pressed"):
            if(event.direction == "up"):
                return True
    return False
                
def move_cursor(event):
    """Moves the grey cursor pixel across the top of
       the led matrix to aid in program loop selection"""
    global curr_x, hat, color_indices
    if event.action in ('pressed'):
        if(curr_x != 8):
            hat.set_pixel(curr_x,0,color_indices[curr_x])
            curr_x = clamp(curr_x + {
                'left': -1,
                'right': 1,
                }.get(event.direction, 0))
        else:
            #Should only happen on startup of this screen
            hat.set_pixel(0,0,grey)#Place cursor at top left pixel
            
    #Wrap around to other side when navigating main menu
    if curr_x == -1:
        curr_x = 7
    if curr_x == 8:
        curr_x = 0
        
    return_to_main_menu(hat, curr_x)

def display_option(curr_x,hat,color_indices):
    """Display the current main menu selection's
       associated mini image as defined by the functions
       herein"""
    show_main_screen(hat)
    #Show the appropriate image for the menu selection
    if(curr_x == 0):
        show_outdoor_hud_image(hat)
    elif(curr_x == 1):
        show_indoor_hud_image(hat)
    elif(curr_x == 2):
        show_3h_readout_image(hat)
    elif(curr_x == 3):
        show_8d_readout_image(hat)

#--------------------- OUTDOOR HUD LOOP & FUNCTIONS----------------------#
      
def run_outdoor_hud_loop(hat, curr_x):
    """Run the program loop for this mini program"""
    global program_state

    #How often do you want to request the forecast data?
    REFRESH_RATE = 600 #Every 10 min (600 seconds)
    #Clear the screen
    hat.clear()
    #We are initializing this screen now
    init = True
    #Capture the start time for refresh rate calculations
    start_time = time.time()
    #Run the sub program loop
    while(True):
        #Check to see if user wants to return to main menu
        return_requested = check_stick_events_2(hat)
        if(return_requested):
            break #Exit while to return to main menu

        counter = time.time() - start_time
        #If it's been < 10 min since the first, or most recent data download...
        if(counter > REFRESH_RATE or init):
            #Send another request for data
            owm = OWM(API_KEY)
            
            """FOR 8-DAY FORECAST (ROW 1 & ROW 2)"""
            #Retrieve daily forecast for 8 days (includes today)
            fc = owm.daily_forecast_at_id(SomeCity, limit=8)
            f = fc.get_forecast()
            i = 0
            for weather in f:
                #FOR DEBUGGING
                #print("At " , str(utc_to_eastern(weather.get_reference_time('date'))),weather.get_weather_code())
                if(i == 8):
                    break

                # Where W_CODES[weather.get_weather_code()][0] is giving the
                #  [weather.get_weather_code()] as a KEY to get the data object
                #  that holds the color at index [0] and description string
                #  (unused here) at index [1]
                
                #Top row
                hat.set_pixel(i, 0,W_CODES[weather.get_weather_code()][0])
                
                #Second row down from top
                hat.set_pixel(i, 1,W_CODES[weather.get_weather_code()][0])
                i += 1
                
            """FOR 3 HOUR FORECAST (ROW 3 & ROW 4)"""
            #Current conditions
            w = get_observation(SomeCity,owm)
            
            #Set leftmost pixels to show current status
            #Row 3
            hat.set_pixel(0, 2,W_CODES[w.get_weather_code()][0])
            #Row 4
            hat.set_pixel(0, 3,W_CODES[w.get_weather_code()][0])
            
            #Get current temperature
            temp_now = w.get_temperature('fahrenheit')["temp"]
            #Restrict temp_now readings to bound for display purposes
            if(temp_now > 100.00):
                temp_now = 100.00
            elif(temp_now < 0.00):
                temp_now = 0.00

            #Get current humidity
            humi_now = w.get_humidity()
            #Get current pressure
            pres_now = w.get_pressure()["press"]
            #Set current temperature color here for leftmost pixels
            curr_temp_color = cold_ok_or_hot(temp_now)
            
            """ROW 5 Code -- 3HR temperature forecast"""
            #Set leftmost pixel for ROW 5
            hat.set_pixel(0,4,curr_temp_color)
            
            #Get the 3hr forecast for the next 7 days        
            fc = owm.three_hours_forecast_at_id(SomeCity)
            #A list of weather objects
            f = fc.get_forecast()
            i = 1
            #Fill in the rest of the row after first pixels for rows 3,4,5
            for weather in f:
                if(i == 8):
                    break
                #Row 3
                hat.set_pixel(i, 2,W_CODES[weather.get_weather_code()][0])
                #Row 4
                hat.set_pixel(i, 3,W_CODES[weather.get_weather_code()][0])
                #Get the temp for the 3hr interval
                temp_then = weather.get_temperature('fahrenheit')["temp"]
                #Also set the temperature indicator row color to show if
                # the temp is high, low, or tolerable at 
                # ROW 5
                hat.set_pixel(i,4,cold_ok_or_hot(temp_then))
                i += 1

            """TEMPERATURE (ROW 6)"""
            #Where 8/100 = 12.5, so every pixel is 12.5 degrees F of temp.
            num_pixels = int(temp_now / 12.5)
            #Temperature displays on row y == 5(6th row) from 0
            # to 100 degrees where each pixel represents 12.5 degrees F
            for i in range(num_pixels):
                hat.set_pixel(i,5,curr_temp_color)
            for i in range(8-num_pixels):
                hat.set_pixel(i + num_pixels,5,nwhite)

            """HUMIDITY (ROW 7)"""
            curr_humi_color = dry_humid_or_ok(humi_now)
            num_pixels = int(humi_now / 12.5)
            #Humidity displays on row y == 6 (7th row)
            #as a relative percent
            for i in range(num_pixels):
                hat.set_pixel(i,6, curr_humi_color)
            for i in range(8-num_pixels):
                hat.set_pixel(i + num_pixels,6,nwhite)

            """AIR PRESSURE (ROW 8)"""
            #Air pressure (in millibars) displays on
            # the last row as one of three colors indicating
            # if the air pressure is high, low, or reasonable
            # for normal conditions
            curr_pres_color = pres_lo_hi_or_ok(pres_now)
            for i in range(8):
                hat.set_pixel(i,7,curr_pres_color)
            
            #Reset counter for refreshing
            start_time = time.time()
            init = False
            
    #Goes here after "break"
    program_state = 0 #Main menu
    return_to_main_menu(hat, curr_x)
    
def cold_ok_or_hot(temp_then):
    """Determines whether the temperature is too cold, too hot, or ok"""
    if(temp_then >= 80.00): #In degrees F
        return hot #Hot temperature range
    elif(temp_then >= 60.00 and temp_then < 80.00):
        return ok #Comfortable temperature range
    elif(temp_then < 60.00 and temp_then >= 50.00):
        return almost_ok #Almost green (ok) temperature range
    elif(temp_then < 50.00 and temp_then >= 40.00):
        return cold
    elif(temp_then < 40.00 and temp_then > 33.00):#33 for a degree of error
        return very_cold #Very cold temperature range
    elif(temp_then <= 33.00):
        return freezing #It's freezing

def dry_humid_or_ok(humi_then):
    """Determines the comfort value of the humidity"""
    if(humi_then >= 55 and humi_then <= 65): #As a relative percent
        return humi_ok #Comfortable temperature range
    elif(humi_then < 55):
        return humi_low
    elif(humi_then > 65):
        return humi_hi

def pres_lo_hi_or_ok(pres_then):
    """Determines the color value of the air pressure"""
    if pres_then < 979.00:#in millibars
        return pres_low
    elif pres_then >= 979.00 and pres_then <= 1027.00:
        return pres_ok
    elif(pres_then > 1027.00):
        return pres_hi

#--------------------- INDOOR HUD LOOP & FUNCTIONS----------------------#
    
# Most of the following code was taken from the bar graph example
#  in the sense hat emulator provided with Raspbian OS

def run_indoor_hud_loop(hat, curr_x):
    """Run the program loop for this mini app"""
    global program_state
    
    REFRESH_RATE = 60 #Every 60 seconds
    
    #We are initializing this screen now
    init = True
    #Capture the start time for refresh rate calculations
    start_time = time.time()
    #Run the sub program loop
    while(True):
        #Check to see if user wants to return to main menu
        return_requested = check_stick_events_2(hat)
        if(return_requested):
            break #Return to main menu

        counter = time.time() - start_time
        #If it's been < 60 sec since the first, or most recent sensing
        if(counter > REFRESH_RATE or init):
            display_readings(hat)
            #Reset counter for refreshing
            start_time = time.time()
            init = False

    #Goes here after break
    program_state = 0 #Main menu
    return_to_main_menu(hat, curr_x)
        
        
def clamp_2(value, min_value, max_value):
    """
    Returns *value* clamped to the range *min_value* to *max_value* inclusive.
    """
    return min(max_value, max(min_value, value))

def scale(value, from_min, from_max, to_min=0, to_max=8):
    """
    Returns *value*, which is expected to be in the range *from_min* to
    *from_max* inclusive, scaled to the range *to_min* to *to_max* inclusive.
    If *value* is not within the expected range, the result is not guaranteed
    to be in the scaled range.
    """
    from_range = from_max - from_min
    to_range = to_max - to_min
    return (((value - from_min) / from_range) * to_range) + to_min

def render_bar(screen, origin, width, height, color):
    """
    Fills a rectangle within *screen* based at *origin* (an ``(x, y)`` tuple),
    *width* pixels wide and *height* pixels high. The rectangle will be filled
    in *color*.
    """
    # Calculate the coordinates of the boundaries
    x1, y1 = origin
    x2 = x1 + width
    y2 = y1 + height
    # Invert the Y-coords so we're drawing bottom up
    max_y, max_x = screen.shape[:2]
    y1, y2 = max_y - y2, max_y - y1
    # Draw the bar
    screen[y1:y2, x1:x2, :] = color

def display_readings(hat):
    """
    Display the temperature, pressure, and humidity readings of the HAT as red,
    green, and blue bars on the screen respectively.
    """
    temp_f = hat.get_temperature_from_humidity()*(9/5) + 32 #convert to fahrenheit
    
    # Calculate the environment values in screen coordinates
    temperature_range = (0, 100)
    pressure_range = (950, 1050)
    humidity_range = (0, 100)
    temperature = scale(clamp_2(temp_f, *temperature_range), *temperature_range)
    pressure = scale(clamp_2(hat.pressure, *pressure_range), *pressure_range)
    humidity = scale(clamp_2(hat.humidity, *humidity_range), *humidity_range)
    # Render the bars
    screen = np.zeros((8, 8, 3), dtype=np.uint8)
    
    render_bar(screen, (0, 0), 2, round(temperature), color=(255, 0, 0))
    render_bar(screen, (3, 0), 2, round(pressure), color=(0, 255, 0))
    render_bar(screen, (6, 0), 2, round(humidity), color=(0, 0, 255))
    hat.set_pixels([pixel for row in screen for pixel in row])

    #Fill screen background
    pixels = hat.get_pixels()
    for i in range(64):
        if(pixels[i] == [0,0,0]):
            pixels[i] = nwhite
    hat.set_pixels(pixels)
    
 #--------------------------- 3 HOUR READOUT ------------------------#
    
def run_3h_readout(hat, curr_x):
    """Displays a text readout of the forecast for the next day or so
       in three-hour intervals"""
    global program_state
    readout_3h = []
    readout_string = ""
    owm = OWM(API_KEY)
    #Current conditions
    current_conditions = get_observation(SomeCity,owm)
    readout_3h.append(current_conditions)
    
     #Get the 3hr forecast for the next 7 days        
    fc = owm.three_hours_forecast_at_id(SomeCity)
    #A list of weather objects
    f = fc.get_forecast()
    i = 1
    for weather in f:
        readout_3h.append(weather)
        if(i == 8):
            break
        i += 1
    for weather in readout_3h:
        readout_string = readout_string + "At " + str(utc_to_eastern(weather.get_reference_time('date')).time())[0:5]
        readout_string = readout_string + " " + weather.get_detailed_status() + " - "

    hat.show_message(readout_string, scroll_speed = 0.035, text_colour = nwhite)
    
    #Goes here after break
    program_state = 0 #Main menu
    return_to_main_menu(hat, curr_x)

 #--------------------------- 8 DAY READOUT ------------------------#

def run_8d_readout(hat, curr_x):
    """Displays a text readout of the forecast for the next 8 days
       and gives the respective dates"""
    global program_state
    readout_8d = []
    readout_string = ""
    #Send another request for data
    owm = OWM(API_KEY)
            
    #Retrieve daily forecast for 8 days (includes today)
    fc = owm.daily_forecast_at_id(SomeCity, limit=8)
    f = fc.get_forecast()
    i = 0
    for weather in f:
        readout_8d.append(weather)
        if(i == 8):
            break
        i += 1
    for weather in readout_8d:
        readout_string = readout_string + " For " + str(utc_to_eastern(weather.get_reference_time('date')))[0:10]
        readout_string = readout_string + " " + weather.get_detailed_status() + " - "

    hat.show_message(readout_string, scroll_speed = 0.035, text_colour = nwhite)
    
    #Goes here after break
    program_state = 0 #Main menu
    return_to_main_menu(hat, curr_x)

 #--------------------------- SOME NEW READOUT OR LOOP ------------------------#
    """
            PUT ANY NEW FUNCTIONS HERE AS SHOWN ABOVE

            CAN ADD:
                -WIND INFO
                -INFO FOR ANOTHER CITY (copy+paste outdoor hud functionality)
                -ANYHTING ELSE PYOWM SUPPLIES AS DATA!

    program_state = 0 #Main menu
    return_to_main_menu(hat, curr_x)
    
    """

######## MAIN LOOP ######### 

hat.clear()

#Time between letters
wait_time = 0.4
# Show welcome message

hat.show_letter("W",\
                 text_colour = red,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("e",\
                 text_colour = orange,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("l",\
                 text_colour = yellow,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("c",\
                 text_colour = green,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("o",\
                 text_colour = blue,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("m",\
                 text_colour = violet,\
                 back_colour = black)
time.sleep(wait_time)
hat.show_letter("e",\
                 text_colour = pink,\
                 back_colour = black)
time.sleep(wait_time)

welc_speed = 0.05

hat.show_message(" to ",\
                 scroll_speed = welc_speed,\
                 text_colour = white,\
                 back_colour = black)
hat.show_message("sWEATHER v" + VERSION + "!",\
                 scroll_speed = welc_speed,\
                 text_colour = nwhite,\
                 back_colour = black)

#Show the welcome screen
hat.set_pixels(screen_welc)
    
while(True):
    
    if (program_state == 0):#Main menu
        check_stick_events(hat, curr_x)
    elif(program_state == 1):#Outdoor HUD loop
        # Always good to try and catch exceptions
        #  when dealing with online stuff
        #try:
        run_outdoor_hud_loop(hat, curr_x)
           # continue
        #except:
         #   print("Had some trouble at time: " + str(time.time()))
          #  continue
            
    elif(program_state == 2):#Indoor HUD loop
        run_indoor_hud_loop(hat, curr_x)
    elif(program_state == 3):#3hr readout
        run_3h_readout(hat, curr_x)
    elif(program_state == 4):#8d readout
        run_8d_readout(hat, curr_x)
        
    # Feel free to extend this! there are 4 more free
    #  spots on the main menu bar to add mini sub programs
    #  of your own! Just follow the function calls here and
    #  you should be able to see how to add some
    #  functionality of your own.
    #
    # See: (Ctrl+F) "SOME NEW READOUT OR LOOP"
    
