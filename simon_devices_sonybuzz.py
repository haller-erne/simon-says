import hid
from bitstring import BitArray # pip install bitstring
from blinkt import set_pixel, set_brightness, show, clear

class Devices:
    def __init__(self):
        self._running = True
        self._devices = []
 
    def init(self):
        self._devices = self.enumerate(0x483, 0x1001) # h+e STM dome button
        self._h = hid.Device(1356,4096)   # Sony Buzz keys
        # self._h = hid.Device(0x483, 0x1001) # h+e STM dome button
        clear()
        show()

    def enumerate(self, vid=0, pid=0):
        ret = []
        info = hid.hid_enumerate(vid, pid)
        c = info
        while c:
            ret.append(c.contents.as_dict())
            c = c.contents.next

        hid.hid_free_enumeration(info)
        return ret        

    # check, if any key has been pressed
    def poll(self):
        d = self._h.read(8, 0)    # timeout = 0
        print(d)
        if len(d) == 0:
            return -1
        
        # decode keys
        c = BitArray(d)
        key1 = c[16:40] #c[23]
        key2 = c[16:40] #c[18]
        key3 = c[16:40] #c[31]
        key4 = c[16:40] #c[26]
        if key1[7]: return 1
        if key2[2]: return 2
        if key3[13]: return 3
        if key4[8]: return 4
        return 0

    def led1(self):     # green
        set_pixel(6,   0, 255,   0)
        set_pixel(7,   0, 255,   0)
    def led2(self):     # red
        set_pixel(4, 255,   0,   0)
        set_pixel(5, 255,   0,   0)
    def led3(self):     # yellow
        set_pixel(2, 128, 128,   0)
        set_pixel(3, 128, 128,   0)
    def led4(self):     # blue
        set_pixel(0,   0,   0, 255)
        set_pixel(1,   0,   0, 255)

    def led(self, key):
        clear()
        set_brightness(0.5)
        if key == 1: 
            self.led1()
        if key == 2: 
            self.led2()
        if key == 3: 
            self.led3()
        if key == 4: 
            self.led4()
        show()

