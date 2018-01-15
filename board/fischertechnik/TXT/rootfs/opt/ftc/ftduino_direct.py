#
# Kommandos fuer ftduino.comm :
#
#    void led_set <0|1> 
#    
#    string ftduino_direct_get_version
#    char[16] ftduino_id_set <string maxlen=16>
#    char[16] ftduino_id_get
#    
#
#    void input_set_mode <I1..I8> <switch|resistance|voltage> 
#    uint16_t input_get <I1..I8>
#
#    void output_set <O1..O8> <mode="0..2"> <pwm=[0..512]>       mode: 0=open 1=switch to plus (normal operation) 2=switch to gnd
#    void motor_set <M1..M4> <right|left|brake> <pwm=[0..512]>
#
#    void ultrasonic_enable <true|false>
#    int16_t ultrasonic_get()
#
#    void counter_set_mode <none|rising|falling|any>
#    uint16_t counter_get <C1..C4>
#    void counter_clear <C1..C4>
#    uint8_t counter_get_state <C1..C4>
#    
#    Beispiel:
#    myftd=ftduino_direct.ftduino()
#    myftd.comm("motor M1 right 512")
#


import serial
import serial.tools.list_ports
import time

FTDUINO_DIRECT_PYTHON_VERSION = "1.0.8"

FTDUINO_VIRGIN_VIDPID="1c40:0537"
FTDUINO_VIDPID="1c40:0538"

__all__ = ["ftduino_scan", "ftduino_find_by_name", "ftduino", "getLibVersion"]

def getLibVersion():
    return FTDUINO_DIRECT_PYTHON_VERSION
    

def ftduino_scan():
    #   scannt nach ftduinos und gibt eine Liste zurueck, die den device-pfad und die vom ftduino zurueckgemeldete ID beinhaltet
    #   [x][0] enthaelt den device-pfad, [x][1] die ID 
    #
    devices = []
    for dev in serial.tools.list_ports.grep("vid:pid="+FTDUINO_VIDPID):
        try:
            o = serial.Serial(dev[0], 115200, timeout=0.1, writeTimeout = 0.1)
            time.sleep(0.25)
            o.flushInput()
            o.flushOutput()
            o.write("ftduino_id_get\n".encode("utf-8"))
            n=o.readline().decode("utf-8")[:-2]
            o.close()
            devices.append([dev[0], n])
        except:
            devices.append([dev[0], ""])
    for dev in serial.tools.list_ports.grep("vid:pid="+FTDUINO_VIRGIN_VIDPID):
        try:
            o = serial.Serial(dev[0], 115200, timeout=0.1, writeTimeout = 0.1)
            time.sleep(0.25)
            o.flushInput()
            o.flushOutput()
            o.write("ftduino_id_get\n".encode("utf-8"))
            n=o.readline().decode("utf-8")[:-2]
            o.close()
            devices.append([dev[0], n])
        except:
            devices.append([dev[0], ""])
            
    return devices
        
def ftduino_find_by_name(duino):
    #   sucht nach einem ftduino mit angegebenem Namen und gibt im Erfolgsfall den device-pfad zurueck
    #   der device-Pfad kann beim Erzeugen eines ftduino-Objekts angegeben werden, um gezielt einen 
    #   bestimmten ftduino anzusprechen.
    d=ftduino_scan()
    try:
        return next(c for c in ftduino_scan() if c[1] == duino)[0]
    except:
        return None
    
class ftduino(object):

    def __init__(self, device=None):
        self.ftduino=None
        
        # bei Angabe eines device-Pfades wird versucht, diesen ftduino zu oeffnen
        # ansonsten wird der erste gefundene ftduino angesprochen
        
        try:
            if device==None:
                liste=ftduino_scan()
                port=liste[0][0]
                if liste!=None:
                    self.ftduino = serial.Serial(port, 115200, timeout=0.1, writeTimeout = 0.1)
                    time.sleep(0.5) #give the connection a second to settle
            else:
                self.ftduino = serial.Serial(device, 115200, timeout=0.1, writeTimeout = 0.1)
        except:
            pass

    def getDevice(self):
        return self.ftduino
    
    def comm(self, command):
        try:
            command=command+"\n"
            self.ftduino.flushInput()
            self.ftduino.flushOutput()
            self.ftduino.write(command.encode("utf-8"))
            data = self.ftduino.readline()
            if data:
                if len(data.decode("utf-8"))>2: return data.decode("utf-8")[:-2]
                return "Fail"
            else: 
                return "Fail"
        except:
            return "Fail"
    
    def close(self):
        self.ftduino.close()
    
