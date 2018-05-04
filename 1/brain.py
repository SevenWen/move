import time
import os
import translations

def getNextMessage(translator, buffer):
    complete, mData = translator.HasMessage(buffer)
    if not complete:
        return None, buffer
    mt, m, headers, hOff, bLen = mData
    body, buffer = buffer[hOff:hOff+bLen], buffer[hOff+bLen:]
    msg = translator.unmarshallFromNetwork(mt, m, headers, body)
    return msg, buffer

def brainLoop():
    gameSocket = open("game://", "rb+")
#% TEMPLATE-ON
    ccSocketName = "pls://20181.666.2.13:10013"
#% TEMPLATE-OFF
    try:
        ccSocket = open(ccSocketName,"rb+")
    except:
        ccSocket = None

    loop = 0
    timert = 0
    translator = translations.NetworkTranslator()
    hb = None
    gameDataStream = b""

    while True:
        loop += 1
        gameData = os.read(gameSocket.fileno(), 1024) # max of 1024
        gameDataStream += gameData
        if gameDataStream:
            msg, gameDataStream = getNextMessage(translator, gameDataStream)
            if isinstance(msg, translations.BrainConnectResponse):
                translator = translations.NetworkTranslator(*msg.attributes)
                hb = msg
        # if (not gameData) or (not ccData):
        #     timert += 1
        #     if timert%20 == 0:
        #         ccSocket = None
        #         gameSocket = None
        #         gameDataStream = None
        #         msg = None
        #         try:
        #             ccSocket = open(ccSocketName, "rb+")
        #             gameSocket = open("game://", "rb+")
        #         except:
        #             ccSocket = None
        #             gameSocket = None
        if (not gameData) and hb and (loop % 100 == 0) and ccSocket:
            ccSocket = None
            gameSocket = None
            gameDataStream = None
            msg = None
            try:
                ccSocket = open(ccSocketName, "rb+")
            except:
                ccSocket = None


        if (not gameData) and hb and (loop % 10 == 0) and ccSocket:
            try:
                os.write(ccSocket.fileno(), translator.marshallToNetwork(hb))
            except:
                ccSocket = None
            # ccSocket = None
            # every thirty seconds, send heartbeat to cc          
             

        try:            
            if ccSocket:
                ccData = os.read(ccSocket.fileno(), 1024)
            else:
                ccData = b""
        except:
            ccData = b""
            ccSocket = None 

        if gameData and ccSocket:
            try: 
                os.write(ccSocket.fileno(), gameData)
            except:
                ccSocket = None
        if ccData: os.write(gameSocket.fileno(), ccData)

        if not gameData and not gameDataStream and not ccData:
            time.sleep(.5) # sleep half a second every time there's no data
        #if not ccData and not gameDataStrean:
        #    timert += 1
        #    if timert > 30:
        #        ccSocket = None
        #        gameSocket = None
        #    else:
        #        timert = 0    
        if not ccSocket and loop % 20 == 0:
             #if the gamesock didn't open or is dead, try to reconnect
             #once per minute
            ccSocket = None
            try:
                ccSocket = open(ccSocketName, "rb+")
            except:
                ccSocket = None

if __name__=="__main__":
    try:
        brainLoop()
    except Exception as e:
        print("Brain failed because {}".format(e))
        
        f = open("/tmp/error.txt","wb+")
        f.write(str(e).encode())
        f.close()

