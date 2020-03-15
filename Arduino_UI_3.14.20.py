
# coding: utf-8

# This code is so we can control the Arduino output on our three ports, setting it to whatever voltage we want.

# To get this code to run properly, run the sketch located in:
# (Arduino Application) > File > Examples > Firmata > Standard Firmata

'''
Code worked on by: Ethan Levitt, Izze Sacksteder, Jadrian Teunissen
Last worked on: 14, March, 2020
'''

# In[1]:

import pyfirmata
import time
import numpy as np

# In[2]:

#user inputs
#magnitude of Magnetic Field (Gauss)
mag = float(input('desired magnitude of field: '))
#angle of Magnetic Field (Radians)
theta = float(input('desired direction of field: '))
#offset for earths magnetic field (Gauss)
offset = float(input('desired offset of field (z-direction): '))

# In[3]:

#define the port here
port='/dev/tty.usbmodem1431'
#example port (mac):  '/dev/tty.usbmodem14201'
#example port (windows): 'COM5'

# In[4]:

#board initialization

# This is the port that the Arduino is connected to. Check in the Arduino program
boardUNO = pyfirmata.Arduino(port)
# This tells the program that there's an Arduino UNO connected at the port (=com4)
time.sleep(1)
# This gives the connection a moment to settle. Dont get rid of this.


# In[5]:


#here we define all the pins
'''
General code here is: board.get_pin('a:7:i'), where
d is for digital/a for analog/p for pwm
7 is the pin number
i is for input/o for output
p for pwm = pulse width modulation, a way to create an analog out using digital pins
'''
pinY = boardUNO.get_pin('d:3:p')
pinX = boardUNO.get_pin('d:5:p')
pinZ = boardUNO.get_pin('d:6:p')



# In[6]:


'''
We are assuming that:
The red coil is in the z direction
The black coil is in the x direction
The yellow coil is in the y direction
'''

# In[7]:

#define components of desired B field from user inputs
Bx0 = mag*np.cos(theta)
By0 = mag*np.sin(theta)
Bz0 = offset

# In[8]:

#Now we do some math to integrate the calibration data
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

# In[9]:
    
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


# In[10]:

#arduino input (number between 1 and 0) as a function of desired pin voltage
def value(V):
    return V/4.911

#define values to write to each pin
xInput = (value(Vx(Ix(Bx0))))
yInput = (value(Vy(Iy(By0))))
zInput = (value(Vz(Iz(Bz0))))

#print values which will be written to each pin
print('Inputs for arduino:')

print ('xInput =', xInput)
print ('yInput =', yInput)
print ('zInput =', zInput)

print('Make sure these are all numbers between 0 and 1!')
        
# In[11]:

#write to the pins
pinX.write(xInput)
pinY.write(yInput)
pinZ.write(zInput)

