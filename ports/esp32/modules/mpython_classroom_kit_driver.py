# labplus mPython-box library
# MIT license; Copyright (c) 2018 labplus

# mpython-box buildin periphers drivers

# history:
# V1.0 zhaohuijiang

from machine import Pin, UART
import time
import ujson
from time import sleep_ms, sleep_us, sleep

# touchpad


class BS8112A(object):
   """  """

   def __init__(self, i2c):
      self.addr = 80
      # config
      self._i2c = i2c
      self.config = [0xB0, 0x00, 0x00, 0x83, 0xf3, 0x98, 0x0f, 0x0f,
                     0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x00]
      checksum = 0
      for i in range(1, 19):
         checksum += self.config[i]
      checksum &= 0xff
      self.config[18] = checksum
      # print(self.config[18])
      retry = 0
      if (retry < 5):
         try:
            self._i2c.writeto(self.addr, bytearray(self.config), True)
            return
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")

       # i2c.writeto(self.addr, b'\xB0', False)
       # time.sleep_ms(10)
       # print(i2c.readfrom(self.addr, 17, True))

   # key map:
   # value       bit7 bit6 bit5 bit4 bit3 bit2 bit1 bit0
   # bs8112a key Key8 Key7 Key6 Key5 Key4 Key3 Key2 Key1
   # mpython key       N    O    H    T    Y    P
   def key_value(self):
      retry = 0
      if (retry < 5):
         try:
            self._i2c.writeto(self.addr, b'\x08', False)
            time.sleep_ms(10)
            value = self._i2c.readfrom(self.addr, 1, True)
            time.sleep_ms(10)
            return value
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")


class Codec_mode():
   ES_MODULE_ADC_DAC = 0x00
   ES_MODULE_DAC = 0x01
   ES_MODULE_ADC = 0x02


class Es8388():
   """  """

   def __init__(self, i2c, adc_volume=0, dac_volume=0, volume=65):
      self._i2c = i2c
      self.addr = 16
      self.adc_volume = adc_volume
      self.dac_volume = dac_volume
      self.volume = volume
      self.set_voice_mute(1)
      retry = 0
      if (retry < 5):
         try:
            # i2c.writeto(self.addr, bytearray([0x19, 0x04])) # ES8388_DACCONTROL3 0x04 mute/0x00 unmute&ramp;DAC unmute and  disabled digital volume control soft ramp
            #  Chip Control and Power Management
            self._i2c.writeto(self.addr, bytearray(
                [0x01, 0x50]))  # ES8388_CONTROL2 0x40?
            # ES8388_CHIPPOWER normal all and power up all
            self._i2c.writeto(self.addr, bytearray([0x02, 0x00]))
            # ES8388_MASTERMODE CODEC IN I2S SLAVE MODE 0x00: slave
            self._i2c.writeto(self.addr, bytearray([0x08, 0x00]))
            # dac setup
            # ES8388_DACPOWER . disable DAC and disable Lout/Rout/1/2
            self._i2c.writeto(self.addr, bytearray([0x04, 0xC0]))
            # ES8388_CONTROL1. Enfr=0,Play&Record Mode,(0x17-both of mic&paly)
            self._i2c.writeto(self.addr, bytearray([0x00, 0x12]))
            # ES8388_DACCONTROL1 1a 0x18:16bit iis , 0x00:24
            self._i2c.writeto(self.addr, bytearray([0x17, 0x18]))
            # ES8388_DACCONTROL2 DACFsMode,SINGLE SPEED; DACFsRatio,256
            self._i2c.writeto(self.addr, bytearray([0x18, 0x02]))
            # ES8388_DACCONTROL16 0x00 audio on LIN1&RIN1,  0x09 LIN2&RIN2
            self._i2c.writeto(self.addr, bytearray([0x26, 0x00]))
            # ES8388_DACCONTROL17 only left DAC to left mixer enable 0db
            self._i2c.writeto(self.addr, bytearray([0x27, 0x90]))
            # ES8388_DACCONTROL20 only right DAC to right mixer enable 0db
            self._i2c.writeto(self.addr, bytearray([0x2a, 0x90]))
            # ES8388_DACCONTROL21 set internal ADC and DAC use the same LRCK clock, ADC LRCK as internal LRCK
            self._i2c.writeto(self.addr, bytearray([0x2b, 0x80]))
            # ES8388_DACCONTROL23 vroi=0
            self._i2c.writeto(self.addr, bytearray([0x2d, 0x00]))
            self.set_adc_dac_volume(
                Codec_mode.ES_MODULE_DAC, self.dac_volume, 0)  # 0db
            # ES8388_DACPOWER 0x3c Enable DAC and Enable Lout/Rout/1/2
            self._i2c.writeto(self.addr, bytearray([0x04, 0x3c]))
            # adc setup
            self._i2c.writeto(self.addr, bytearray(
                [0x03, 0xff]))  # ES8388_ADCPOWER
            # ES8388_ADCCONTROL1 MIC Left and Right channel PGA gain
            self._i2c.writeto(self.addr, bytearray([0x09, 0xbb]))
            # ES8388_ADCCONTROL2 0x00 LINSEL & RINSEL, LIN1/RIN1 as ADC Input; DSSEL,use one DS Reg11; DSR, LINPUT1-RINPUT1
            self._i2c.writeto(self.addr, bytearray([0x0a, 0x00]))
            # ES8388_ADCCONTROL3 clock input
            self._i2c.writeto(self.addr, bytearray([0x0b, 0x02]))
            # ES8388_ADCCONTROL4 Left/Right data, Left/Right justified mode, Bits length 16bit, I2S format 0x0c?
            self._i2c.writeto(self.addr, bytearray([0x0c, 0x0c]))
            # ES8388_ADCCONTROL5 ADCFsMode,singel SPEED,RATIO=256
            self._i2c.writeto(self.addr, bytearray([0x0d, 0x02]))
            # ALC for Microphone
            self.set_adc_dac_volume(
                Codec_mode.ES_MODULE_ADC, self.adc_volume, 0)  # 0db
            # ES8388_ADCPOWER Power on ADC, Enable LIN&RIN, Power off MICBIAS, set int1lp to low power mode
            self._i2c.writeto(self.addr, bytearray([0x03, 0x09]))
            # set volume
            self.set_volume(self.volume)
            self.set_voice_mute(0)
            # test
            # for i in range(0, 52):
            #     i2c.writeto(self.addr, bytearray([i]))
            #     print("%d: %d" % (i, i2c.readfrom(self.addr, 1)[0]))
            return
         except:
               retry = retry + 1
      else:
         raise Exception("es8388 i2c read/write error!")

   def deinit(self):
      retry = 0
      if (retry < 5):
         try:
            # ES8388_CHIPPOWER reset and stop es838
            self._i2c.writeto(self.addr, bytearray([0x02, 0xff]))
            return
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")

   def set_adc_dac_volume(self, mode, volume, dot):
      _volume = volume
      if (_volume < -96):
         _volume = -96
      else:
         _volume = 0
      _dot = 0
      if dot >= 5:
         _dot = 1

      _volume = (-_volume << 1) + _dot
      retry = 0
      if (retry < 5):
         try:
            if (mode == Codec_mode.ES_MODULE_ADC or mode == Codec_mode.ES_MODULE_ADC_DAC):
               self._i2c.writeto(self.addr, bytearray(
                   [0x10, _volume]))  # ES8388_ADCCONTROL8
               self._i2c.writeto(self.addr, bytearray(
                   [0x11, _volume]))  # ES8388_ADCCONTROL9
            if (mode == Codec_mode.ES_MODULE_DAC or mode == Codec_mode.ES_MODULE_ADC_DAC):
               self._i2c.writeto(self.addr, bytearray(
                   [0x1b, _volume]))  # ES8388_DACCONTROL5
               self._i2c.writeto(self.addr, bytearray(
                   [0x1a, _volume]))  # ES8388_DACCONTROL4
            return
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")

   def set_volume(self, volume):
      self.volume = volume
      if (self.volume < 0):
         self.volume = 0
      elif (self.volume > 100):
         self.volume = 100

      retry = 0
      if (retry < 5):
         try:
            self._i2c.writeto(self.addr, bytearray(
                [0x2e, self.volume//3]))  # ES8388_DACCONTROL24
            self._i2c.writeto(self.addr, bytearray(
                [0x2f, self.volume//3]))  # ES8388_DACCONTROL25
            self._i2c.writeto(self.addr, bytearray(
                [0x30, 0]))  # ES8388_DACCONTROL26
            self._i2c.writeto(self.addr, bytearray(
                [0x31, 0]))  # ES8388_DACCONTROL27
            # print("volume L: %d" % (self.volume//3))
            return
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")

   def get_volume(self):
         return self.volume

   def set_voice_mute(self, mute):
      retry = 0
      if (retry < 5):
         try:
            self._i2c.writeto(self.addr, b'\x19')
            dac_ctr3 = self._i2c.readfrom(self.addr, 1)[0]
            if(mute):
               dac_ctr3 |= 0x04
            else:
               dac_ctr3 &= 0xFB
            self._i2c.writeto(self.addr, bytearray([0x19, dac_ctr3]))
         except:
               retry = retry + 1
      else:
         raise Exception("bs8112a i2c read/write error!")


uart2 = UART(2, baudrate=115200, rx=Pin.P8, tx=Pin.P23,
             timeout=50, timeout_char=1024, rxbuf=512, txbuf=512)


class K210Error(Exception):
   """K210异常类"""
   pass

class blob():
   
   def __init__(self,*args):
      self.dict = args[0]

   def __repr__(self):
      return  self.dict

   def x(self):
      return self.dict['x']

   def y(self):
      return self.dict['y']

   def w(self):
      return self.dict['w']

   def h(self):
      return self.dict['h']

   def rect(self):
      return(self.dict['x'], self.dict['y'], self.dict['w'], self.dict['h'])

   def pixels(self):
      return self.dict['pixels']

   def cx(self):
      return self.dict['cx']

   def cy(self):
      return self.dict['cy']
      
   def rotation(self):
      return self.dict['rotation']

   def code(self):
      return self.dict['code']

   def count(self):
      return self.dict['count']




class K210():
   def __init__(self):
        t1 = time.ticks_ms()
        while (time.ticks_diff(time.ticks_ms(), t1) < 10000):
            rsp = self.send_cmd({'GET_KEYS': 0})  # 通过发获取按键指令测试K210是否初始化成功
            if rsp and isinstance(rsp, dict):
                for key, value in rsp.items():
                    if key == 'RET_KEYS':
                        return
        raise K210Error("K210 init failed!")

   def send_cmd(self, command, wait=True, timeout=100):
      json_stream = ujson.dumps(command)
      uart2.write(json_stream + '\n')
      # print("UART_Send:%s" % (json_stream + '\n'))
      t1 = time.ticks_ms()
      while wait:
         if uart2.any() > 0:
               r=None
               r = uart2.readline()
               r= r.strip()
               while uart2.readline():
                  pass
               # print("UART_Recv:%s" % r)
               try:
                  rsp = ujson.loads(r)
               except Exception as e:
                  print(e)
                  break
               else:
                  if rsp and isinstance(rsp, dict):
                     for key, value in rsp.items():
                        if key == 'ERROR':
                           raise K210Error(value)
                  return rsp
         if time.ticks_diff(time.ticks_ms(), t1) > timeout:
            # raise K210Error("k210 not respone!")
            break
      return None

   def response_value(self, rsp, _key):
         for key, value in rsp.items():
            if key == _key:
               return value

   def get_key(self):
      rsp = self.send_cmd({'GET_KEYS': 0}, True, 50)

      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_KEYS')
      return None

   def get_distance(self):
      rsp = self.send_cmd({'GET_DISTANCE': 0}, True, 50)
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_DISTANCE')
      return None

   def set_motor(self, speed):
      rsp = self.send_cmd({'SET_MOTOR': speed}, True, 50)
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_MOTOR')
      return None

   def reset(self):
      self.send_cmd({'RESET': 0} ,True, 20)

   def select_model(self, *args):

      self.send_cmd({'SELE_MOD': args[0]},True, 50)

   def load_model(self, **kws):

      self.send_cmd({'LOD_MOD': kws}, True, 50)

   def detect_yolo(self):
      rsp = self.send_cmd({'DET_YO': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_DET_YO')
      return None

   def predict_net(self):
      rsp = self.send_cmd({'PRE_NET': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_PRE_NET')
      return None

   def deinit_yolo(self):
      self.send_cmd({'DINT_YO': 0},True, 20)

   def deinit_net(self):
      self.send_cmd({'DINT_NET': 0},True, 20)

   def camera_snapshot(self):
      self.send_cmd({'SNAPSHOT': 0},True,20)

   def camera_reset(self):
      self.send_cmd({'CAM_RST': 0},True, 20)

   def camera_run(self, *arg):
      self.send_cmd({'CAM_RUN': arg[0]},True, 20)

   def camera_set_pixformat(self, *arg):
      self.send_cmd({'CAM_SET_PF': arg[0]},True, 20)

   def camera_set_contrast(self, *arg):
      self.send_cmd({'CAM_SET_CRA': arg[0]},True, 20)

   def camera_set_brightness(self, *arg):
      self.send_cmd({'CAM_SET_BRG': arg[0]},True, 20)

   def camera_set_saturation(self, *arg):
      self.send_cmd({'CAM_SET_SAT': arg[0]},True, 20)

   def camera_set_auto_gain(self, *arg, **kw):
      self.send_cmd({'CAM_AUTO_GAIN': [arg, kw]},True, 20)

   def camera_set_auto_whitebal(self, *arg):
      self.send_cmd({'CAM_AUTO_WBAL': arg[0]},True, 20)

   def camera_set_windowing(self, *arg):
      self.send_cmd({'CAM_SET_WIN': arg[0]},True, 20)

   def camera_set_hmirror(self, *arg):
      self.send_cmd({'CAM_SET_HM': arg[0]},True, 20)

   def camera_set_vflip(self, *arg):
      self.send_cmd({'CAM_SET_VF': arg[0]},True, 20)

   def camera_skip_frames(self, *arg, **kw):
      self.send_cmd({'CAM_SKIP_FRM': [arg, kw]},True, 20)

   def lcd_init(self, *args, **kws):
      self.send_cmd({'LCD_INT': [args, kws]},True,1000)

   def lcd_display(self, **kws):
      self.send_cmd({'LCD_DISP': kws},True, 20)

   def lcd_clear(self, **kws):
      self.send_cmd({'LCD_CLR': kws},True, 20)

   def lcd_draw_string(self, *args):
      self.send_cmd({'LCD_STR': args},True, 20)

   def image_load(self, *args, **kws):
      self.send_cmd({'IMG_LOD': [args, kws]},True, 20)

   def image_width(self):
      rsp = self.send_cmd({'IMG_WID': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_IMG_WID')
      return None

   def image_hight(self):
      rsp = self.send_cmd({'IMG_HIG': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_IMG_HIG')
      return None

   def image_format(self):
      rsp = self.send_cmd({'IMG_FRM': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_IMG_FRM')
      return None

   def image_size(self):
      rsp = self.send_cmd({'IMG_SIZE': 0})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_IMG_SIZE')
      return None

   def image_get_pixel(self, *args, **kws):
      rsp = self.send_cmd({'IMG_GET_PIX': [args, kws]})
      if rsp and isinstance(rsp, dict):
         return self.response_value(rsp, 'RET_IMG_GET_PIX')
      return None

   def image_set_pixel(self, *args, **kws):
      self.send_cmd({'IMG_SET_PIX': [args, kws]},True, 20)

   def image_mean_pool(self, *args, **kws):
      self.send_cmd({'IMG_MEAN_P': [args, kws]},True, 20)

   def image_to_grayscale(self):
      self.send_cmd({'IMG_TO_GRAY': 0},True, 20)

   def image_to_rainbow(self):
      self.send_cmd({'IMG_TO_RB': 0},True, 20)

   def image_copy(self, *args, **kws):
      self.send_cmd({'IMG_CPY': [args, kws]},True, 20)

   def image_save(self, *args, **kws):
      self.send_cmd({'IMG_SAVE': [args, kws]},True, 20)

   def image_clear(self):
      self.send_cmd({'IMG_CLR': 0},True, 20)

   def image_draw_line(self, *args, **kws):
      self.send_cmd({'IMG_DRW_LN': [args, kws]},True, 20)

   def image_draw_rectangle(self, *args, **kws):
      self.send_cmd({'IMG_DRW_RECTANG': [args, kws]},True, 20)

   def image_draw_circle(self, *args, **kws):
      self.send_cmd({'IMG_DRW_CIR': [args, kws]},True, 20)

   def image_draw_string(self, *args, **kws):
      self.send_cmd({'IMG_DRW_STR': [args, kws]},True, 20)

   def image_draw_cross(self, *args, **kws):
      self.send_cmd({'IMG_DRW_CRS': [args, kws]},True, 20)

   def image_draw_arrow(self, *args, **kws):
      self.send_cmd({'IMG_DRW_ARR': [args, kws]},True, 20)

   def image_draw_image(self, *args, **kws):
      self.send_cmd({'IMG_DRW_IMG': [args, kws]},True, 20)

   def image_binary(self, *args, **kws):
      self.send_cmd({'IMG_BINARY': [args, kws]},True, 20)

   def image_invert(self):
      self.send_cmd({'IMG_INVERT': 0},True, 20)

   def image_erode(self, *args, **kws):
      self.send_cmd({'IMG_ERODE': [args, kws]},True, 20)
      
   def image_dilate(self, *args, **kws):
      self.send_cmd({'IMG_DIL': [args, kws]},True, 20)

   def image_negate(self, *args, **kws):
      self.send_cmd({'IMG_NEG': [args, kws]},True, 20)

   def image_mean(self, *args, **kws):
      self.send_cmd({'IMG_MEAN': [args, kws]},True, 20)

   def image_mode(self, *args, **kws):
      self.send_cmd({'IMG_MODE': [args, kws]},True, 20)

   def image_median(self, *args, **kws):
      self.send_cmd({'IMG_MEDIAN': [args, kws]},True, 20)

   def image_midpoint(self, *args, **kws):
      self.send_cmd({'IMG_MIDP': [args, kws]},True, 20)

   def image_cartoon(self, *args, **kws):
      self.send_cmd({'IMG_CART': [args, kws]},True, 20)

   def image_conv3(self, *args, **kws):
      self.send_cmd({'IMG_CONV': [args, kws]},True, 20)

   def image_gaussian(self, *args, **kws):
      self.send_cmd({'IMG_GAUS': [args, kws]},True, 20)

   def image_bilateral(self, *args, **kws):
      self.send_cmd({'IMG_BIL': [args, kws]},True, 20)

   def image_linpolar(self, *args, **kws):
      self.send_cmd({'IMG_LINP': [args, kws]},True, 20)

   def image_logpolar(self, *args, **kws):
      self.send_cmd({'IMG_LOGP': [args, kws]},True, 20)

   def image_rotation_corr(self, *args, **kws):
      self.send_cmd({'IMG_ROT_COR': [args, kws]},True, 20)

   def image_find_blobs(self, *args, **kws):
      rsp = self.send_cmd({'IMG_FID_BLOB': [args, kws]})
      if rsp and isinstance(rsp, dict):
         return [blob(i) for i in self.response_value(rsp, 'RET_FID_BLOB')]
      return None
