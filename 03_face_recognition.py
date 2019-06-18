#import pyttsx3
import hashlib
import sys
import cv2
import numpy as np
import os 
from picamera.array import PiRGBArray
from picamera import PiCamera
import importlib
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
#engine=pyttsx3.init()
class PrpCrypt(object):

    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    # 补足为16的倍数。
    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        # 这里密钥长度为16
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            # \0 backspace
            # text = text + ('\0' * add)
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            # text = text + ('\0' * add)
            text = text + ('\0' * add).encode('utf-8')
        self.ciphertext = cryptor.encrypt(text)
        #这个crypto库不更新了，传参错误最后debug才发现的要把ascii转bytes，坑死了
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        # return plain_text.rstrip('\0')
        return bytes.decode(plain_text).rstrip('\0')

user_key = input(" Please input decryption key: ")
user_key = user_key + 'md5salt'
user_key_md5 = hashlib.md5()
user_key_md5.update(user_key.encode(encoding='utf-8'))
pc = PrpCrypt(user_key_md5.hexdigest())
#pc = PrpCrypt('keyskeyskeyskeys')  # 初始化密钥
enc_yml = open('trainer/enc_trainer.yml', 'r')#打开被加密的模型
enc_yml_contents = enc_yml.read()
enc_yml_bckup = open('trainer/enc_trainer_bckup.yml', 'r')#打开被加密的模型备份
enc_yml_bckup_contents = enc_yml_bckup.read()
if enc_yml_contents !=enc_yml_bckup_contents:
   print(" [ERROR] Data corruption detected.")
   sys.exit(1)
try:
    d = pc.decrypt(enc_yml_contents)#解密成一个字符串
except:
    print (" [ERROR] Key invalid.")
    sys.exit(1)
filename = 'trainer/rev_trainer.yml'#写入文件
with open(filename,'w') as f:
    f.write(d)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/rev_trainer.yml')#读取解密后的模型

my_file = 'trainer/rev_trainer.yml'
if os.path.exists(my_file):
   os.remove(my_file)


cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0
#sys.setdefaultcoding(utf-8)
# names related to ids: example ==> Marcelo: id=1,  etc
names = ['None', '田家禾','董一鸣']
names2=['None','TianJiahe','DongYiming']
# Initialize and start realtime video capture
#cam = cv2.VideoCapture(0)
#cam.set(3, 640) # set video widht
#cam.set(4, 480) # set video height
x=640
y=480
camera = PiCamera()
camera.resolution = (x , y )
camera.framerate =20 #帧速率

rawCapture = PiRGBArray( camera, size=(x, y ) )
# Define min window size to be recognized as a face
minW = 0.1*x
minH = 0.1*y
num=0
for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
    img = frame.array
#while True:

   # ret, img =cam.read()
   # img = cv2.flip(img, -1) # Flip vertically

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale( 
        gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (int(minW), int(minH)),
       )

    for(x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        id2=''
        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            id2=names2[id]
            id = names[id]
            
            if num<3:#broadcast sound not more than three times
              importlib.reload(sys)
              #sys.setdefaultcoding("utf-8")
              txt=id+'已签到,谢谢！'
              
              cmd="ilang "+txt
              os.system(cmd)
              num+=1
             # engine.runAndWait()
            confidence = "  {0}%".format(round(100 - confidence))
            
        else:
            id2 = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(img, id2, (x+5,y-5), font, 1, (255,255,255), 2)
       # cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
    cv2.imshow('camera',img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    rawCapture.truncate(0)
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cv2.destroyAllWindows()
