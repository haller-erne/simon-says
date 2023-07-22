import hid
from bitstring import BitArray # pip install bitstring
# from blinkt import set_pixel, set_brightness, show, clear
import blinkt
import pygame

class Devices:
    def __init__(self):
        self._running = True
        self._devices = []
        self._h = [ None ]*4
        self._serials = [
            '206037905948',
            '204737855948',
            '206037985948',
            '2046379B5948'
        ]
        self._colors = [ [0,0,0,7] ]*4      # r,g,b,brightness
        self._old_colors = [ [0,0,0,7] ]*4
        self._tLastUpd = pygame.time.get_ticks()
        self._tAnimate = self._tLastUpd
        self._AnimateIdx = 0
        self._hSwitch = None
        self._old_sw = [ 99,99,99,99 ]
        self._sw = [ 0,0,0,0 ]              # selector keys
        self._keys = [ 0,0,0,0 ]            # dome buttons
        self.keycolors = [ [0,255,0], [255,0,0], [128,128,0], [0,0,255] ]

    # helpers, see http://docs.pimoroni.com/blinkt/_modules/blinkt.html
    def set_color(self, x, r, g, b, brightness=None):
        if brightness is None:
            brightness = self._colors[x][3]
        else:
            brightness = int(31.0 * brightness) & 0b11111

        self._colors[x] = [int(r) & 0xff, int(g) & 0xff, int(b) & 0xff, brightness]

    def init(self):
        devs = hid.enumerate(0x483, 0x1002) # h+e STM selector switches
        for dev in devs:
            self._hSwitch = hid.Device(dev['vendor_id'], dev['product_id'], dev['serial_number'])

        self._devices = hid.enumerate(0x483, 0x1001) # h+e STM dome button
        # self._h = hid.Device(0x483, 0x1001) # h+e STM dome button
        for dev in self._devices:
            h = hid.Device(dev['vendor_id'], dev['product_id'], dev['serial_number'])
            i = self._serials.index(h.serial)
            self._h[i] = h
        self._led_clear()
        self._led_show()
        self._led_show_sw([0,0,0,0])

    def _poll(self, h):
        if h == None:
            return -1       # not initializes --> no data
        try:
            d = ''
            d = h.read(8, 0)    # timeout = 0
        except:
            print('read failed!')
            pass
        if len(d) == 0:
            return -1
        
        # decode keys
        print(d)
        cmd = d[0]
        num = d[1]
        adr = d[2]
        sw1 = d[3]
        #sw2 = d[4]
        #sw3 = d[5]
        #sw4 = d[6]
        return sw1
    
    def _poll_sw(self):
        # poll the selector switch
        h = self._hSwitch
        if h == None:
            return -1       # not initializes --> no data
        try:
            d = ''
            d = h.read(8, 0)    # timeout = 0
        except:
            print('read failed!')
            pass
        if len(d) == 0:
            return -1
        
        # decode keys
        print('selector: ', end='')
        print(d)
        cmd = d[0]
        num = d[1]
        adr = d[2]
        sw4 = d[3]
        sw3 = d[4]
        sw2 = d[5]
        sw1 = d[6]
        self._sw = [sw1, sw2, sw3, sw4]
        return 1

    # check, if any key has been pressed
    def poll(self):

        if pygame.time.get_ticks() - self._tLastUpd > 100:
            self._tLastUpd = pygame.time.get_ticks()
            self._led_show(True)    # force LED update
            self._led_show_sw(self._old_sw, True) 

        self._poll_sw()

        for i in range(4):
            h = self._h[i]
            ret = self._poll(h)
            if ret != -1:
                self._keys[i] = ret
                if ret != 0:
                    ret = i+1       # key number 1..4
                return ret
            
        return -1

    def get_sw(self):
        return self._sw
    def get_keys(self):
        return self._keys

    def led1(self):     # green
        blinkt.set_pixel(6,   0, 255,   0)
        blinkt.set_pixel(7,   0, 255,   0)
        self.set_color(  0,   0, 255,   0)
    def led2(self):     # red
        blinkt.set_pixel(4, 255,   0,   0)
        blinkt.set_pixel(5, 255,   0,   0)
        self.set_color(  1, 255,   0,   0)
    def led3(self):     # yellow
        blinkt.set_pixel(2, 128, 128,   0)
        blinkt.set_pixel(3, 128, 128,   0)
        self.set_color(  2, 128, 128,   0)
    def led4(self):     # blue
        blinkt.set_pixel(0,   0,   0, 255)
        blinkt.set_pixel(1,   0,   0, 255)
        self.set_color(  3,   0,   0, 255)

    def _led_clear(self):
        brightness = 0.5
        blinkt.clear()
        blinkt.set_brightness(brightness)
        for i in range(4):
            self._colors[i][0:3] = [0, 0, 0]
            self._colors[i][3] = int(31.0 * brightness) & 0b11111

    def _led_show(self, force=False):
        blinkt.show()
        #print('led: ', end='')
        for i in range(4):
            color = self._colors[i]
            if force or color != self._old_colors[i]:
                dev = self._h[i]
                if dev != None:
                    r, g, b, brightness = color
                    tx = b'\x01\x04\x00\x80' + r.to_bytes(1, 'big') + g.to_bytes(1, 'big') + b.to_bytes(1, 'big')
                    try:
                        dev.write(tx)
                        #print(tx, end='')
                        #print(' : ', end='')
                    except:
                        print('write failed!')
                        pass
                self._old_colors[i] = color
       
        #print('')

    def _led_show_sw(self, sw, force=False):
        if force or sw != self._old_sw:
            dev = self._hSwitch
            if dev != None:
                tx = b'\x01\x05\x00' + sw[3].to_bytes(1,'big') + sw[2].to_bytes(1,'big') + sw[1].to_bytes(1,'big') + sw[0].to_bytes(1,'big')
                try:
                    dev.write(tx)
                except:
                    print('selector: write failed!')
                    pass
            self._old_sw = sw

    def animate(self):
        if pygame.time.get_ticks() - self._tAnimate > 100:
            self._tAnimate = pygame.time.get_ticks()

            r = self._AnimateIdx * 16
            g = 255 - (self._AnimateIdx * 16)
            b = 0x78
            self.set_color(0, r, g, b)
            self.set_color(1, r, g, b)
            self.set_color(2, r, g, b)
            self.set_color(3, r, g, b)

            self._AnimateIdx = self._AnimateIdx + 1
            if self._AnimateIdx >= 16: 
                self._AnimateIdx = 0

            self._led_show(True)    # force LED update

    def led(self, key):
        self._led_clear()
        if key == 1: 
            self.led1()
        if key == 2: 
            self.led2()
        if key == 3: 
            self.led3()
        if key == 4: 
            self.led4()
        self._led_show(True)

    def led_all(self, color):
        self._led_clear()
        r, b, g = color
        for i in range(4):
            self.set_color(i, r, b, g)
        self._led_show(True)


    def led_sw(self, sw):
        self._led_show_sw(sw, True)
