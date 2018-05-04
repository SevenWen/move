import os

root = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(os.path.dirname(root))

print(path)
def getPrivateKeyForAddr(addr):
    if addr == "20181.2.2.2":
        with open(path + "/certs/ccpriv.key") as fp:
            server_key = fp.read()
        fp.close()
        return server_key
    if addr == "20181.2.2.3":
        with open(path + "/certs/city_privkey") as fp:
            client_key = fp.read()
        fp.close()
        return client_key

    return None


def getCertsForAddr(addr):
    certs = []
    if addr == "20181.2.2.2":
        with open(path + "/certs/ccpriv.key", "rb") as fp:
            certs.append(fp.read())
        fp.close()
        # with open(path + "/certs/signed.cert", "rb") as fp:
        #     certs.append((fp.read()))
        # fp.close()
        return certs
    if addr == "20181.2.2.3":
        with open(path + "/certs/city_privkey", "rb") as fp:
            certs.append(fp.read())
        fp.close()
        # with open(path + "/certs/signed.cert", "rb") as fp:
        #     certs.append((fp.read()))
        # fp.close()
        return certs
    # if addr == "20181.666.2.15":
    #     with open(path + "/certs/15.cert", "rb") as fp:
    #         certs.append(fp.read())
    #     fp.close()
    #     with open(path + "/certs/signed.cert", "rb") as fp:
    #         certs.append((fp.read()))
    #     fp.close()
    #     return certs
    # if addr == "20181.666.2.16":
    #     with open(path + "/certs/16.cert", "rb") as fp:
    #         certs.append(fp.read())
    #     fp.close()
    #     with open(path + "/certs/signed.cert", "rb") as fp:
    #         certs.append((fp.read()))
    #     fp.close()
    #     return certs
    return None


def getRootCert():
    with open(path + "/certs/rootCA.crt", "rb") as fp:
        cert = fp.read()
    fp.close()
    return cert

#--
