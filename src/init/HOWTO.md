Some notes about the code and how I use it.

# Earthquake Data

I use the ShakeNet Station View web app to get the data for the quake
I’m interested in. (I also use EarthquakesGA and any other source I
can find for aussie quakes that aren’t on RS). The quake/event data is
entered into lines 72 to 79.

# Station Data

Station data is in lines 65 to 70 and once setup doesn’t need to be
changed unless you are changing the station you want to use.

# Plot Timing

Immediately below the event data, I enter figures for a delay and
duration. The delay is the number of seconds from the event
(earthquake) time till the signal plots start. The duration is, of
course how long the signal plot should run for.

# Bandpass Filters

In line 91 to 96 are some bandpass filter settings. Initially I edited
the filter corner figures to change the bandpass filter, but I’ve
since got a few common filters I use set up on separate lines and
simply comment out the ones I don’t want to use at the time.

# Waveforms for Displacement, Velocity and Acceleration

In lines 101 to to 106, the program gets the waveform from the server
and then makes two additional copies of it. This is so they can be
processed into displacement, velocity and acceleration plots when the
instrument response is removed.

# Map

Lines 181 to 220 is where the map is plotted. Initially plot_map in
line 182 is true, and the plt.savefig command in line 218 is commented
out. This allows the map to be adjusted before saving the final
version. Once the final version is saved, I comment out the
plt.savefig command again ready for next time, and then set plot_map
to false to skip all the mapping code for subsequent runs.

# Plotting Traces

In the section where the traces are plotted (lines 261 to 280) there
are several code lines commented out which can be uncommented to
use. For example, there’s provision for manual y scaling on each plot
so that strong noise in the plot can be clipped and the signal still
be reasonably displayed.

# Phase Arrival Array

Lines 347 to 376 is where an array of phase arrival data is
constructed and plotted into the figure. This array includes the phase
name, the arrival time in seconds after the earthquake, the arrival
time in UTC and the vertical component of the signal as a percentage
of the true signal. The vertical component is all that a Shake and
Boom or 1D can detect, so knowing the vertical component allows some
judgement about how much signal to expect from that phase. The
allphases variable on line 356 is initially set to true to plot all
the phase ray paths in the one diagram. I usually do this for the
first figure, with a long duration of , say, 900 seconds. After that,
I change allphases to false so only the path of the phases in the plot
window are plotted.

# Saving Final Figure Plot

At the end of the code (line 457 in fact) the plt.savefig command is
commented out until the figure is final. When the command is
uncommented the figure is saved using a standardised file name made up
of the path, and the quake magnitude, location, time and the phases in
the plot.

# How I Use It

Initially I run the program to produce a plot of the map and the
initial long duration plot (say 900s) with all phases displayed. I
then set allphases to false to only display the ray paths of the
phases in the plots for subsequent plots. If the filter is 0.7 to 2
Hz, I will usually change the plot_envelopes variable in line 289 to
true to add envelopes to the waveforms. Envelopes can get messy with
broad bandpass filters and long durations.

For the subsequent plots, I refer to the phase arrival times in the
IPython Console of Spyder (or in the phases array on the previous
figure) to change the delay and duration of the plots for each phase
or group of phases. This gives a detailed plot of the arrival(s) for
timing. As the core mantle boundary and inner outer core boundaries
may be a different shape to the spherical model, the actual arrivals
may be earlier or later than predicted.

# Detecting Weak Signals

To help in detecting weak signals, background noise standard deviation
lines are plotted on the waveform plots. These are calculated from the
signal 900s before to 600s after the earthquake time so that
temperature and other periodic effects on the Shake sensitivity are
taking into account as well as local noise and noise from other
earthquake signals. This is done by slicing the 900 + 600 = 1500
second signals into 15s long pieces and finding the minimum standard
deviation for a 15s interval. This seems, by trial and error to be a
reasonable fit for the base noise level. If this is not found to be
the case, the time intervals can be adjusted to suit in lines 88 and
89 for the background noise start (bnstart) and end (bnend) and in
line 157 where the background noise sample (bns) is calculated by
dividing (bnend - bnstart) by 15 seconds.

# Specific Energy Plot

The other thing I added to aid in detect weak signals was to calculate
the Specific Energy signal from the velocity waveform. This is based
on the formula E = mvv/2, so by squaring the velocity waveform and
dividing by 2, the specific energy plot is obtained. The intent was
that this would make weak signal more obvious, and it does to some
extent, though perhaps it may benefit from plotting on the log y
scale. What I have found is that specific energy often gives a very
clear indication of arrival time.
