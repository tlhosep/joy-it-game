""" module: tlu_hardwarebase
** Content **
This module provides the base for all hardware-bound classes

** Details **
Besides defining the dip-settings that are needed in order to get the hardware working,
we also define the port-numbers we need to setup the GPI correctly

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-31 
""" 

class tlu_hardwarebase(object):
    '''
    Class used as a baseclass to perform certain hardware-bound activities
    Please note that the GPIO is working in BCM Mode only as the modes could not be mixed!
    '''
    #buttons in bcm notation
    button_up = 26
    button_down = 13
    button_left = 25
    button_right = 19
    

    #buzzer
    buzzer_bcm = 18

    #lcd panel
    lcd_address = 0x21
    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows    = 2
    
    #led 7 segment display
    led_7seg_address = 0x70

    def __init__(self):
        '''
        Initializer, but nothing to do here
        '''
        pass

    def lefthand_dip_setting(self) -> int:
        '''
        Default for the left DIP-switch: all buttons down (0)
        '''
        return 0x00

    def righthand_dip_setting(self) -> int:
        '''
        Default for the right DIP-switch: all buttons down (0)
        '''
        return 0x00

    def showdip(self, diphex) -> str:
        '''
        Show the DIP-setting in a human readable format
        :param diphex: 8-bit code for the DIP-switch, 0=down, 1 = up
        '''
        setting=0x80
        result ="|"
        for i in range(8):  # @UnusedVariable
            if (setting & diphex != 0):
                result += "°|"
            else:
                result += "_|"
            setting = setting >> 1
        return result
    
    def showleft_dip(self) -> str:
        '''
        Show the setting for the lefthand switch in human readable format
        '''
        return self.showdip(self.lefthand_dip_setting())
    
    def showright_dip(self) -> str:
        '''
        Show the setting for the righthand switch in human readable format
        '''
        return self.showdip(self.righthand_dip_setting())
    