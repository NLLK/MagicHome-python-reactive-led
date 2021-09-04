from PyQt5 import QtCore
from sklearn import preprocessing
from colorpicker.colorpicker import ColorPicker
import magichome as mh
import pyaudio
import numpy as np
import colorsys 
from scipy.fftpack import rfft, rfftfreq
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import pyqtSignal
from UI.mainUI import Ui_MainWindow
import sys
import time

class MainApp(QtWidgets.QMainWindow):
    lowBarSetValueSignal = pyqtSignal(int)
    midBarSetValueSignal = pyqtSignal(int)
    highBarSetValueSignal = pyqtSignal(int)
    noiseCanselLevelProgressBarSetValueSignal = pyqtSignal(int)
    def __init__(self):
        super(MainApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init()

    def init(self):
        self.color = QColor(255,255,255)
        self.ip_addresss = '192.168.8.23'
        self.audioStreamInitialised = False
        self.ledLastTimeUpdated = time.time()
        self.recordNoiseTimer = time.time()
        self.led_connected = False
        self.uiLastTimeUpdated = self.ledLastTimeUpdated 
        self.pyaudioModule = pyaudio.PyAudio()
        self.audio_channels = 1
        self.audio_rate = 44100
        self.audio_dev_index = 4
        self.audio_chunk = 1024
        self.audio_noiseCansellationLevel = 5
        self.init_ui()
        self.init_ui_handlers()

    def init_ui_handlers(self):
        self.ui.chooseColorButton.clicked.connect(self.e_chooseColorButton_clicked)
        self.ui.powerOnButton.clicked.connect(self.e_powerOnButton_clicked)
        self.ui.powerOffButton.clicked.connect(self.e_powerOffButton_clicked)
        self.ui.ipaddresschangeButton.clicked.connect(self.e_ipaddresschangeButton_clicked)
        self.ui.reactiveStartButton.clicked.connect(self.e_reactiveStartButton_clicked)
        self.ui.reactiveStopButton.clicked.connect(self.e_reactiveStopButton_clicked)
        self.ui.lowDial.valueChanged.connect(self.e_lowDial_valueChanged)
        self.ui.midDial.valueChanged.connect(self.e_midDial_valueChanged)
        self.ui.brightnessSlider.valueChanged.connect(self.e_brightnessSlider_valueChanged)    
        self.ui.lowGainSlider.valueChanged.connect(self.e_lowGainSlider_valueChanged)
        self.ui.midGainSlider.valueChanged.connect(self.e_midGainSlider_valueChanged)
        self.ui.highGainSlider.valueChanged.connect(self.e_highGainSlider_valueChanged)
        self.ui.lowResetButton.clicked.connect(self.e_lowResetButton_clicked)
        self.ui.midResetButton.clicked.connect(self.e_midResetButton_clicked)
        self.ui.highResetButton.clicked.connect(self.e_highResetButton_clicked)
        self.ui.lowCutOffSlider.valueChanged.connect(self.e_lowCutOffSlider_valueChanged)
        self.ui.midCutOffSlider.valueChanged.connect(self.e_midCutOffSlider_valueChanged)
        self.ui.highCutOffSlider.valueChanged.connect(self.e_highCutOffSlider_valueChanged)
        self.ui.lowResetCutOffButton.clicked.connect(self.e_lowResetCutOffButton_clicked)
        self.ui.midResetCutOffButton.clicked.connect(self.e_midResetCutOffButton_clicked)
        self.ui.highResetCutOffButton.clicked.connect(self.e_highResetCutOffButton_clicked)
        self.ui.ledDisconnectButton.clicked.connect(self.e_ledDisconnectButton_clicked)
        self.lowBarSetValueSignal.connect(self.s_lowBarSetValue)
        self.midBarSetValueSignal.connect(self.s_midBarSetValue)
        self.highBarSetValueSignal.connect(self.s_highBarSetValue)
        self.noiseCanselLevelProgressBarSetValueSignal.connect(self.s_noiseCanselLevelProgressBarSetValue)

        self.ui.inputDevicesComboBox.currentIndexChanged.connect(self.e_inputDevicesComboBox_currentIndexChanged)
        self.ui.noiseCanselLevelSlider.valueChanged.connect(self.e_noiseCanselLevelSlider_valueChanged)
        self.ui.noiseCanselLevelEdit.textChanged.connect(self.e_noiseCanselLevelEdit_textChanged)
        self.ui.recordNoiseButton.clicked.connect(self.e_recordNoiseButton_clicked)

    def init_ui(self):
        for i in range(0, int(self.pyaudioModule.get_device_count()/2)):
            device = self.pyaudioModule.get_device_info_by_index(i)
            if device['maxInputChannels'] > 0:
                index = str(device['index']+1)
                name = device['name']
                if name.__len__()>30:
                    name = name[:30]
                    name += "..."
                self.ui.inputDevicesComboBox.addItem(index+'. '+name)
        pass

    def paintEvent(self, e):
            qp = QPainter()
            qp.begin(self)
            self.drawRectangle(qp)
            qp.end()
            pass
    def drawRectangle(self,qp):
        qp.setBrush(self.color)
        qp.drawRect(20, 60, 100, 100)

    def e_chooseColorButton_clicked(self):
        self.paintingActive = False
        my_color_picker = ColorPicker()
        picked_color = my_color_picker.getColor()
        self.color = QColor(int(picked_color[0]),int(picked_color[1]),int(picked_color[2]))
        level = self.ui.brightnessSlider.value()
        self.color = self.change_brightness(self.color, self.brightnessLevelFix(level))
        if self.led_connected == True:
            self.led.turn_on()
            self.led.update_device(self.color.red(), self.color.green(), self.color.blue())
    
    def e_ipaddresschangeButton_clicked(self):
        self.ip_addresss = self.ui.ipaddressEdit.text()
        self.led = mh.MagicHomeApi(self.ip_addresss, 0)
        try:
            status = self.led.get_status()
        except:
            self.ui.connectionLabel.setText("Disconnected")
            self.led_connected = False
        else:
            self.ui.connectionLabel.setText("Connected")
            self.led_connected = True
    def e_ledDisconnectButton_clicked(self):
        self.ui.connectionLabel.setText("Disconnected")
        self.led_connected = False
        pass
    def e_powerOnButton_clicked(self):
        if self.led_connected == True:
            self.led.turn_on()
    def e_powerOffButton_clicked(self):
        if self.led_connected == True:
            self.led.turn_off()
    def e_lowDial_valueChanged(self,e):
        self.ui.lowLabel.setText(str(e))
        self.ui.midLowerLabel.setText(str(e+1) + " Hz")
        self.ui.midDial.setMinimum(e+1)
        pass
    def e_midDial_valueChanged(self,e):
        self.ui.midLabel.setText(str(e))
        self.ui.highLowerLabel.setText(str(e+1) + " Hz")

        self.ui.highDial.setMinimum(e+1)
        pass
    def e_lowGainSlider_valueChanged(self, e):
        self.ui.lowGainLabel.setText(str(e-50))
        pass
    def e_midGainSlider_valueChanged(self, e):
        self.ui.midGainLabel.setText(str(e-50))
        pass    
    def e_highGainSlider_valueChanged(self, e):
        self.ui.highGainLabel.setText(str(e-50))
        pass
    def e_lowResetButton_clicked(self,e):
        self.ui.lowGainSlider.setValue(50)
        pass
    def e_midResetButton_clicked(self,e):
        self.ui.midGainSlider.setValue(50)
        pass
    def e_highResetButton_clicked(self,e):
        self.ui.highGainSlider.setValue(50)
        pass

    def e_lowCutOffSlider_valueChanged(self,e):
        self.ui.lowCutOffLabel.setText(str(e)+'%')
    def e_midCutOffSlider_valueChanged(self,e):
        self.ui.midCutOffLabel.setText(str(e)+'%')
    def e_highCutOffSlider_valueChanged(self,e):
        self.ui.highCutOffLabel.setText(str(e)+'%')

    def e_lowResetCutOffButton_clicked(self):
        self.ui.lowCutOffLabel.setText(str(0)+'%')
        self.ui.lowCutOffSlider.setValue(0)
    def e_midResetCutOffButton_clicked(self):
        self.ui.midCutOffLabel.setText(str(0)+'%')
        self.ui.midCutOffSlider.setValue(0)
    def e_highResetCutOffButton_clicked(self):
        self.ui.highCutOffLabel.setText(str(0)+'%')
        self.ui.highCutOffSlider.setValue(0)

    def e_brightnessSlider_valueChanged(self,e):
        self.ui.brightnessEdit.setText(str(e))
        level = self.brightnessLevelFix(e)
        self.color = self.change_brightness(self.color,level)
        if self.led_connected == True:
            if e <1:
                self.led.turn_off()
            else:
                self.led.update_device(self.color.red(), self.color.green(), self.color.blue())
    
    def e_inputDevicesComboBox_currentIndexChanged(self,e):
        text = self.ui.inputDevicesComboBox.itemText(e)
        dev_index = int(text[:2].replace('.',''))-1
        choosenDevice = self.pyaudioModule.get_device_info_by_index(dev_index)
        
        self.audio_channels = choosenDevice['maxInputChannels']
        self.audio_dev_index = dev_index
        self.audio_rate = int(choosenDevice['defaultSampleRate'])

        self.e_reactiveStopButton_clicked()

    def e_noiseCanselLevelSlider_valueChanged(self,e):
        self.ui.noiseCanselLevelEdit.setText(str(e))
        self.audio_noiseCansellationLevel = e
    def e_noiseCanselLevelEdit_textChanged(self,e):
        try:
            value = int(e)
        except:
            pass
        else:
            self.ui.noiseCanselLevelSlider.setValue(value)
            
        pass
    def s_lowBarSetValue(self, value):
        self.ui.lowBar.setValue(value)
    def s_midBarSetValue(self, value):
        self.ui.midBar.setValue(value)
    def s_highBarSetValue(self, value):
        self.ui.highBar.setValue(value)   
    def s_noiseCanselLevelProgressBarSetValue(self, value):
        self.ui.noiseCanselLevelProgressBar.setValue(value)   
    def e_recordNoiseButton_clicked(self):
        self.recordNoiseTimer = time.time()
        self.audio_noiseCansellationLevel = 0
        self.ui.recordNoiseButton.setDisabled(True)
        self.ui.reactiveStartButton.setDisabled(True)
        self.ui.reactiveStopButton.setDisabled(True)
        self.audioStream = self.pyaudioModule.open(
                 format=pyaudio.paInt16,
                 channels = self.audio_channels,
                 rate = self.audio_rate,
                 output = False,
                 input = True,
                 input_device_index = self.audio_dev_index,
                 stream_callback = self.recordNoiseCallback,
                 frames_per_buffer = self.audio_chunk)
        self.audioStream.start_stream()
        
    def recordNoiseCallback(self, in_data, frame_count, time_info, flag):
        diff = time.time() - self.recordNoiseTimer
        if diff <= 5:
            self.noiseCanselLevelProgressBarSetValueSignal.emit(int(diff*(100/5)))
            array = np.frombuffer(in_data, dtype=np.int16)    #creating array with audio data
            fft_row = rfft(array)                             #using fft to create fq array
            fft_abs = abs(fft_row)
            max = np.max(fft_abs)//1000
            if self.audio_noiseCansellationLevel < max:
                self.audio_noiseCansellationLevel = max
            pass
        else:
            print("Recorded")
            self.ui.recordNoiseButton.setEnabled(True)
            self.ui.reactiveStartButton.setEnabled(True)
            self.ui.reactiveStopButton.setEnabled(True)
            self.noiseCanselLevelProgressBarSetValueSignal.emit(0)
            self.ui.noiseCanselLevelSlider.setValue(int(self.audio_noiseCansellationLevel))
            return in_data, pyaudio.paAbort
        return in_data, pyaudio.paContinue
    def e_reactiveStartButton_clicked(self):
        if self.audioStreamInitialised == False:
            self.audioStreamInitialised = True

            self.audioStream = self.pyaudioModule.open(
                 format=pyaudio.paInt16,
                 channels = self.audio_channels,
                 rate = self.audio_rate,
                 output = False,
                 input = True,
                 input_device_index = self.audio_dev_index,
                 stream_callback = self.audioStreamCallback,
                 frames_per_buffer = self.audio_chunk)
            self.audioStream.start_stream()
            self.ui.recordNoiseButton.setDisabled(True)

    def e_reactiveStopButton_clicked(self):
        if self.audioStreamInitialised == True:
            self.ui.recordNoiseButton.setEnabled(True)
            self.audioStream.stop_stream()
            #self.pyaudioModule.terminate()
            self.audioStreamInitialised = False
            self.fftthings()#TODO: delete it

    def audioStreamCallback(self, in_data, frame_count, time_info, flag):
        self.row_data = in_data
        rate = 60
        if time.time() - self.uiLastTimeUpdated >(1/rate):
            self.fftthings()
            self.uiLastTimeUpdated = time.time()

        return in_data, pyaudio.paContinue
    def fftthings(self):
        array = np.frombuffer(self.row_data, dtype=np.int16)    #creating array with audio data
        fft_row = rfft(array)                                   #using fft to create fq array
        fft_abs = abs(fft_row)                                  #get real
        noise_level = self.audio_noiseCansellationLevel*1000
        fft_abs[fft_abs <=noise_level] = 0                      #noise reduction
        norm_array = preprocessing.normalize([fft_abs])         #normalizing, cus otherwise it would be dependent on volume
        fft_fin = norm_array[0]*100                             #multiplying to make it looks like percents
        #SINGLE COLOR MODE: PEAKS
        max = np.max(fft_fin)                                   #finding maximum of signal

        #catecorize fqs for three groups (of course you can create your own but i needed these three)

        step = float(self.audio_rate)/self.audio_chunk          #we have (for example) 1024 numbers for 44100 hz sectors, so they are grouped to 44100/1024 sectors
        lowBorderIndex = int(self.ui.lowDial.value()//step)     #first upper border to split array
        if lowBorderIndex == 0:
            lowBorderIndex = 1
        lowArray = fft_fin[:lowBorderIndex]                     #spliting first part
        midBorderIndex = int(self.ui.midDial.value()//step)     #second upper border to split array
        if midBorderIndex-lowBorderIndex < 1:
            midBorderIndex += abs(midBorderIndex-lowBorderIndex)+1
        midArray = fft_fin[lowBorderIndex:midBorderIndex]       #spliting second part
        highArray = fft_fin[midBorderIndex:]                    #spliting last part

        #finding maximums of each part
        lowMax = np.max(lowArray)                               
        midMax = np.max(midArray)
        highMax = np.max(highArray)

        #cut off some values to make output more spiky
        lowMax = self.cut_off_value(lowMax,self.ui.lowCutOffSlider.value())
        midMax = self.cut_off_value(midMax,self.ui.midCutOffSlider.value())
        highMax = self.cut_off_value(highMax,self.ui.highCutOffSlider.value())


        #adjust volume for each part
        lowFin = self.check_number_value(lowMax + (self.ui.lowGainSlider.value()-50),100)
        midFin = self.check_number_value(midMax + (self.ui.midGainSlider.value()-50),100)
        highFin = self.check_number_value(highMax + (self.ui.highGainSlider.value()-50),100)

        self.ui_updateBars(int(lowFin),int(midFin),int(highFin))#Updating bars showing level of each part

        #TODO: добавить режим, где моргает просто по максимуму громкости
        flag = False
        if flag == True:
            level = max
            newColor = self.change_brightness(self.color,level)
            self.updateDevice(newColor)
            pass
        else:  
            brightness = self.ui.brightnessSlider.value()/100
            red = int(lowFin *(255/100)*brightness)
            blue = int(midFin *(255/100)*brightness)
            green = int(highFin *(255/100)*brightness)
            color = QColor(red, green, blue)
            self.updateDevice(color)

        ### OTHER THINGS ###

        #The way to know what frequency is playing
        # max_i = np.where(fft_fin == max)
        # freqs = rfftfreq(self.audio_chunk, 1/self.audio_rate)
        # ccc = freqs[max_i[0]]
    def check_number_value(self, number, value):
        if number>value:
            return value
        elif number<0:
            return 0
        else:
            return number
    def cut_off_value(self, value, lowBorder):
        if value<lowBorder:
            return 0
        else:
            return value
    def ui_updateBars(self, low, mid, high):

        self.lowBarSetValueSignal.emit(low)
        self.midBarSetValueSignal.emit(mid)
        self.highBarSetValueSignal.emit(high)
        self.ui_barsLastTimeUpdated = time.time()
    def change_brightness(self, color, level):
        oldColor = color
        level = level/100
        
        hsv_color = colorsys.rgb_to_hsv(oldColor.red()/256,oldColor.green()/256,oldColor.blue()/256)
        newColor = colorsys.hsv_to_rgb(hsv_color[0], hsv_color[1], level)
        newColor = QColor(int(newColor[0]*256),int(newColor[1]*256),int(newColor[2]*256))
        return newColor
    def brightnessLevelFix(self,level):
        if level>99:
            level = 99
        if level <1:
            level = 1
        return level
    def updateDevice(self, color):
        if self.led_connected == True:
            rate = 60
            if time.time() - self.ledLastTimeUpdated >(1/rate):
                self.led.update_device(color.red(), color.green(), color.blue())
                self.ledLastTimeUpdated = time.time()
        
def main():
    #QT_QPA_PLATFORM_PLUGIN_PATH = ".venv\Lib\platforms"
    app = QtWidgets.QApplication([])
    app.setStyle('Fusion')
    mainApp = MainApp()
    mainApp.show()

    sys.exit(app.exec())
#pyuic5 ui\main.ui -o ui\mainUI.py  
main()
