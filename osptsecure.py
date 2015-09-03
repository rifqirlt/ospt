from osptutil import *
from Crypto.Cipher import AES

#Precondition
RT = [0x0C,0x0F,0x8D,0x73,0x64,0x61,0x6E,0x16,0xBD,0xD0,0xE4,0xF0,0x71,0x9C,0x5C,0x72]
rt = [0x49,0x7F,0x74,0x13,0x18,0xBA]
KID = [0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73, 0x73]
K0 = []

def mutual_auth(RP,rp):
    global K0
    #Calculate NLM
    nlmin = KID[10:16]
    nlmin = list2int(nlmin)
    kp = NLM(nlmin,list2int(rp))
    preaesin1 = PAD2(kp)
    preaesin2 = PAD(rt)
    aesinput = XOR128(preaesin1,preaesin2)
    cipher = AES.new(bytes(aesinput),AES.MODE_ECB)
    K0_pre = cipher.encrypt(bytes(KID))
    K0_pre = bytes2list(K0_pre)
    K0 = XOR128(K0_pre,KID)
    cipher = AES.new(bytes(K0),AES.MODE_ECB)
    CP = cipher.encrypt(bytes(RP))
    return bytes2list(CP)
    
    
def validate_sessionkey(skey):
    global K0
    intkey = list2int(skey)
    cipher = AES.new(bytes(K0),AES.MODE_ECB)
    ct = cipher.encrypt(bytes(RT))
    intct = bytes2int(ct)
    
    if(intct == intkey):
        return True
        
    return False