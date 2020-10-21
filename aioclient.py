import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


class AioClient:

    def __init__(self, cp):
        self.cp = cp
        self.username = self.cp.get('username')
        self.password = self.cp.get('password')
        self.lang = self.cp.get('lang')
        self.url = self.cp.get('url')

    async def getcookie(self):
        async with aiohttp.ClientSession() as client:
            async def getpara():
                async with client.get(self.url) as RESP:
                    htmldoc = await RESP.text()
                    soup = BeautifulSoup(htmldoc, features="html.parser")
                    uid = soup.find('input')['value']
                    postdata = {
                        "uid": uid,
                        "username": self.username,
                        "pwd": self.password,
                        "language": self.lang,
                        "action": "GoLogin"
                    }
                    return postdata

            async with client.post(self.url, data=await getpara()) as resp:
                cookie = resp.cookies
        return cookie

    async def fetch(self, client, myurl, mydata):
        async with client.post(myurl, data=mydata) as resp1:
            htmldoc = await resp1.text()
            datasoup = BeautifulSoup(htmldoc, features="html.parser")
            pds = [pd.read_html(str(table))[0].dropna(axis=1, how="all") for table in
                   datasoup.find_all('table', text=None, recursive=True, attrs={"class": "data"})]
            return pds
