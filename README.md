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
