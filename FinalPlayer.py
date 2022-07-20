import vlc
import threading
import serial
import time
import numpy as np
from pynput import keyboard

ser = serial.Serial('COM4', 19200) # init serial communication

# loading files
print('\n\nVideo(mp4) and File(txt) name should be the same!!\n')
name = input('Enter File name: ')
data = np.loadtxt(name+'_modified.txt',unpack='true')

#### PARAMETER CHANGE HERE
# syncing parameter drift
drift = 2.30/1650  # second / timestamp (t) (the output log is in t/10) # negative value for motion lagging
                   # (eva = 2.30/1650) 
delay_start = 0.2  # delay between seek to begining and serial com
# movement parameters
# This section makes the angle from the original data ( theta from 0-100 range)
angle = 30   # movement range
lowestangle = 70  # lowest angle in range
values = []
t = 0
# counting the data
count = -1
for item in data[0]:
    count+=1
while t <= count:
    temp = (int(data[1][t])/100)*angle
    values.append(int(temp)+lowestangle)
    data[0][t]=data[0][t]/10
    t += 1


# Video player initialize
Instance = vlc.Instance('--fullscreen')
player = Instance.media_player_new()
Media = Instance.media_new(name+'.mp4')
Media.get_mrl()
player.set_media(Media)

# start player
player.play()
player.set_position(0.9)

time.sleep(1) # this is needed for the get_length() to work properly
media_length = int(player.get_length()/10)/10  # ms to 0.01s because our datawidth is 0.01s

# skipping parameters for data
skip_position = 10 * 20  # multiplier * seconds (skips by 20 sec)
skip_percent = (skip_position/media_length)  # convert skip to percent (0-1 range)

# timestamps needed for globar varable between threads
t0 = time.perf_counter()*10
t = 0 # also resets t=count from counting the data

### serial communication stuff
#skip media player
pause_flag = 0  # pause flag for the serial com thread, controlled by the keyboard thread
terminate_serial = 0 # serial com thread termination
def serial_com():
    global t
    global t0
    global delay_start
    player.set_position(0) # reset player position
    time.sleep(delay_start)  #start delay compensation
    t0 = time.perf_counter()*10
    while t<count: #ignoring the last value for simplicity 
        while pause_flag==1:
            pass
        if (((time.perf_counter()*10 - t0)-(t/10))>0.01):
            print(t/10)
            t+=1
        ser.write(values[t+int(drift*t*10)].to_bytes(1,'little'))
        time.sleep(0.01)
        t+=1
        if terminate_serial:
            break
threading.Thread(target=serial_com).start()
ttt = threading.Thread(target=serial_com)


# keyboard control setup
def on_press(key):
    global t
    global t0
    global pause_flag
    global ttt
    global terminate_serial
    if key == keyboard.Key.esc:
        terminate_serial = 1
        player.stop()  # stop media
        time.sleep(1)
        return False  # stop listen keys
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in ['up', 'down', 'left', 'right']:  # keys of interest
        if k=='up' or k=='down':
            player.pause()
            if pause_flag == 0:
                pause_flag = 1
            else:
                pause_flag = 0
        if k=='left':
            now_position = player.get_position() # get current playhead position (0 - 1)
            skip = now_position - skip_percent           
            #skip media player
            player.set_position(skip)
            t = t - skip_position * 10
            t0 = t0 + skip_position
        
        if k=='right':
            now_position = player.get_position() # get current playhead position (0 - 1)
            skip = now_position + skip_percent           
            #skip media player
            player.set_position(skip)
            t = t + skip_position * 10
            t0 = t0 - skip_position
            
        # self.keys.append(k)  # store it in global-like variable
        #return False  # stop listener; remove this if want more keys

listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys

ser.close() # close serial port