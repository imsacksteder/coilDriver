#!/usr/bin/env python3

'''
This code is so we can control the Arduino output on our three ports, setting it to whatever voltage we want.

To get this code to run properly, run the sketch located in:
(Arduino Application) > File > Examples > Firmata > Standard Firmata

Code worked on by: Ethan Levitt, Izze Sacksteder, Jadrian Teunissen
'''
import pyfirmata
import time
import numpy as np
import tkinter as tk

#----------------------------------------
# board initialization
#----------------------------------------

#define the port that the Arduino is on
port='/dev/tty.usbmodem1411101'
#example port (mac):  '/dev/tty.usbmodem14201'
#example port (windows): 'COM5'
boardUNO = pyfirmata.Arduino(port)
# This tells the program that there's an Arduino UNO connected at the port (=com4)
time.sleep(1)
# This gives the connection a moment to settle. Dont get rid of this.


'''
Defining pins

General code here is: board.get_pin('a:7:i'), where
d is for digital/a for analog/p for pwm
7 is the pin number
i is for input/o for output
p for pwm = pulse width modulation, a way to create an analog out using digital pins
'''
pinY = boardUNO.get_pin('d:3:p')
pinX = boardUNO.get_pin('d:5:p')
pinZ = boardUNO.get_pin('d:6:p')

#----------------------------------------
# Math to integrate the calibration data
#----------------------------------------
#current as a function of Magnetic Field
def Ix(Bx):
    if Bx > 0:
        return (Bx-0.2829644135733139)/2.9485607589731986 #linear fit
    if Bx<= 0:
        return 0

def Iy(By):
    if By > 0:
        return (By-0.012218694814285891)/3.137805514887857
    if By <= 0:
        return 0

def Iz(Bz):
    if Bz > 0:
        return (Bz-0.07240858035683723)/16.422404523051785
    if Bz <= 0:
        return 0

#voltage as a funtion of current
def Vx(Ix):
    if Ix > 0:
        return 3.25*np.log(4.8*(Ix+0.218))
    if Ix <= 0:
        return 0

def Vy(Iy):
    if Iy > 0:
        return 1.759*np.log(4.628*(Iy+0.228))
    if Iy <= 0:
        return 0

def Vz(Iz):
    if Iz > 0:
        return 1.966*np.log(39.22*(Iz+0.027))
    if Iz <= 0:
        return 0

#arduino input (number between 1 and 0) as a function of desired pin voltage
def value(V):
    return V/4.911


#----------------------------------------
# Tk interface (main)
#----------------------------------------

m = tk.Tk()
m.title('Arduino GUI')
tk.Label(m, text='Please select a mode:').grid(row=0)
#tk.Label(m, text='Static:').grid(row=1)
#tk.Label(m, text='Dynamic:').grid(row=2)

#----------------------------------------
# Tk interface (Static)
#----------------------------------------

def static():
    '''
    user inputs

    magnitude of Magnetic Field (Gauss)
    mag = float(input('desired magnitude of field: '))

    angle of Magnetic Field (Radians)
    theta = float(input('desired direction of field: '))

    offset for earths magnetic field (Gauss)
    offset = float(input('desired offset of field (z-direction): '))
    '''
    m.destroy()
    static = tk.Tk()
    static.title('Static Input')
    tk.Label(static, text='Magnitude (Gauss):').grid(row=0)
    tk.Label(static, text='Angle (Degrees):').grid(row=1)
    tk.Label(static, text='Z-Offset (Gauss):').grid(row=2)
    mag = tk.Entry(static, textvariable = 'mag')
    angle = tk.Entry(static, textvariable = 'theta')
    offset = tk.Entry(static, textvariable = 'offset')

    tk.Label(static, text='Click to print arduino inputs:').grid(row=3, column =0)
    tk.Label(static, text='Click to write to arduino pin:').grid(row=4, column=0)

    mag.grid(row=0, column=1)
    angle.grid(row = 1, column = 1)
    offset.grid(row =2, column = 1)

    def check():

        mag0 = float(mag.get())
        theta0 = float(angle.get())*np.pi/180
        #we want it in rad for the math
        offset0 = float(offset.get())
        Bx0 = mag0 * np.cos(theta0)
        By0 = mag0 * np.sin(theta0)
        Bz0 = offset0


        #define values to write to each pin
        xInput = (value(Vx(Ix(Bx0))))
        yInput = (value(Vy(Iy(By0))))
        zInput = (value(Vz(Iz(Bz0))))


        #print values which will be written to each pin
        tk.Label(static, text='                             ').grid(row=5)
        tk.Label(static, text='                             ').grid(row=6)
        tk.Label(static, text='                             ').grid(row=7)
        tk.Label(static, text='                             ').grid(row=8)

        tk.Label(static, text='Inputs for arduino:').grid(row=5)
        tk.Label(static, text='xInput =' + str(round(float(xInput),2))).grid(row=6)
        tk.Label(static, text='yInput =' + str(round(float(yInput),2))).grid(row=7)
        tk.Label(static, text='zInput =' + str(round(float(zInput),2))).grid(row=8)


        if xInput > 1:
            tk.Label(static, text='xINPUT out of range [0,1]', fg="red").grid(row=6, column=1)
        if yInput > 1:
            tk.Label(static, text='yINPUT out of range [0,1]', fg="red").grid(row=7, column=1)
        if zInput > 1:
            tk.Label(static, text='zINPUT out of range [0,1]', fg="red").grid(row=8, column=1)

    def pinwrite():
        check()
        mag0 = float(mag.get())
        theta0 = float(angle.get())*np.pi/180
        offset0 = float(offset.get())
        Bx0 = mag0 * np.cos(theta0)
        By0 = mag0 * np.sin(theta0)
        Bz0 = offset0

        #define values to write to each pin
        xInput = (value(Vx(Ix(Bx0))))
        yInput = (value(Vy(Iy(By0))))
        zInput = (value(Vz(Iz(Bz0))))
        #define components of desired B field from user inputs

        #write to the pins
        print('write to the pins')
        pinX.write(xInput)
        pinY.write(yInput)
        pinZ.write(zInput)

    #buttons
    b = tk.Button(static, text="check", command=check)
    b.grid(row=3, column=1)

    b0 = tk.Button(static, text="run", command=pinwrite)
    b0.grid(row=4, column=1)


    static.mainloop()

#----------------------------------------
# Tk interface (Dynamic)
#----------------------------------------

def dynamic():
    '''
    This function will run between a magnetic field at
    0 degrees and swings out to 90 degrees.
    The magnitude of the magnetic field, along with the change in angle
    and time between each iteration are all controlled with the tk Interface
    '''
    m.destroy()
    dyno = tk.Tk()
    dyno.title('Dynamic Input')

    tk.Label(dyno, text='Field magnitude (gauss)').grid(row=0)
    tk.Label(dyno, text='Change in angle per iteration(degrees)').grid(row=1)
    tk.Label(dyno, text='Time between intervals (seconds)').grid(row=2)
    tk.Label(dyno, text='Z-direction offset(gauss)').grid(row=3)

    TKmag = tk.Entry(dyno, textvariable = 'TKmag')
    TKmag.grid(row=0, column=1)
    TKdAngle = tk.Entry(dyno, textvariable = 'TKdAngle')
    TKdAngle.grid(row=1, column=1)
    TKwaitTime = tk.Entry(dyno, textvariable = 'TKwaitTime')
    TKwaitTime.grid(row=2, column=1)
    TKoffset = tk.Entry(dyno, textvariable = 'TKoffset')
    TKoffset.grid(row=3,column=1)

    def go():
        mag = float(TKmag.get())
        dTheta = float(TKdAngle.get())*np.pi/180
        waitTime = float(TKwaitTime.get())
        offset = float(TKoffset.get())
        i = 0

        start = time.time()
        while i*dTheta <= np.pi/2:
            theta = i*dTheta
            Bx = mag * np.cos(theta)
            By = mag * np.sin(theta)
            Bz = offset

            #define values to write to each pin
            xInput = (value(Vx(Ix(Bx))))
            yInput = (value(Vy(Iy(By))))
            zInput = (value(Vz(Iz(Bz))))
            #define components of desired B field from user inputs

            tk.Label(dyno, text='                             ').grid(row=5)
            tk.Label(dyno, text='                             ').grid(row=6)
            tk.Label(dyno, text='                             ').grid(row=7)
            tk.Label(dyno, text='                             ').grid(row=8)

            tk.Label(dyno, text='Inputs for arduino:').grid(row=5)
            tk.Label(dyno, text='xInput =' + str(round(float(xInput),2))).grid(row=6)
            tk.Label(dyno, text='yInput =' + str(round(float(yInput),2))).grid(row=7)
            tk.Label(dyno, text='zInput =' + str(round(float(zInput),2))).grid(row=8)

            #write to the pins
            measuredMag=np.sqrt(Bx**2+By**2)
            print('Magnitude: '+str(measuredMag)+" Gauss")
            pinX.write(xInput)
            pinY.write(yInput)
            pinZ.write(zInput)
            i +=1
            dyno.update()
            magnitudeList+=measuredMag
            if i*dTheta <= np.pi/2:
                time.sleep(waitTime)

        end = time.time()
        print ("done. "+str(end-start)+" seconds elapsed.")

    tk.Button(dyno,text='go', command=go).grid(row=4,column=1)
    dyno.mainloop()

#----------------------------------------
# The rest of main interface
#----------------------------------------

staticButton = tk.Button(m, text="Static Mode", command=static)
staticButton.grid(row=1)

dynamicButton = tk.Button(m, text="Dynamic Mode", command=dynamic)
dynamicButton.grid(row=2)

m.mainloop()
