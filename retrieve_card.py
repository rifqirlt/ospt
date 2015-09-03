import osptutil as OSPTUTIL
import osptsecure as sec
import scard


# Table CRC32 akan diiisi saat pemanggilan crc32 pertamakali'
import scard
import time

class ReadError(Exception):
    def __init__(self,msg,addr,value):
        super(ReadErrorException,self).__init__(msg)
        self.__addr__ = addr
        self.__value__ = value

    def get_addr(self):
        return self.__addr__
    
    def get_value(self):
        return self.__value__


class WriteErrorException(Exception):
    def __init__(self,msg,addr,val,banknum):
        super(WriteError,self).__init__(msg)
        self.__addr__ = addr
        self.__value__ = val
        self.__banknum__ = banknum

    def get_value(self):
        return self.__value__

    def get_addr(self):
        return self.__addr__

    def get_banknum(self):
        return self.__banknum__

        
class APDUError(Exception):
    def __init__(self,msg,apdu,status,expected):
        super(APDUError,self).__init__(msg)
        self.__apdu__ = apdu
        self.__status__ = status
        self.__expected__ = expected            
        
    def get_apdu(self):
        return self.__apdu__
            
    def get_status(self):
        return self.__status__
        
    def get_expected(self):
        return self.__expected__            


class EraseAllErr(APDUError):
    def __init__(self,apdu,status,expected):
        super(EraseAllErr,self).__init__("Erase All Error",apdu,status,expected)


class SelectBankErr(APDUError):
    def __init__(self,apdu,status,expected,banknum):
        super(SelectBankErr,self).__init__("Select Bank Error",apdu,status,expected)
        self.__bnknum__ = banknum

        
    def get_banknum(self):
        return self.__banknum__


        
class AnimateProcess:
    def __init__(self,szprocname):
        self.__szproc__ = szprocname
        self.__counter__ = 0
        self.__animap__ = {0: '|', 1:'/', 2:'-', 3:'\\'}
    
    def __exit__(self,type,value,traceback):
        self.end()
        
        
    def begin(self):
        print(self.__szproc__ + ":   ",end="",flush=True)


    def animate(self):
        print('\x08',end="",flush=True)
        print("%s" % self.__animap__[self.__counter__],end="",flush=True)
        self.__counter__ +=1
        if(self.__counter__ == 4):
            self.__counter__ = 0
        

    def end(self):
        for x in range(3):
            print("\x08",end="",flush=True)
        print(" FINISHED")
        
        
        
def erase_all(con):
    payload = bytearray([0x51,0x02,0x00,0x00,0x01,0xff])
    resp = con.transceive(payload)
    if(get_response_status(resp) != 0x9000):
        raise EraseAllErr(payload,get_response_status(resp),0x9000)



def erase_sector(con,sector):
    sctmsb = (sector>>8) & 0xff
    sctlsb = sector & 0xff
    payload = bytearray([0x51,0x02,0x00,0x00,0x02,sctmsb,sctlsb])
    resp = con.transceive(payload)
    status = get_response_status(resp)
    if( status != 0x9000):
        raise APDUError("Erase Sector's Error",payload,status,0x9000)

        
def select_bank(con,number):
    payload = bytearray([0x51,0x06,0x00,0x00,0x01,number])
    resp = con.transceive(payload)
    if(get_response_status(resp) != 0x9000):
        raise SelectBankErr(payload,get_response_status(resp),0x9000,number)

        
"""
Blocking until theres "connected" state on card reader
"""
def waittoconnect(con):
    while(1):
        state = con.readerstate()
        if(state.eventstate & scard.SCARD_STATE_INUSE):
            #DON'T PUT sleep in here just continue the loop!!
            continue
        if(state.eventstate & scard.SCARD_STATE_PRESENT):
            break
    time.sleep(0.5)
    
    
"""
Blocking until there is "disconnected" state on card reader
"""
def waittodisconnect(con):
    while(1):
        state = con.readerstate()
        if(state.eventstate & scard.SCARD_STATE_INUSE):
            #DON'T PUT sleep in here just continue the loop!!
            continue
        if(state.eventstate & scard.SCARD_STATE_EMPTY):
            break
    time.sleep(0.5)
    
    
def get_response_status(lsresp):
    if(isinstance(lsresp,bytes) == False):
        raise TypeError("Input should be list of bytes")
    if(len(lsresp) < 2):
        raise RuntimeError("Length input too little")
        
    return int("".join("%2.2x" % c for c in lsresp[len(lsresp)-2:]),16)

    
def get_response_data(lsresp):
    if(isinstance(lsresp,bytes) == False):
        raise TypeError("Input should be list of bytes")
    if(len(lsresp) < 2):
        raise RuntimeError("Length input too little")
        
    return lsresp[0:len(lsresp)-2]

def cleanup(val,con):
    print()
    print("Untapped card to disconnect")
    waittodisconnect(con)
    print("disconnect")
    con.disconnect()
    exit(-1)

    
if __name__ == '__main__':
    ctx = scard.context()
    con = ctx.connector(0)
    print()
    print("Tap CIPURSE Smart Card")
    waittoconnect(con)
    con.connect()
    print()
    print("Select File --> 00 A4 00 00 02 3F 00 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x3F,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File --> 00 A4 00 00 02 2F F7")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x2F,0xF7])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read Binary --> 00 B0 00 00 00")
    apdu = bytes([0x00,0xB0,0x00,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select MF --> 00 A4 00 00")
    apdu = bytes([0x00,0xA4,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read File Attributes --> 80 CE 00 00 00")
    apdu = bytes([0x80,0xCE,0x00,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by FID --> 00 A4 00 00 02 2F F1 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x2F,0xF1,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read File Attributes --> 80 CE 00 00 00")
    apdu = bytes([0x80,0xCE,0x00,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read Binary --> 00 B0 00 00 C8")
    apdu = bytes([0x00,0xB0,0x00,0x00,0xC8])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by FID --> 00 A4 00 00 02 2F f7 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x2F,0xf7,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read File Attributes --> 80 CE 00 00 00")
    apdu = bytes([0x80,0xCE,0x00,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read Binary --> 00 B0 00 00 C8")
    apdu = bytes([0x00,0xB0,0x00,0x00,0xC8])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by FID --> 00 A4 00 00 02 2F F3 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x2F,0xF3,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read File Attributes --> 80 CE 00 00 00")
    apdu = bytes([0x80,0xCE,0x00,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Read Binary --> 00 B0 00 00 C8")
    apdu = bytes([0x00,0xB0,0x00,0x00,0xC8])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by FID --> 00 A4 00 00 02 3F 00 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x3F,0x00,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by AID --> 00 A4 04 00 10 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 00")
    apdu = bytes([0x00,0xA4,0x04,0x00,0x10,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x11,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))
    print()
    print("Select File by FID --> 00 A4 00 00 02 30 00")
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x30,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))	
    #apdu = bytes([0x80,0xce,0x00,0x00,0x00])
    #esp = con.transceive(apdu)
    #print("<-- " + "".join("%2.2X " % c for c in resp))
    
    """
    apdu = bytes([0x00,0xA4,0x00,0x00,0x02,0x38,0x00])
    resp = con.transceive(apdu)
    print("<-- " + "".join("%2.2X " % c for c in resp))    
    """
    
    
    cleanup(0,con)
        
    