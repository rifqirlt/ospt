

def list2int(lsresp):         
    return int("".join("%2.2x" % c for c in lsresp),16)
    

def int2list(bigint,**kwargs):
    if(isinstance(bigint,int) is not True):
        raise RuntimeError("argument must be Integer type")
    size = (bigint.bit_length()+7)//8
    if('size' in kwargs):
        size = kwargs['size']
        
    return memoryview(bigint.to_bytes(size,'big')).tolist()
    
    
def bytes2list(buffer,**kwargs):
    if(isinstance(buffer,bytes) is not True):
        raise RuntimeError("argument must be bytes type")
    return memoryview(buffer).tolist()    
    
bytes2int = lambda buffer: list2int(buffer)    

def ROTL48(inp):
    msb = inp >> 47
    retval = (inp << 1)| msb
    return retval & 0xFFFFFFFFFFFF
    


def NLM(x,y):
    """
    Taken from
    The Cipurse specification of Cryptographic Protocol : 7.1 NLM software architecture 
    """
    f1 = 0x35B088CCE173
    RED = [0x000000000000,f1^0x000000000001]
    MUL = [0x000000000000,x&0xFFFFFFFFFFFF]
    Y = y & 0xFFFFFFFFFFFF
    R = 0x000000000000
    for i in range(48):
        R = ROTL48(R)
        idx = R & 0x000000000001
        R = R ^ RED[idx]
        Y = ROTL48(Y)
        idx = Y & 0x000000000001
        R = R ^ MUL[idx]
    
    return R
        
def Extract_RP(piccresp):
    #do verifyinput
    return piccresp[0:16]
    

def Extract_rp(piccresp):
    #doverifiyinput
    return piccresp[16:22]


def PAD2(listin):
    if(isinstance(listin,int) is not True):
        raise RuntimeError("argument of PAD2 must be int type")  
    
    ls = int2list(listin,size=6)
    ret = [0x00,0x00,0x00,0x00]
    ret.extend(ls)
    ret.extend(ls)
    return ret
    
def PAD(listin):
    if(type(listin) == 'int'):
        listin = int2list(listin,size=6)
    ret = [0,0,0,0,0,0,0,0,0,0]
    ret.extend(listin)
    return ret
    

def XOR128(x,y):
    if(isinstance(x,list) is not True):
        raise RuntimeError("argument 'x' must be list type")
        
    if(isinstance(y,list) is not True):
        raise RuntimeError("argument 'y' must be list type")        
        
    res = list2int(x) ^ list2int(y)
    return int2list(res,size=16)
    
    
if __name__ == '__main__':
    print("testing NLM")
    x = 0x204b45592031
    y = 0x3c68f4c738b7
    nlm = NLM(x,y)
    print("%X" % nlm)
    lsnlm = int2list(nlm)
    print(lsnlm)