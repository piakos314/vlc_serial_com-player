import vlc
import threading
import time
from pynput import keyboard

name = input('Enter File name: ')

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
skip_position = 10 * 20  # multiplier * seconds 
skip_percent = (skip_position/media_length)

# keyboard control setup
def on_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in ['up', 'down', 'left', 'right']:  # keys of interest
        if k=='up' or k=='down':
            player.pause()
        if k=='left':
            now_position = player.get_position() # get current playhead position (0 - 1)
            skip = now_position - skip_percent           
            #skip media player
            player.set_position(skip)
        
        if k=='right':
            now_position = player.get_position() # get current playhead position (0 - 1)
            skip = now_position + skip_percent           
            #skip media player
            player.set_position(skip)
            
        # self.keys.append(k)  # store it in global-like variable
        #return False  # stop listener; remove this if want more keys

listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
listener.join()  # remove if main thread is polling self.keys




# skipping params for media




