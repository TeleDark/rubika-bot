import requests
from time import sleep

class HTTPrequest:
    def __init__(self, url):
        self.connection = self.create_connection(url)
        self.response_code = self.connection.status_code
        self.headers = self.connection.headers
        content_length = self.headers.get("content-length")
        self.buffer_size = int(content_length) if content_length else None

    def create_connection(self, url, received=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }
        if received:
            headers["Range"] = f"bytes={received}-{self.buffer_size}"

        retries = 0
        while retries < 5:
            try:
                connection = requests.get(url, stream=True, headers=headers, timeout=10, allow_redirects=True)
                if connection.status_code == 200:
                    return connection
                else:
                    retries += 1
                    sleep(2)
                    
            except requests.RequestException:
                retries += 1

        raise Exception('Unable to establish a connection!')

    def download(self, file_name: str):
        with open(file_name, 'wb') as file_stream:
            try:
                for data in self.connection.iter_content(chunk_size=500000):
                    file_stream.write(data)
            except Exception as e:
                self.connection.close()
                raise Exception("Download failed")