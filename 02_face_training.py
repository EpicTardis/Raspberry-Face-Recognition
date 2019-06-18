import cv2
import numpy as np
from PIL import Image
import os
import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import hashlib

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


#pc = PrpCrypt('keyskeyskeyskeys')  # 初始化密钥
user_key = input(" Please input encryption key:")
user_key = user_key + 'md5salt'
user_key_md5 = hashlib.md5()
user_key_md5.update(user_key.encode(encoding='utf-8'))
pc = PrpCrypt(user_key_md5.hexdigest())
# Path for face image database
path = 'dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi
ori_yml = open('trainer/trainer.yml', 'r')
ori_yml_contents = ori_yml.read()
e = pc.encrypt(ori_yml_contents)
#测试代码
#d = pc.decrypt(e)
#filename = 'trainer/new_trainer.yml'
#with open(filename,'w') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
#    f.write(d)
filename = 'trainer/enc_trainer.yml'
with open(filename,'wb') as f:
    f.write(e)
filename = 'trainer/enc_trainer_bckup.yml'#数据的冗余存储
with open(filename,'wb') as f:
    f.write(e)
#原始模型文件删除
#
my_file = 'trainer/trainer.yml'
if os.path.exists(my_file):
   os.remove(my_file)

# Print the numer of faces trained and end program
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
