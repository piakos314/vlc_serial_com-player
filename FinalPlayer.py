import vlc
import threading
import serial
import time
import numpy as np
from pynput import keyboard

ser = serial.Serial('COM4', 115200) # init serial communication

# loading files
print('\n\nVideo(mp4) and File(txt) name should be the same!!\n')
name = input('Enter File name: ')
data = np.loadtxt(name+'_modified.txt',unpack='true')

# counting the data
count = -1
for item in data[0]:
    count+=1
    
# movement parameters
# This section makes the angle from the original data ( theta from 0-100 range)
angle = 30   # movement range
lowestangle = 70  # lowest angle in range
values = []
t = 0
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

time.sleep(1) # this is needed for the get_length() to work properly
media_length = int(player.get_length()/10)/10  # ms to 0.01s because our datawidth is 0.01s

# skipping parameters for data
skip_position = 10 * 20  # multiplier * seconds (skips by 20 sec)
skip_percent = (skip_position/media_length)  # convert skip to percent (0-1 range)

# send data to arduino
t = 0
drift = 2.30/1650 # (2.30/1650 eva) # second / timestamp # negative value for motion lagging
t0 = time.perf_counter()*10
pause_flag = 0

### serial communication stuff
#skip media player
def serial_com():
    global t
    player.set_position(0) # reset player position
    time.sleep(0.8)  #start delay compensation
    t0 = time.perf_counter()*10
    while t<count: #ignoring the last value for simplicity 
        while pause_flag==1:
            pass
        if (((time.perf_counter()*10 - t0)-(data[0][t]+int(drift*t)))>0.01):
            print(data[0][t])
            t+=1
        ser.write(values[t].to_bytes(1,'little'))
        time.sleep(0.01)
        t+=1
threading.Thread(target=serial_com).start()
ttt = threading.Thread(target=serial_com)
# keyboard control setup
def on_press(key):
    global t
    global t0
    global pause_flag
    global ttt
    if key == keyboard.Key.esc:
        player.stop()  # stop media
        ttt._stop()
        return False  # stop listen
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
            t0 = t0 + skip_position * 10
        
        if k=='right':
            now_position = player.get_position() # get current playhead position (0 - 1)
            skip = now_position + skip_percent           
            #skip media player
            player.set_position(skip)
            t = t + skip_position * 10
            t0 = t0 - skip_position * 10
            
        # self.keys.append(k)  # store it in global-like variable
        #return False  # stop listener; remove this if want more keys

listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys

ser.close()