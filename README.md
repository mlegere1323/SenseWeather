# Sense Weather (sWeather) for Raspberry Pi Sense Hat

Author: Michael Legere [https://github.com/mlegere1323]
Date 1/15/2017
Version 1.0

This is a program used to display relevant weather information using
pyowm, the Raspberry Pi Sense Hat, and the Raspberry Pi.

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

## How To Use

You will first need a Raspberry Pi with wifi, and a Raspberry Pi SENSE Hat.

This program will need to be run at startup: [Here's how to do that](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/).

When the program starts, it will have a "welcome" animation, followed by this welcome screen with a sun, clouds, and field (as below--please forgive the image quality, as the LED lights were hard to capture well, so I put paper over them so it didn't look like white light all over).

![Welcome Screen](/images/WelcomeScreen.jpg)

Following this, you'll only need to use the joystick on the sense hat to use the program. 

Note the top pixel row is the menu, where each colored pixel represents a menu option. You can scroll through the menu by moving the joystick left or right.

## **The Menu Options:**
### OH "Outdoor HUD"
![Outdoor HUD Menu](/images/OutdoorHUDMenu.jpg)
![Outdoor HUD](/images/OutdoorHUD.jpg)

* **Rows 1 and 2** are the 8-day forecast, as depicted by color representing the general outlook. Each single pixel on the x axis represents a day in these rows, starting with today (the leftmost pixel in the top two rows).
```python 
#Forecast color groups RGB values
thunder = [102,102,0]
drizzle = [0,204,204]
rain = blue
snow = white
atmos = [70,50,100]
danger = red
clear = yellow
clouds = grey
wind = [204,153,255]
```
* **Rows 3 and 4** are the 3-hour-interval forecast pixels, much like the first two rows, each pixel column is colored based on real-time information. These rows represent the general outlook for now, through the next 24 hours.
* **Row 5** is the 3-hour-interval temperature readout row, and is a singular row, unlike the previous double-row outputs. This row will show you the general temperature in three hour intervals starting form now, based on a color scheme (using R,G,B) loosely defined as follows (for more details, please see code):
```python
#Below 30 degrees F, temp pixel will be white
freezing = white
# Temperature colors (so you know generally
#  how hot/cold it is instantly, visually
very_cold = pink
cold = [70,130,174] #cyan/light blue
almost_ok = [0,200,150] #turquoise/blue-green
ok = green
hot = red
```
* **Row 6** is the current temperature, using the color scheme from row 5. This pixel row will fill up towards the right if it gets hotter, or recede towards the left if it gets colder--bounded by 100 and 0 degrees F. respectively, and drawn relative to this temperature range. Note the background for this row is beige; only rows 5 and 6 have a background in this Outdoor HUD.
* **Row 7** is the relative humidity, and is drawn scaled from 0 to 100% as the previous row, with a beige background, but is only colored with three colors (based on general weather science consensus for humidity readings): Low: Light Blue, Ok: Green, High: Red. For details on how this is discerned, please see code.
* **Row 8** is the current readout for atmospheric pressure, as indicated by the following color scheme: Low: Light Blue, Ok: Green, High: Red. The whole row will be the relevant color indicating if the pressure is low, high, or ok. For details on how this is discerned, please see code.

### IH "Indoor HUD"
![Indoor HUD Menu](/images/IndoorHUDMenu.jpg)
![Indoor HUD](/images/IndoorHUD.jpg)

* There will be three bars displayed: a Red, Green, and Blue bar, which represent temperature, pressure, and humidity, respectively, as measured in real time by the on-board sensors in the sense hat. Each bar will remain the same color, but will raise or lower depending on readings by the pi hat, relative to the following ranges:
```python
temperature_range = (0, 100)
pressure_range = (950, 1050)
           humidity_range = (0, 100)
```
