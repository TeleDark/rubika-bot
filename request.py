import requests
from time import time
import time as tmdd
class HTTPrequest:
    def __init__(self,url):
        self.con = self.create_connection(url)
        self.response_code = self.con.status_code
        self.headers = self.con.headers
        lnd = self.headers.get("content-length")
        self.buffer_size = (int(lnd) if lnd != None else None)
    def create_connection(self,url,rcvd=None):
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }
        if rcvd:
            headers["Range"] = "bytes="+str(rcvd)+"-"+str(self.buffer_size)
        trd = 0
        while True:
            try:
                con = requests.get(url,stream=True,headers=headers,timeout=10,allow_redirects=True)
                if con.status_code == 200:
                    return con
                else:
                    trd += 1
                    tmdd.sleep(2)
            except:
                trd += 1
            if trd > 5:
                raise Exception('cant connect !')
    def download(self,file_name:str):
        file_stream = open(file_name,'wb')
        try:
            for data in self.con.iter_content(chunk_size=500000):
                file_stream.write(data)
        except Exception as e:
            self.con.close()
            file_stream.close()
            raise Exception("")
        
        file_stream.close()
