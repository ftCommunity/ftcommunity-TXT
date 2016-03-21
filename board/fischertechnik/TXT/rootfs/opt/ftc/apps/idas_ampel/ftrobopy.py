"""
***********************************************************************
**ftrobopy** - Ansteuerung des fischertechnik TXT Controllers in Python
***********************************************************************
(c) 2016 by Torsten Stuehn
"""

from __future__ import print_function
from os import system
import sys
import socket
import threading
import select
import struct
import time
from math import sqrt

__author__      = "Torsten Stuehn"
__copyright__   = "Copyright 2015, 2016 by Torsten Stuehn"
__credits__     = "fischertechnik GmbH for the excellent TXT hardware"
__license__     = "MIT License"
__version__     = "0.94"
__maintainer__  = "Torsten Stuehn"
__email__       = "stuehn@mailbox.org"
__status__      = "beta"
__date__        = "03/12/2016"

def version():
  """
     Gibt die Versionsnummer des ftrobopy-Moduls zurueck

     :return: Versionsnummer (float)

     Anwendungsbeispiel:

     >>> print("ftrobopy Version ", ftrobopy.ftrobopy.version())
  """
  return __version__


def default_error_handler(message, exception):
  print(message)
  return False


def default_data_handler(ftTXT):
  pass


class ftTXT(object):
  """
    Basisklasse zum fischertechnik TXT Computer.
    Implementiert das Protokoll zum Datenaustausch ueber Unix Sockets.
    Die Methoden dieser Klasse werden typischerweise vom End-User nicht direkt aufgerufen, sondern
    nur indirekt ueber die Methoden der Klasse ftrobopy.ftrobopy, die eine Erweiterung der Klasse ftrobopy.ftTXTBase darstellt.

    Die folgenden Konstanten werden in der Klasse definiert:

        + ``C_VOLTAGE    = 0`` *Zur Verwendung eines Eingangs als Spannungsmesser*
        + ``C_SWITCH     = 1`` *Zur Verwendung eines Eingangs als Taster*
        + ``C_RESISTOR   = 1`` *Zur Verwendung eines Eingangs als Wiederstand, z.B. Photowiederstand*
        + ``C_RESISTOR2  = 2`` *Zur Verwendung eines Eingangs als Wiederstand*
        + ``C_ULTRASONIC = 3`` *Zur Verwendung eines Eingangs als Distanzmesser*
        + ``C_ANALOG     = 0`` *Eingang wird analog verwendet*
        + ``C_DIGITAL    = 1`` *Eingang wird digital verwendet*
        + ``C_OUTPUT     = 0`` *Ausgang (O1-O8) wird zur Ansteuerung z.B. einer Lampe verwendet*
        + ``C_MOTOR      = 1`` *Ausgang (M1-M4) wird zur Ansteuerung eines Motors verwendet*
  """
  
  C_VOLTAGE    = 0
  C_SWITCH     = 1
  C_RESISTOR   = 1
  C_RESISTOR2  = 2
  C_ULTRASONIC = 3
  C_ANALOG     = 0
  C_DIGITAL    = 1
  C_OUTPUT     = 0
  C_MOTOR      = 1

  def __init__(self, host, port, on_error=default_error_handler, on_data=default_data_handler):
    """
      Initialisierung der ftTXT Klasse:

      * Alle Ausgaenge werden per default auf 1 (=Motor) gesetzt
      * Alle Eingaenge werden per default auf 1, 0 (=Taster, digital) gesetzt
      * Alle Zaehler werden auf 0 gesetzt

      :param host: Hostname oder IP-Nummer des TXT Moduls
      :type host: string

      - '127.0.0.1' im Downloadbetrieb
      - '192.168.7.2' im USB Offline-Betrieb
      - '192.168.8.2' im WLAN Offline-Betrieb
      - '192.168.9.2' im Bluetooth Offline-Betreib

      :param port: Portnummer (normalerweise 65000)
      :type port: integer

      :param on_error: Errorhandler fuer Fehler bei der Kommunikation mit dem Controller (optional)
      :type port: function(str, Exception) -> bool


      :return: Leer

      Anwedungsbeispiel:

      >>> import ftrobopy
      >>> txt = ftrobopy.ftTXT('192.168.7.2', 65000)
    """
    self._camera_already_running = False
    self._m_devicename = b''
    self._m_version    = b''
    self._host=host
    self._port=port
    self.handle_error=on_error
    self.handle_data=on_data
    self._sock=socket.socket()
    self._sock.settimeout(5)
    self._sock.connect((self._host, self._port))
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._sock.setblocking(1)
    self._txt_stop_event = threading.Event()
    self._txt_stop_event.set()
    self._exchange_data_lock = threading.RLock()
    self._camera_data_lock   = threading.Lock()
    self._socket_lock  = threading.Lock()
    self._txt_thread = None
    self._update_timer  = time.time()
    self._sound_timer   = self._update_timer
    self._sound_length  = 0
    self._config_id            = 0
    self._m_extension_id       = 0
    self._ftX1_pgm_state_req   = 0
    self._ftX1_old_FtTransfer  = 0
    self._ftX1_dummy           = b'\x00\x00'
    self._ftX1_motor           = [1,1,1,1]
    self._ftX1_uni            = [1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00',
                                 1,1,b'\x00\x00'] 
    self._ftX1_cnt            = [1,b'\x00\x00\x00',
                                 1,b'\x00\x00\x00',
                                 1,b'\x00\x00\x00',
                                 1,b'\x00\x00\x00']
    self._ftX1_motor_config   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    self._exchange_data_lock.acquire()
    self._pwm          = [0,0,0,0,0,0,0,0]
    self._motor_sync   = [0,0,0,0]
    self._motor_dist   = [0,0,0,0]
    self._motor_cmd_id = [0,0,0,0]
    self._last_motor_cmd_id = self._motor_cmd_id
    self._counter      = [0,0,0,0]
    self._sound        = 0
    self._sound_index  = 0
    self._sound_repeat = 0
    self._current_input          = [0,0,0,0,0,0,0,0]
    self._current_counter        = [0,0,0,0]
    self._current_counter_value  = [0,0,0,0]
    self._current_counter_cmd_id = [0,0,0,0]
    self._current_motor_cmd_id   = [0,0,0,0]
    self._current_sound_cmd_id   = 0
    self._current_ir             = range(26)
    self._exchange_data_lock.release() 

  def isOnline(self):
    return (not self._txt_stop_event.isSet()) and (self._txt_thread is not None)

  def queryStatus(self):
    """
       Abfrage des Geraetenamens und der Firmware Versionsnummer des TXT
       Nach dem Umwandeln der Versionsnummer in einen Hexadezimalwert, kann
       die Version direkt abgelesen werden.

       :return: Geraetename (string), Versionsnummer (integer)

       Anwendungsbeispiel:

       >>> name, version = txt.queryStatus()
    """
    m_id         = 0xDC21219A
    m_resp_id    = 0xBAC9723E
    buf          = struct.pack('<I', m_id)
    self._socket_lock.acquire()
    res          = self._sock.send(buf)
    data         = self._sock.recv(512)
    self._socket_lock.release()
    fstr         = '<I16sI'
    response_id  = 0
    if len(data) == struct.calcsize(fstr):
      response_id, m_devicename, m_version = struct.unpack(fstr, data)
    else:
      m_devicename = ''
      m_version    = 0
    if response_id != m_resp_id:
      print('WARNING: ResponseID ', hex(response_id),'of queryStatus command does not match')
    self._m_devicename = m_devicename.decode('utf-8').strip('\x00')
    self._m_version    = m_version
    v1                 = int(hex(m_version)[2])
    v2                 = int(hex(m_version)[3:5])
    v3                 = int(hex(m_version)[5:7])
    self._m_firmware   = 'firmware version '+str(v1)+'.'+str(v2)+'.'+str(v3)
    return m_devicename, m_version

  def getDevicename(self):
    """
       Liefert den zuvor mit queryStatus() ausgelesenen Namen des TXT zurueck

       :return: Geraetename (string)

       Anwendungsbeispiel:

       >>> print('Name des TXT: ', txt.getDevicename())
    """
    return self._m_devicename

  def getVersionNumber(self):
    """
       Liefert die zuvor mit queryStatus() ausgelesene Versionsnummer zurueck.
       Um die Firmwareversion direkt ablesen zu koennen, muss diese Nummer noch in
       einen Hexadezimalwert umgewandelt werden

       :return: Versionsnummer (integer)

       Anwendungsbeispiel:

       >>> print(hex(txt.getVersionNumber()))
    """
    return self._m_version
    
  def getFirmwareVersion(self):
    """
       Liefert die zuvor mit queryStatus() ausgelesene Versionsnummer als
       Zeichenkette (string) zurueck.

       :return: Firmware Versionsnummer (str)

       Anwendungsbeispiel:

       >>> print(txt.getFirmwareVersion())
    """
    return self._m_firmware
    
  def startOnline(self, update_interval=0.01):
    """
       Startet den Onlinebetrieb des TXT und startet einen Python-Thread, der die Verbindung zum TXT aufrecht erhaelt.

       :return: Leer

       Anwendungsbeispiel:

       >>> txt.startOnline()
    """
    if self._txt_stop_event.isSet():
      self._txt_stop_event.clear()
    else:
      return
    if self._txt_thread is None:
      m_id       = 0x163FF61D
      m_resp_id  = 0xCA689F75
      buf        = struct.pack('<I64s', m_id,b'')
      self._socket_lock.acquire()
      res        = self._sock.send(buf)
      data       = self._sock.recv(512)
      self._socket_lock.release()
      fstr       = '<I'
      response_id = 0
      if len(data) == struct.calcsize(fstr):
        response_id, = struct.unpack(fstr, data)
      if response_id != m_resp_id:
        self.handle_error('WARNING: ResponseID %s of startOnline command does not match' % hex(response_id), None)
      else:
        self._txt_thread = ftTXTexchange(txt=self, sleep_between_updates=update_interval, stop_event=self._txt_stop_event)
        self._txt_thread.setDaemon(True)
        self._txt_thread.start()
    return None

  def stopOnline(self):
    """
       Beendet den Onlinebetrieb des TXT und beendet den Python-Thread der fuer den Datenaustausch mit dem TXT verantwortlich war.

       :return: Leer

       Anwendungsbeispiel:

       >>> txt.stopOnline()
    """
    if not self.isOnline():
      return
    self._txt_stop_event.set()
    m_id       = 0x9BE5082C
    m_resp_id  = 0xFBF600D2
    buf        = struct.pack('<I', m_id)
    self._socket_lock.acquire()
    res        = self._sock.send(buf)
    data       = self._sock.recv(512)
    self._socket_lock.release()
    fstr       = '<I'
    response_id = 0
    if len(data) == struct.calcsize(fstr):
      response_id, = struct.unpack(fstr, data)
    if response_id != m_resp_id:
      self.handle_error('WARNING: ResponseID %s of stopOnline command does not match' % hex(response_id), None)
    self._txt_thread = None
    return None

  def setConfig(self, M, I):
    """
       Einstellung der Konfiguration der Ein- und Ausgaenge des TXT.
       Diese Funktion setzt nur die entsprechenden Werte in der ftTXT-Klasse.
       Zur Uebermittlung der Werte an den TXT wird die updateConfig-Methode verwendet.

       :param M: Konfiguration der 4 Motorausgaenge (0=einfacher Ausgang, 1=Motorausgang)
       :type M: int[4]

       - Wert=0: Nutzung der beiden Ausgaenge als einfache Outputs
       - Wert=1: Nutzung der beiden Ausgaenge als Motorausgang (links-rechts-Lauf)

       :param I: Konfiguration der 8 Eingaenge
       :type I: int[8][2]

       :return: Leer

       Anwendungsbeispiel:

       - Konfiguration der Ausgaenge M1 und M2 als Motorausgaenge
       - Konfiguration der Ausgaenge O5/O6 und O7/O8 als einfache Ausgaenge


       - Konfiguration der Eingaenge I1, I2, I6, I7, I8 als Taster
       - Konfiguration des Eingangs I3 als Ultraschall Entfernungsmesser
       - Konfiguration des Eingangs I4 als analoger Spannungsmesser
       - Konfiguration des Eingangs I5 als analoger Widerstandsmesser

       >>> M = [txt.C_MOTOR, txt.C_MOTOR, txt.C_OUTPUT, txt.C_OUTPUT]
       >>> I = [(txt.C_SWITCH,     txt.C_DIGITAL),
                (txt.C_SWITCH,     txt.C_DIGITAL),
                (txt.C_ULTRASONIC, txt.C_ANALOG),
                (txt.C_VOLTAGE,    txt.C_ANALOG),
                (txt.C_RESISTOR,   txt.C_ANALOG),
                (txt.C_SWITCH,     txt.C_DIGITAL),
                (txt.C_SWITCH,     txt.C_DIGITAL),
                (txt.C_SWITCH,     txt.C_DIGITAL)]
       >>> txt.setConfig(M, I)
       >>> txt.updateConfig()
    """
    m_id       = 0x060EF27E
    m_resp_id  = 0x9689A68C
    self._config_id += 1
    # Configuration of motors
    # 0=single output O1/O2
    # 1=motor output M1
    # self.ftX1_motor          = [M[0],M[1],M[2],M[3]]  # BOOL8[4]
    self._ftX1_motor            = M
    # Universal input mode, see enum InputMode:
    # MODE_U=0
    # MODE_R=1
    # MODE_R2=2
    # MODE_ULTRASONIC=3
    # MODE_INVALID=4
    # print("setConfig I=", I)
    self._ftX1_uni           = [I[0][0],I[0][1],b'\x00\x00',
                                I[1][0],I[1][1],b'\x00\x00',
                                I[2][0],I[2][1],b'\x00\x00',
                                I[3][0],I[3][1],b'\x00\x00',
                                I[4][0],I[4][1],b'\x00\x00',
                                I[5][0],I[5][1],b'\x00\x00',
                                I[6][0],I[6][1],b'\x00\x00',
                                I[7][0],I[7][1],b'\x00\x00'] 
    return None

  def getConfig(self):
    """
       Abfrage der aktuellen Konfiguration des TXT

       :return: M[4], I[8][2]
       :rtype: M:int[4], I:int[8][2]

       Anwendungsbeispiel: Aenderung des Eingangs I2 auf analoge Ultraschall Distanzmessung

       - Hinweis: Feldelemente werden in Python typischerweise durch die Indizes 0 bis N-1 angesprochen
       - Der Eingang I2 des TXT wird in diesem Beispiel ueber das Feldelement I[1] angesprochen

       >>> M, I = txt.getConfig()
       >>> I[1] = (txt.C_ULTRASONIC, txt.C_ANALOG)
       >>> txt.setConfig(M, I)
       >>> txt.updateConfig()
    """
    m  = self._ftX1_motor
    i  = self._ftX1_uni
    ii = [(i[0], i[1]), (i[3], i[4]),(i[6], i[7]),(i[9], i[10]),(i[12], i[13]),(i[15], i[16]),(i[18], i[19]),(i[21], i[22]) ]
    return m, ii 

  def updateConfig(self):
    """
       Uebertragung der Konfigurationsdaten fuer die Ein- und Ausgaenge zum TXT

       :return: Leer

       Anwendungsbeispiel:

       >>> txt.setConfig(M, I)
       >>> txt.updateConfig()
    """
    if not self.isOnline():
      self.handle_error("Controller must be online before updateConfig() is called", None)
      return
    m_id       = 0x060EF27E
    m_resp_id  = 0x9689A68C
    self._config_id += 1
    fields = [m_id, self._config_id, self._m_extension_id]
    fields.append(self._ftX1_pgm_state_req)
    fields.append(self._ftX1_old_FtTransfer)
    fields.append(self._ftX1_dummy)
    fields += self._ftX1_motor
    fields += self._ftX1_uni
    fields += self._ftX1_cnt
    fields += self._ftX1_motor_config
    buf = struct.pack('<Ihh B B 2s BBBB BB2s BB2s BB2s BB2s BB2s BB2s BB2s BB2s B3s B3s B3s B3s 16h', *fields)
    self._socket_lock.acquire()
    res = self._sock.send(buf)
    data = self._sock.recv(512)
    self._socket_lock.release()
    fstr    = '<I'
    response_id = 0
    if len(data) == struct.calcsize(fstr):
      response_id, = struct.unpack(fstr, data)
    if response_id != m_resp_id:
      self.handle_error('WARNING: ResponseID %s of updateConfig command does not match' % hex(response_id), None)
      self._txt_stop_event.set()  # Stop the data exchange thread if we were online
    return None

  def startCameraOnline(self):
    """
      Startet den Prozess auf dem TXT, der das aktuelle Camerabild ueber Port 65001 ausgibt und startet einen Python-Thread,
      der die Cameraframes kontinuierlich vom TXT abholt. Die Frames werden vom TXT im jpeg-Format angeliefert.
      Es wird nur das jeweils neueste Bild aufgehoben.

      Nach dem Starten des Cameraprozesses auf dem TXT vergehen bis zu 2 Sekunden, bis des erste Bild vom TXT gesendet wird.

      Anwendungsbeispiel:

      Startet den Cameraprozess, wartet 2.5 Sekunden und speichert das eingelesene Bild als Datei 'txtimg.jpg' ab.

      >>> txt.startCameraOnline()
      >>> time.sleep(2.5)
      >>> pic = None
      >>> while pic == None:
      >>>   pic = txt.getCameraFrame()
      >>> f=open('txtimg.jpg','w')
      >>> f.write(''.join(pic))
      >>> f.close()
    """
    if self._camera_already_running:
      print("Camera is already running")
      return
    self._camera_already_running = True
    m_id                 = 0x882A40A6
    m_resp_id            = 0xCF41B24E
    self._m_width         = 320
    self._m_height        = 240
    self._m_framerate     = 15
    self._m_powerlinefreq = 0 # 0=auto, 1=50Hz, 2=60Hz
    buf        = struct.pack('<I4i', m_id,
                                     self._m_width,
                                     self._m_height,
                                     self._m_framerate,
                                     self._m_powerlinefreq)
    self._socket_lock.acquire()
    res        = self._sock.send(buf)
    data       = self._sock.recv(512)
    self._socket_lock.release()
    fstr       = '<I'
    response_id = 0
    if len(data) == struct.calcsize(fstr):
      response_id, = struct.unpack(fstr, data)
    if response_id != m_resp_id:
      print('WARNING: ResponseID ', hex(response_id),' of startCameraOnline command does not match')
    self._camera_stop_event = threading.Event()
    self._camera_thread = camera(self._host, self._port+1, self._camera_data_lock, self._camera_stop_event)
    self._camera_thread.setDaemon(True)
    self._camera_thread.start()
    return

  def stopCameraOnline(self):
    """
      Beendet den lokalen Python-Camera-Thread und den Camera-Prozess auf dem TXT.

      Anwendungsbeispiel:

      >>> txt.stopCameraOnline()

    """
    if not self._camera_already_running:
      return None
    self._camera_stop_event.set()
    m_id                 = 0x17C31F2F
    m_resp_id            = 0x4B3C1EB6
    buf        = struct.pack('<I', m_id)
    self._socket_lock.acquire()
    res        = self._sock.send(buf)
    data       = self._sock.recv(512)
    self._socket_lock.release()
    fstr       = '<I4'
    response_id = 0
    if len(data) == struct.calcsize(fstr):
      response_id, = struct.unpack(fstr, data)
    if response_id != m_resp_id:
      print('WARNING: ResponseID ', hex(response_id),' of stopCameraOnline command does not match')
    self._camera_already_running = False
    return

  def getCameraFrame(self):
    """
      Diese Funktion liefert das aktuelle Camerabild des TXT zurueck (im jpeg-Format).
      Der Camera-Prozess auf dem TXT muss dafuer vorher gestartet worden sein.

      Anwendungsbeispiel:

      >>>   pic = txt.getCameraFrame()

      :return: jpeg Bild
    """
    if self._camera_already_running:
      return self._camera_thread.getCameraFrame()
    else:
      return None

  def sleep(self, seconds):
    """
    Dieser Befehl wird nicht mehr benoetigt und ist nur noch aus kompatibilitaetsgruenden vorhanden.
    Die Kommunikation zum TXT ist inzwischen ueber Thread-Prozesse implementiert.
    Anstelle dieses Befehls sollte die Python-Methode time.sleep() aus dem Time-Modul verwendet werden
    """
    print("Anstelle des sleep-Befehls sollte die Methode time.sleep() aus dem Time-Modul verwendet werden.")


  def incrMotorCmdId(self, idx):
    """
      Erhoehung der sog. Motor Command ID um 1.

      Diese Methode muss immer dann aufgerufen werden, wenn die Distanzeinstellung eines Motors (gemessen ueber die 4 schnellen Counter-Eingaenge)
      geaendert wurde oder wenn ein Motor mit einem anderen Motor synchronisiert werden soll. Falls nur die Motorgeschwindigkeit veraendert wurde,
      ist der Aufruf der incrMotorCmdId()-Methode nicht notwendig.

      :param idx: Nummer des Motorausgangs
      :type idx: integer

      Achtung:

      * Die Zaehlung erfolgt hier von 0 bis 3, idx=0 entspricht dem Motorausgang M1 und idx=3 entspricht dem Motorausgang M4

      Anwendungsbeispiel:

      Der Motor, der am TXT-Anschluss M2 angeschlossen ist, soll eine Distanz von 200 (Counterzaehlungen) zuruecklegen.

      >>> txt.setMotorDistance(1, 200)
      >>> txt.incrMotorCmdId(1)
    """
    self._exchange_data_lock.acquire()
    self._motor_cmd_id[idx] += 1
    if self._motor_cmd_id[idx] >= 32768:
      self._motor_cmd_id[idx] = 0
    self._exchange_data_lock.release()
    return None

  def getMotorCmdId(self, idx=None):
    """
      Liefert die letzte Motor Command ID eines Motorausgangs (oder aller Motorausgaenge als array) zurueck.

      :param idx: Nummer des Motorausgangs. Falls dieser Parameter nicht angeben wird, wird die Motor Command ID aller Motorausgaenge als Array[4] zurueckgeliefert.
      :type idx: integer

      :return: Die Motor Command ID eines oder aller Motorausgaenge
      :rtype: integer oder integer[4] array

      Anwendungsbeispiel:

      >>> letzte_cmd_id = txt.getMotorCmdId(4)
    """
    if idx != None:
      ret=self._motor_cmd_id[idx]
    else:
      ret=self._motor_cmd_id
    return ret

  def cameraOnline(self):
    """
      Mit diesem Befehl kann abgefragt werden, ob der Camera-Prozess gestartet wurde

      :return:
      :rtype: boolean
    """
    return self._camera_online

  def getSoundCmdId(self):
    """
      Liefert die letzte Sound Command ID zurueck.

      :return: Letzte Sound Command ID
      :rtype: integer

      Anwendungsbeispiel:

      >>> last_sound_cmd_id = txt.getSoundCmdId()
    """
    return self._sound

  def incrCounterCmdId(self, idx):
    """
      Erhoehung der Counter Command ID um eins.
      Falls die Counter Command ID eines Counters um eins erhoeht wird, wird der entsprechende Counter zurueck auf 0 gesetzt.

      :param idx: Nummer des schnellen Countereingangs, dessen Command ID erhoeht werden soll. (Hinweis: die Zaehlung erfolgt hier von 0 bis 3 fuer die Counter C1 bis C4)
      :type idx: integer

      :return: Leer

      Anwendungsbeispiel:

      Erhoehung der Counter Command ID des Counters C4 um eins.

      >>> txt.incrCounterCmdId(3)
    """
    self._exchange_data_lock.acquire()
    self._counter[idx] += 1
    self._exchange_data_lock.release()
    return None

  def incrSoundCmdId(self):
    """
      Erhoehung der Sound Command ID um eins.
      Die Sound Command ID muss immer dann um eins erhoeht werden, falls ein neuer Sound gespielt werden soll oder
      wenn die Wiederholungsanzahl eines Sounds veraendert wurde. Falls kein neuer Sound index gewaehlt wurde und auch
      die Wiederholungsrate nicht veraendert wurde, wird der aktuelle Sound erneut abgespielt.

      :return: Leer

      Anwendungsbeispiel:

      >>> txt.incrSoundCmdId()
    """
    self._exchange_data_lock.acquire()
    self._sound += 1
    self._exchange_data_lock.release()
    return None

  def setSoundIndex(self, idx):
    """
      Einstellen eines neuen Sounds.

      :param idx: Nummer des neuen Sounds (0=Kein Sound, 1-29 Sounds des TXT)
      :type idx: integer

      :return: Leer

      Anwendungsbeispiel:

      Sound "Augenzwinkern" einstellen und 2 mal abspielen.

      >>> txt.setSoundIndex(26)
      >>> txt.setSoundRepeat(2)
      >>> txt.incrSoundCmdId()
    """
    self._exchange_data_lock.acquire()
    self._sound_index = idx
    self._exchange_data_lock.release()
    return None

  def getSoundIndex(self):
    """
      Liefert die Nummer des aktuell eingestellten Sounds zurueck.

      :return: Nummer des aktuell eingestellten Sounds
      :rtype: integer

      Anwendungsbeispiel:

      >>> aktueller_sound = txt.getSoundIndex()
    """
    return self._sound_index

  def setSoundRepeat(self, rep):
    """
      Einstellen der Anzahl der Wiederholungen eines Sounds.

      :param rep: Anzahl der Wiederholungen (0=unendlich oft wiederholen)
      :type rep: integer

      Anwendungsbeispiel:

      "Motor-Sound" unendlich oft (d.h. bis zum Ende des Programmes oder bis zur naechsten Aenderung der Anzahl der Wiederholungen) abspielen.

      >>> txt.setSound(19) # 19=Motor-Sound
      >>> txt.setSoundRepeat(0)
    """
    self._exchange_data_lock.acquire()
    self._sound_repeat = rep
    self._exchange_data_lock.release()
    return None

  def getSoundRepeat(self):
    """
      Liefert die aktuell eingestellte Wiederholungs-Anzahl des Sounds zurueck.

      :return: Aktuell eingestellte Wiederholungs-Anzahl des Sounds.
      :rtype: integer

      Anwendungsbeispiel:

      >>> repeat_rate = txt.getSoundRepeat()
    """
    return self._sound_repeat

  def getCounterCmdId(self, idx=None):
    """
      Liefert die letzte Counter Command ID eines (schnellen) Counters zurueck

      :param idx: Nummer des Counters. (Hinweis: die Zaehlung erfolgt hier von 0 bis 3 fuer die Counter C1 bis C4)

      Anwendungsbeispiel:

      Counter Command ID des schnellen Counters C3 in Variable num einlesen.

      >>> num = txt.getCounterCmdId(2)
    """
    if idx != None:
      ret=self._counter[idx]
    else:
      ret=self._counter
    return ret

  def setPwm(self, idx, value):
    """
      Einstellen des Ausgangswertes fuer einen Motor- oder Output-Ausgang. Typischerweise wird diese Funktion nicht direkt aufgerufen,
      sondern von abgeleiteten Klassen zum setzen der Ausgangswerte verwendet.
      Ausnahme: mit Hilfe dieser Funktionen koennen Ausgaenge schnell auf 0 gesetzt werden um z.B. einen Notaus zu realisieren (siehe auch stopAll)

      :param idx: Nummer des Ausgangs. (Hinweis: die Zaehlung erfolgt hier von 0 bis 7 fuer die Ausgaenge O1-O8)
      :type idx: integer (0-7)

      :param value: Wert, auf den der Ausgang gesetzt werden soll (0:Ausgang ausgeschaltet, 512: Ausgang auf maximum)
      :type value: integer (0-512)

      :return: Leer

      Anwendungsbeispiel:

      * Motor am Anschluss M1 soll mit voller Geschwindigkeit Rueckwaerts laufen.
      * Lampe am Anschluss O3 soll mit halber Leuchtkraft leuchten.

      >>> txt.setPwm(0,0)
      >>> txt.setPwm(1,512)
      >>> txt.setPwm(2,256)
    """
    self._exchange_data_lock.acquire()
    self._pwm[idx]=value
    self._exchange_data_lock.release()
    return None

  def stopAll(self):
    """
    Setzt alle Ausgaenge auf 0 und stoppt damit alle Motoren und schaltet alle Lampen aus.

    :return:
    """
    for i in range(8):
      self.setPwm(i, 0)
    return

  def getPwm(self, idx=None):
    """
      Liefert die zuletzt eingestellten Werte der Ausgaenge O1-O8 (als array[8]) oder den Wert eines Ausgangs.

      :param idx:
      :type idx: integer oder None, bzw. leer

      - Wenn kein idx-Parameter angegeben wurde, werden alle Pwm-Einstellungen als array[8] zurueckgeliefert.
      - Ansonsten wird nur der Pwm-Wert des mit idx spezifizierten Ausgangs zurueckgeliefert.

      Hinweis: der idx-Parameter wird angeben von 0 bis 7 fuer die Ausgaenge O1-O8

      :return: der durch (idx+1) spezifizierte Ausgang O1 bis O8 oder das gesamte Pwm-Array
      :rtype: integer oder integer array[8]

      Anwendungsbeispiel:

      Liefert die

      >>> M1_a = txt.getPwm(0)
      >>> M1_b = txt.getPwm(1)
      >>> if M1_a > 0 and M1_b == 0:
            print("Geschwindigkeit Motor M1: ", M1_a, " (vorwaerts).")
          else:
            if M1_a == and M1_b > 0:
              print("Geschwindigkeit Motor M1: ", M1_b, " (rueckwaerts).")
    """
    if idx != None:
      ret=self._pwm[idx]
    else:
      ret=self._pwm
    return ret

  def setMotorSyncMaster(self, idx, value):
    """
      Hiermit koennen zwei Motoren miteinander synchronisiert werden, z.B. fuer perfekten Geradeauslauf.

      :param idx: Der Motorausgang, der synchronisiert werden soll
      :type idx: integer

      :param value: Die Numer des Motorausgangs, mit dem synchronisiert werden soll.
      :type value: integer

      :return: Leer

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Motor-Ausgaenge M1 bis M4.
      - der value-PArameter wird angeben von 1 bis 4 fuer die Motor-Ausgaenge M1 bis M4.

      Anwendungsbeispiel:

      Die Motorausgaenge M1 und M2 werden synchronisiert.
      Um die Synchronisations-Befehle abzuschliessen, muss ausserdem die MotorCmdId der Motoren erhoeht werden.

      >>> txt.setMotorSyncMaster(0, 2)
      >>> txt.setMotorSyncMaster(1, 1)
      >>> txt.incrMotorCmdId(0)
      >>> txt.incrMotorCmdId(1)
    """
    self._exchange_data_lock.acquire()
    self._motor_sync[idx]=value
    self._exchange_data_lock.release()
    return None

  def getMotorSyncMaster(self, idx=None):
    """
      Liefert die zuletzt eingestellte Konfiguration der Motorsynchronisation fuer einen oder alle Motoren zurueck.

      :param idx: Die Nummer des Motors, dessen Synchronisation geliefert werden soll oder None oder <leer> fuer alle Ausgaenge.
      :type idx: integer

      :return: Leer

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Motor-Ausgaenge M1 bis M4.
      - oder None oder <leer> fuer alle Motor-Ausgaenge.

      Anwendungsbeispiel:

      >>> xm = txt.getMotorSyncMaster()
      >>> print("Aktuelle Konfiguration aller Motorsynchronisationen: ", xm)
    """
    if idx != None:
      ret=self._motor_sync[idx]
    else:
      ret=self._motor_sync
    return ret

  def setMotorDistance(self, idx, value):
    """
      Hiermit kann die Distanz (als Anzahl von schnellen Counter-Zaehlungen) fuer einen Motor eingestellt werden.

      :param idx: Nummer des Motorausgangs
      :type idx: integer

      :return: Leer

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Motor-Ausgaenge M1 bis M4.

      Anwendungsbeispiel:

      Der Motor an Ausgang M3 soll 100 Counter-Zaehlungen lang drehen.
      Um den Distanz-Befehl abzuschliessen, muss ausserdem die MotorCmdId des Motors erhoeht werden.

      >>> txt.setMotorDistance(2, 100)
      >>> txt.incrMotorCmdId(2)
    """
    self._exchange_data_lock.acquire()
    self._motor_dist[idx]=value
    self._exchange_data_lock.release()
    return None

  def getMotorDistance(self, idx=None):
    """
      Liefert die zuletzt eingestellte Motordistanz fuer einen oder alle Motorausgaenge zurueck.

      :param idx: Nummer des Motorausgangs
      :type idx: integer

      :return: Letzte eingestellte Distanz eines Motors (idx=0-3) oder alle zuletzt eingestellten Distanzen (idx=None oder kein idx-Parameter angegeben)

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Motor-Ausgaenge M1 bis M4.

      Anwendungsbeispiel:

      >>> md = txt.getMotorDistance(1)
      >>> print("Mit setMotorDistance() eingestellte Distanz fuer M2: ", md)
    """
    if idx != None:
      ret=self._motor_dist[idx]
    else:
      ret=self._motor_dist
    return ret

  def getCurrentInput(self, idx=None):
    """
       Liefert den aktuellen vom TXT zurueckgelieferten Wert eines Eingangs oder aller Eingaenge als Array

       :param idx: Nummer des Eingangs
       :type idx: integer

       :return: Aktueller Wert eines Eingangs (idx=0-7) oder alle aktuellen Eingangswerte des TXT-Controllers als Array[8] (idx=None oder kein idx angegeben)

       Hinweis:

       - der idx-Parameter wird angeben von 0 bis 7 fuer die Eingaenge I1 bis I8.

       Anwendungsbeispiel:

       >>> print("Der aktuelle Wert des Eingangs I4 ist: ", txt.getCurrentInput(3))
    """
    self._exchange_data_lock.acquire()
    if idx != None:
      ret=self._current_input[idx]
    else:
      ret=self._current_input
    self._exchange_data_lock.release()
    return ret

  def getCurrentCounterInput(self, idx=None):
    """
      Zeigt an, ob ein Counter oder alle Counter (als Array[4]) sich seit der letzten Abfrage veraendert haben.

      :param idx: Nummer des Counters
      :type idx: integer

      :return: Aktueller Status-Wert eines Counters (idx=0-3) oder aller schnellen Counter des TXT-Controllers als Array[4] (idx=None oder kein idx angegeben)

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Counter C1 bis C4.

      Anwendungsbeispiel:

      >>> c = txt.getCurrentCounterInput(0)
      >>> if c==0:
      >>>   print("Counter C1 hat sich seit der letzten Abfrage nicht veraendert")
      >>> else:
      >>>   print("Counter C1 hat sich seit der letzten Abfrage veraendert")
    """
    self._exchange_data_lock.acquire()
    if idx != None:
      ret=self._current_counter[idx]
    else:
      ret=self._current_counter
    self._exchange_data_lock.release()
    return ret

  def getCurrentCounterValue(self, idx=None):
    """
      Liefert den aktuellen Wert eines oder aller schnellen Counter Eingaenge zurueck.
      Damit kann z.B. nachgeschaut werden, wie weit ein Motor schon gefahren ist.

      :param idx: Nummer des Counters
      :type idx: integer

      :return: Aktueller Wert eines Counters (idx=0-3) oder aller schnellen Counter des TXT-Controllers als Array[4] (idx=None oder kein idx angegeben)

      Hinweis:

      - der idx-Parameter wird angegeben von 0 bis 3 fuer die Counter C1 bis C4.

      Anwendungsbeispiel:

      >>> print("Aktueller Wert von C1: ", txt.getCurrentCounterValue(0)
    """
    self._exchange_data_lock.acquire()
    if idx != None:
      ret=self._current_counter_value[idx]
    else:
      ret=self._current_counter_value
    self._exchange_data_lock.release()
    return ret

  def getCurrentCounterCmdId(self, idx=None):
    """
      Liefert die aktuelle Counter Command ID eines oder aller Counter zurueck.

      :param idx: Nummer des Counters
      :type idx: integer

      :return: Aktuelle Commmand ID eines Counters (idx=0-3) oder aller Counter des TXT-Controllers als Array[4] (idx=None oder kein idx angegeben)

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Counter C1 bis C4.

      Anwendungsbeispiel:

      >>> cid = txt.getCurrentCounterCmdId(3)
      >>> print("Aktuelle Counter Command ID von C4: ", cid)
    """
    self._exchange_data_lock.acquire()
    if idx != None:
      ret=self._current_counter_cmd_id[idx]
    else:
      ret=self._current_counter_cmd_id
    self._exchange_data_lock.release()
    return ret

  def getCurrentMotorCmdId(self, idx=None):
    """
      Liefert die aktuelle Motor Command ID eines oder aller Motoren zurueck.

      :param idx: Nummer des Motors
      :type idx: integer

      :return: Aktuelle Commmand ID eines Motors (idx=0-3) oder aller Motoren des TXT-Controllers als Array[4] (idx=None oder kein idx angegeben)

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 3 fuer die Motoren M1 bis M4.

      Anwendungsbeispiel:

      >>> print("Aktuelle Motor Command ID von M4: ", txt.getCurrentMotorCmdId(3))
    """
    self._exchange_data_lock.acquire()
    if idx != None:
      ret=self._current_motor_cmd_id[idx]
    else:
      ret=self._current_motor_cmd_id
    self._exchange_data_lock.release()
    return ret

  def getCurrentSoundCmdId(self):
    """
      Liefert die aktuelle Sound Command ID zurueck.

      :return: Die aktuelle Sound Command ID
      :rtype: integer

      Anwendungsbeispiel:

      >>> print("Die aktuelle Sound Command ID ist: ", txt.getCurrentSoundCmdId())
    """
    self._exchange_data_lock.acquire()
    ret=self._current_sound_cmd_id
    self._exchange_data_lock.release()
    return ret

  def getCurrentIr(self):
    """
      Liefert die aktuellen Werte der Infrarot Fernsteuerung zurueck (als Array oder als einzelnen Wert)

      Die Werte werden fuer jede einzelne Einstellung der DIP-Switche auf der IR-Fernsteuerung zurueckgeliefert,
      so dass insgesamt 4 Fernsteuerungen abgefragt werden koennen (als Python-Liste von Python-Listen).
      Die 5. Liste innerhalb der Python-Liste gibt den Zustand einer Fernsteuerung mit beliebiger DIP-Switch-Einstellung zurueck.
      Die Einstellung der Switche selbst wird auch zurueckgelifert, aber nicht, wenn wenn die Switche sich aendern, sondern nur, wenn einer der anderen Werte sich aendert.

      :param idx: Nummer des IR Eingangs
      :type idx: integer

      :return: Aktueller Wert eines IR Eingangs (idx=0-5) oder aller IR Eingaenge des TXT-Controllers als Array[5] (idx=None oder kein idx angegeben)

      Hinweis:

      - der idx-Parameter wird angeben von 0 bis 5 fuer die einzelnen Listen innerhalb der Liste.

      Anwendungsbeispiel:

      >>> print("Aktuelle Werte der IR Fernsteuerung: ", txt.getCurrentIr())
    """
    self._exchange_data_lock.acquire()
    ret=self._current_ir
    self._exchange_data_lock.release()
    return ret

  def getHost(self):
    """
    Liefert die aktuelle Netzwerk-Einstellung (typischerweise die IP-Adresse des TXT) zurueck.
    :return: Host-Adresse
    :rtype: string
    """
    return self._host

  def getPort(self):
    """
    Liefert die den aktuellen Netzwerkport zum TXT zurueck (normalerweise 65000).
    :return: Netzwerkport
    :rtype: int
    """
    return self._port

  def SyncDataBegin(self):
    """
      Die Funktionen SyncDataBegin() und SyncDataEnd()  werden verwendet um eine ganze Gruppe von Befehlen gleichzeitig ausfuehren zu koennen.

      Anwendungsbeispiel:

      Die drei Ausgaenge motor1, motor2 und lampe1 werden gleichzeitig aktiviert.

      >>> SyncDataBegin()
      >>> motor1.setSpeed(512)
      >>> motor2.setSpeed(512)
      >>> lampe1.setLevel(512)
      >>> SyncDataEnd()
    """
    self._exchange_data_lock.acquire()

  def SyncDataEnd(self):
    """
      Die Funktionen SyncDataBegin() und SyncDataEnd()  werden verwendet um eine ganze Gruppe von Befehlen gleichzeitig ausfuehren zu koennen.

      Anwendungsbeispiel siehe SyncDataBegin()
    """
    self._exchange_data_lock.release()

class ftTXTexchange(threading.Thread):
  """
  Thread zum kontinuierlichen Datenaustausch zwischen TXT und einem Computer
  sleep_between_updates ist die Zeit, die zwischen zwei Datenaustauschprozessen gewartet wird.
  Der TXT kann im schnellsten Falle alle 20 ms Daten austauschen.
  Typischerweise wird diese Thread-Klasse vom Endanwender nicht direkt verwendet.
  """
  def __init__(self, txt, sleep_between_updates, stop_event):
    threading.Thread.__init__(self)
    self._txt                       = txt
    self._txt_sleep_between_updates = sleep_between_updates
    self._txt_stop_event            = stop_event
    self._txt_interval_timer        = time.time()
    return

  def run(self):
    while not self._txt_stop_event.is_set():
      try:
        if (self._txt_sleep_between_updates > 0):
          time.sleep(self._txt_sleep_between_updates)
        exchange_ok = False
        m_id          = 0xCC3597BA
        m_resp_id     = 0x4EEFAC41
        self._txt._exchange_data_lock.acquire()
        fields  = [m_id]
        fields += self._txt._pwm
        fields += self._txt._motor_sync
        fields += self._txt._motor_dist
        fields += self._txt._motor_cmd_id
        fields += self._txt._counter
        fields += [self._txt._sound, self._txt._sound_index, self._txt._sound_repeat,0,0]
        self._txt._exchange_data_lock.release()
        buf = struct.pack('<I8h4h4h4h4hHHHbb', *fields)
        self._txt._socket_lock.acquire()
        res = self._txt._sock.send(buf)
        data = self._txt._sock.recv(512)
        self._txt._update_timer = time.time()
        self._txt._socket_lock.release()
        fstr    = '<I8h4h4h4h4hH4bB4bB4bB4bB4bBb'
        response_id = 0
        if len(data) == struct.calcsize(fstr):
          response = struct.unpack(fstr, data)
        else:
          print('Received data size (', len(data),') does not match length of format string (',struct.calcsize(fstr),')')
          print('Connection to TXT aborted')
          self._txt_stop_event.set()
          return
        response_id = response[0]
        if response_id != m_resp_id:
          print('ResponseID ', hex(response_id),' of exchangeData command in exchange thread does not match')
          print('Connection to TXT aborted')
          self._txt_stop_event.set()
          return
        self._txt._exchange_data_lock.acquire()
        self._txt._current_input          = response[1:9]
        self._txt._current_counter        = response[9:13]
        self._txt._current_counter_value  = response[13:17]
        self._txt._current_counter_cmd_id = response[17:21]
        self._txt._current_motor_cmd_id   = response[21:25]
        self._txt._current_sound_cmd_id   = response[25]
        self._txt._current_ir             = response[26:52]
        self._txt.handle_data(self._txt)
        self._txt._exchange_data_lock.release()
      except Exception as err:
        self._txt.handle_error('Network error', err)
        self._txt_stop_event.set()
        return
    return

class camera(threading.Thread):
  """
  Hintergrund-Prozess, der den Daten(Bilder)-Stream der TXT-Camera kontinuierlich empfaengt
  Typischerweise wird diese Thread-Klasse vom Endanwender nicht direkt verwendet.
  """
  def __init__(self, host, port, lock, stop_event):
    threading.Thread.__init__(self)
    self._camera_host           = host
    self._camera_port           = port
    self._camera_stop_event     = stop_event
    self._thread_first_start    = True
    self._camera_data_lock      = lock
    self._m_numframesready      = 0
    self._m_framewidth          = 0
    self._m_frameheight         = 0
    self._m_framesizeraw        = 0
    self._m_framesizecompressed = 0
    self._m_framedata           = []
    return

  def run(self):
    if self._thread_first_start:
      self._camera_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self._camera_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self._camera_sock.setblocking(1)
      self._total_bytes_read = 0
      camera_ready = False
      fault_count  = 0
      while not camera_ready:
        time.sleep(0.02)
        try:
          self._camera_sock.connect((self._camera_host, self._camera_port))
          camera_ready = True
        except:
          fault_count += 1
        if fault_count > 150:
          camera_ready = True
          self._camera_stop_event.set()
          print('Camera not connected')
      self._thread_first_start = False
      if not self._camera_stop_event.is_set():
        print('Camera connected')
    while not self._camera_stop_event.is_set():
      try:
        m_id     = 0xBDC2D7A1
        m_ack_id = 0xADA09FBA
        fstr       = '<Iihhii'
        ds_size    = struct.calcsize(fstr) # data struct size without jpeg data
        data = self._camera_sock.recv(ds_size)
        data_size  = len(data)
        if data_size > 0:
          self._total_bytes_read += data_size
          if self._total_bytes_read == ds_size:
            response = struct.unpack(fstr, data)
            if response[0] != m_id:
              print('WARNING: ResponseID ', hex(response[0]),' of cameraOnlineFrame command does not match')
            self._m_numframesready      = response[1]
            self._m_framewidth          = response[2]
            self._m_frameheight         = response[3]
            self._m_framesizeraw        = response[4]
            self._m_framesizecompressed = response[5]
            self._m_framedata           = []
            m_framedata_part = []
            fdatacount = 0
            while len(data) > 0 and self._total_bytes_read < ds_size + self._m_framesizecompressed:
              data = self._camera_sock.recv(1500)
              m_framedata_part[fdatacount:] = data[:]
              fdatacount += len(data)
              self._total_bytes_read += len(data)
            self._camera_data_lock.acquire()
            self._m_framedata[:] = m_framedata_part[:]
            self._camera_data_lock.release()
            if len(data) == 0:
              print('WARNING: Connection to camera lost')
              self._camera_stop_event.set()
            if self._total_bytes_read == ds_size + self._m_framesizecompressed:
              buf  = struct.pack('<I', m_ack_id)
              res  = self._camera_sock.send(buf)
            self._total_bytes_read = 0
        else:
          self._camera_stop_event.set()
      except:
        self._camera_sock.close()
        return
    self._camera_sock.close()
    return

  def getCameraFrame(self):
    """
    Liefert das letzte von der TXT-Camera empfangene Bild zurueck

    :return: Bild der TXT Camera
    :rtype: jpeg Bild

    Anwendungsbeispiel:

    >>> pic = txt.getCameraFrame()
    """
    data = []
    self._camera_data_lock.acquire()
    data[:] = self._m_framedata[:]
    self._camera_data_lock.release()
    return data

class ftrobopy(ftTXT):
  """
    Erweiterung der Klasse ftrobopy.ftTXT. In dieser Klasse werden verschiedene fischertechnik Elemente
    auf einer hoeheren Abstraktionsstufe (aehnlich den Programmelementen aus der ROBOPro Software) fuer den End-User zur Verfuegung gestellt.
    Derzeit sind die folgenden Programmelemente implementiert:
    
    * **motor**, zur Ansteuerung der Motorausgaenge M1-M4
    * **output**, zur Ansteuerung der universellen Ausgaenge O1-O8
    * **input**, zum Einlesen von Werten der Eingaenge I1-I8
    * **ultrasonic**, zur Bestimmung von Distanzen mit Hilfe des Ultraschall Moduls
    
    Ausserdem werden die folgenden Sound-Routinen zur Verfuegung gestellt:
    
    * **play_sound**
    * **stop_sound**
    * **sound_finished**
    
  """
  def __init__(self, host, port, update_interval=0.01):
    """
      Initialisierung der ftrobopy Klasse:
      
      * Aufbau der Socket-Verbindung zum TXT Controller mit Hilfe der Basisklasse ftTXT und Abfrage des Geraetenamens und der Firmwareversionsnummer
      * Initialisierung aller Datenfelder der ftTXT Klasse mit Defaultwerten und Setzen aller Ausgaenge des TXT auf 0
      * Starten eines Python-Hintergrundthreads der die Kommunikation mit dem TXT aufrechterhaelt

      :param host: Hostname oder IP-Nummer des TXT Moduls
      :type host: string
      
      - '127.0.0.1' im Downloadbetrieb
      - '192.168.7.2' im USB Offline-Betrieb
      - '192.168.8.2' im WLAN Offline-Betrieb
      - '192.168.9.2' im Bluetooth Offline-Betreib
      
      :param port: Portnummer (normalerweise 65000)
      :type port: integer

      :param update_interval: Zeit (in Sekunden) zwischen zwei Aufrufen des Datenaustausch-Prozesses mit dem TXT
      :type update_intervall: float

      :return: Leer
      
      Anwedungsbeispiel:
      
      >>> import ftrobopy
      >>> ftrob = ftrobopy.ftrobopy('192.168.7.2', 65000)
    """
    ftTXT.__init__(self, host, port)
    self.queryStatus()
    if self.getVersionNumber() < 0x4010600:
      print('ftrobopy needs at least firmwareversion ',hex(0x4010600), '.')
      sys.exit()
    print('Connected to ', self.getDevicename(), self.getFirmwareVersion())
    for i in range(8):
      self.setPwm(i,0)
    self.startOnline(update_interval)
    self.updateConfig()

  def __del__(self):
    self.stopCameraOnline()
    self.stopOnline()
    self._sock.close()

  def motor(self, output):
    """
      Diese Funktion erzeugt ein Motor-Objekt, das zur Ansteuerung eines Motors verwendet wird,
      der an einem der Motorausgaenge M1-M4 des TXT angeschlossen ist. Falls auch die schnellen
      Zaehler C1-C4 angeschlossen sind (z.b. durch die Verwendung von Encodermotoren oder Zaehlraedern)
      koennen auch Achsumdrehungen genau gemessen werden und damit zurueckgelegte Distanzen bestimmt werden.
      Ausserdem koennen jeweils zwei Motorausgaenge miteinander synchronisiert werden, um z.b. perfekten
      Geradeauslauf bei Robotermodellen zu erreichen.
      
      Anwendungsbeispiel:
      
      >>> Motor1 = ftrob.motor(1)
      
      Das so erzeugte Motor-Objekt hat folgende Funktionen:

      * **setSpeed(speed)**
      * **setDistance(distance, syncto=None)**
      * **finished()**
      * **getCurrentDistance()**
      * **stop()**

      Die Funktionen im Detail:
      
      **setSpeed** (speed)
      
      Einstellung der Motorgeschwindigkeit
      
      :param speed: 
      :type speed: integer
      
      :return: Leer
      
      Gibt an, mit welcher Geschwindigkeit der Motor laufen soll:
      
      - der Wertebereich der Geschwindigkeit liegt zwischen 0 (Motor anhalten) und 512 (maximale Geschwindigkeit)
      - Falls die Geschwindigkeit negativ ist, laeuft der Motor Rueckwaerts
      
      Hinweis: Der eingegebene Wert fuer die Geschwindigkeit haengt nicht linear mit der tatsaechlichen
               Drehgeschwindig des Motors zusammen, d.h. die Geschwindigkeit 400 ist nicht doppelt
               so gross, wie die Geschwindigkeit 200.  Bei Hoeheren Werten von speed kann dadurch die
               Geschwindigkeit in feineren Stufen reguliert werden.
      
      Anwendungsbeispiel:

      >>> Motor1.setSpeed(512)

      Laesst den Motor mit maximaler Umdrehungsgeschwindigkeit laufen.

      **setDistance** (distance, syncto=None)
      
      Einstellung der Motordistanz, die ueber die schnellen Counter gemessen wird, die dafuer natuerlich angeschlossen
      sein muessen.
      
      :param distance: Gibt an, um wieviele Counter-Zaehlungen sich der Motor drehen soll (der Encodermotor gibt 72 Impulse pro Achsumdrehung)
      :type distance: integer
      
      :param syncto: Hiermit koennen zwei Motoren synchronisiert werden um z.B. perfekten Geradeauslauf
                     zu ermoeglichen. Als Parameter wird hier das zu synchronisierende Motorobjekt uebergeben.
      :type syncto: ftrobopy.motor Objekt
      
      :return: Leer
      
      Anwendungsbeispiel:
      
      Der Motor am Anschluss M1 wird mit dem Motor am Anschluss M2 synchronisiert. Die Motoren M1 und M2 laufen
      so lange, bis beide Motoren die eingestellte Distanz (Achsumdrehungen / 72) erreicht haben. Ist einer oder beide Motoren
      nicht mit den schnellen Zaehlereingaengen verbunden, laufen die Motoren bis zur Beendigung des Python-Programmes !

      >>> Motor_links=ftrob.motor(1)
      >>> Motor_rechts=ftrob.motor(2)
      >>> Motor_links.setDistance(100, syncto=Motor_rechts)
      >>> Motor_rechts.setDistance(100, syncto=Motor_links)

      **finished** ()
      
      Abfrage, ob die eingestellte Distanz bereits erreicht wurde.
      
      :return: False: Motor laeuft noch, True: Distanz erreicht
      :rtype: boolean
      
      Anwendungsbeispiel:

      >>> while not Motor1.finished():
            print("Motor laeuft noch")

      **getCurrentDistance** ()
      
      Abfrage der Distanz, die der Motor seit dem letzten setDistance-Befehl zurueckgelegt hat.
      
      :return: Aktueller Wert des Motor Counters
      :rtype: integer
            
      **stop** ()
      
      Anhalten des Motors durch setzen der Geschwindigkeit auf 0.
      
      :return: Leer
      
      Anwendungsbeispiel:
      
      >>> Motor1.stop()
    """
    class mot(object):
      def __init__(self, outer, output):
        self._outer=outer
        self._output=output
        self._speed=0
        self._distance=0
        self._outer._exchange_data_lock.acquire()
        self.setSpeed(0)
        self.setDistance(0)
        self._outer._exchange_data_lock.release()
      def setSpeed(self, speed):
        self._outer._exchange_data_lock.acquire()
        self._speed=speed
        if speed > 0:
         self._outer.setPwm((self._output-1)*2, self._speed)
         self._outer.setPwm((self._output-1)*2+1, 0)
        else:
          self._outer.setPwm((self._output-1)*2, 0)
          self._outer.setPwm((self._output-1)*2+1, -self._speed)
        self._outer._exchange_data_lock.release()
      def setDistance(self, distance, syncto=None):
        self._outer._exchange_data_lock.acquire()
        self._outer.setMotorDistance(self._output-1, distance)
        self._distance=distance
        if syncto:
          self._outer.setMotorSyncMaster(self._output-1, syncto._output)
          self._outer.setMotorSyncMaster(syncto._output-1, self._output)
        self._command_id=self._outer.getCurrentMotorCmdId(self._output-1)
        self._outer.incrMotorCmdId(self._output-1)
        self._outer._exchange_data_lock.release()
      def finished(self):
        old = self._outer.getCurrentMotorCmdId(self._output-1)
        if (old <= self._command_id) and not (old == 0 and self._command_id == 32767):
          return False
        else:
          return True
      def getCurrentDistance(self):
        return self._outer.getCurrentCounterValue(idx=self._output-1)
      def stop(self):
        self._outer._exchange_data_lock.acquire()
        self.setSpeed(0)
        self.setDistance(0)
        self._outer._exchange_data_lock.release()
    
    M, I = self.getConfig()
    M[output-1] = ftTXT.C_MOTOR
    self.setConfig(M, I)
    self.updateConfig()
    return mot(self, output)

  def output(self, num, level=0):
    """
      Diese Funktion erzeugt ein allgemeines Output-Objekt, das zur Ansteuerung von Elementen verwendet
      wird, die an den Ausgaengen O1-O8 angeschlossen sind.
      
      Anwendungsbeispiel:
      
      Am Ausgang O7 ist eine Lampe oder eine LED angeschlossen:
      
      >>> Lampe = ftrob.output(7)
      
      Das so erzeugte allg. Output-Objekt hat folgende Methoden:
      
      **setLevel** (level)
      
      :param level: Ausgangsleistung, die am Output anliegen soll (genauer fuer die Experten: die Gesamtlaenge des Arbeitsintervalls eines PWM-Taktes in Einheiten von 1/512, d.h. mit level=512 liegt das PWM-Signal waehrend des gesamten Taktes auf high).
      :type level: integer, 1 - 512
      
      Mit dieser Methode kann die Ausgangsleistung eingestellt werden, um z.B. die Helligkeit
      einer Lampe zu regeln.
      
      Anwendungsbeispiel:

      >>> Lampe.setLevel(512)
    """
    class out(object):
      def __init__(self, outer, num, level):
        self._outer=outer
        self._num=num
        self._level=level
      def setLevel(self, level):
        self._level=level
        self._outer._exchange_data_lock.acquire()
        self._outer.setPwm(num-1, self._level)
        self._outer._exchange_data_lock.release()
    
    M, I = self.getConfig()
    M[int((num-1)/2)] = ftTXT.C_OUTPUT
    self.setConfig(M, I)
    self.updateConfig()
    return out(self, num, level)    

  def input(self, num):
    """
      Diese Funktion erzeugt ein allgemeines Input-Objekt fuer Sensoren oder Taster,
      die an einem der Eingaenge I1-I8 des TXT angeschlossen sind.
      
      Anwendungsbeispiel:
      
      >>> Taster = ftrob.input(5)
      
      Das so erzeugte allg. Input-Objekt hat folgende Methoden:
      
      **state** ()
      
      Mit dieser Methode wird der Status des Eingangs abgefragt.
      
      :return: Zustand des Schalters (0: Kontakt geschlossen, 1: Kontakt geoeffnet)
      :rtype: integer
      
      Anwendungsbeispiel:

      >>> if Taster.state() == 1:
            print("Der Taster an Eingang I5 wurde gedrueckt.")
    """
    class inp(object):
      def __init__(self, outer, num):
        self._outer=outer
        self._num=num
      def state(self):
        return self._outer.getCurrentInput(num-1)
    
    M, I = self.getConfig()
    I[num-1]= (ftTXT.C_SWITCH, ftTXT.C_DIGITAL)
    self.setConfig(M, I)
    self.updateConfig()
    return inp(self, num)
  
  def ultrasonic(self, num):
    """
      Diese Funktion erzeugt ein Objekt zur Abfrage eines an einem der Eingaenge I1-I8 angeschlossenen
      TX/TXT-Ultraschall-Distanzmessers.
      
      Anwendungsbeispiel:

      >>> ultraschall = ftrob.ultrasonic(6)
      
      Das so erzeugte Ultraschall-Objekt hat folgende Methoden:
      
      **distance** ()
      
      Mit dieser Methode wird der aktuelle Distanz-Wert abgefragt
      
      :return: Die aktuelle Distanz zwischen Ultraschallsensor und vorgelagertem Objekt in cm.
      :rtype: integer

      Anwendungsbeispiel:
      
      >>> print("Der Abstand zur Wand betraegt ", ultraschall.distance(), " cm.")
    """
    class inp(object):
      def __init__(self, outer, num):
        self._outer=outer
        self._num=num
      def distance(self):
        return self._outer.getCurrentInput(num-1)
    
    M, I = self.getConfig()
    I[num-1]= (ftTXT.C_ULTRASONIC, ftTXT.C_ANALOG)
    self.setConfig(M, I)
    self.updateConfig()
    return inp(self, num)

  def sound_finished(self):
    """
      Ueberpruefen, ob die Zeit des zuletzt gespielten Sounds bereits abgelaufen ist
      
      :return: True (Zeit ist abgelaufen) oder False (Sound wird noch abgespielt)
      :rtype: boolean

      Anwendungsbeispiel:
      
      >>> while not ftrob.sound_finished():
            pass
    """
    if time.time()-self._sound_timer > self._sound_length:
      return True
    else:
      return False

  def play_sound(self, idx, seconds=1):
    """
      Einen Sound eine bestimmte zeitlang abspielen
      
      Anwendungsbeispiel:
      
      >>> ftrob.play_sound(27, 5) # 5 Sekunden lang Fahrgeraeusche abspielen
    """
    self._sound_length=seconds
    if time.time()-self._sound_timer < self._sound_length:
      self._exchange_data_lock.acquire()
      self.setSoundIndex(idx)
      self.setSoundRepeat(1)
      self.incrSoundCmdId()
      self._exchange_data_lock.release()
      self._sound_timer=time.time()

  def stop_sound(self):
    """
      Die Aktuelle Soundausgabe stoppen. Dabei wird der abzuspielende Sound-Index auf 0 (=Kein Sound)
      und der Wert fuer die Anzahl der Wiederholungen auf 1 gesetzt.

      :return: Leer
      
      Anwendungsbeispiel:
      
      >>> ftrob.stop_sound()
    """
    self._exchange_data_lock.acquire()
    self.setSoundIndex(0)
    self.setSoundRepeat(1)
    self.incrSoundCmdId()
    self._exchange_data_lock.release()

