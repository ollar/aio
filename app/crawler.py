import asyncio
import aiohttp
import urllib.parse
import pdb
import json
import datetime
import sqlite3


class Crawler():
    BASE_URL = 'https://devapicorreqts.bssys.com/api/v1/'
    TOKEN_LINK = 'auth/tokens'
    ACCESS_TOKEN = None
    GET_LINKS = [
        'configs',
        'currencies/rates/exchange',
        'news?_sort=beginShowDate-&_sort=dateTime-',
        'banners?isMobile=true',
        'points/types',
        'points/operationTypes',
        'points?_offset=0&_limit=1000',
        'cards'
    ]
    POST_LINKS = [

    ]

    def __init__(self, base_url=None, *args, **kwargs):
        if base_url:
            self.BASE_URL = base_url
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')

        self.db = kwargs.get('db')
        self.cursor = kwargs.get('cursor')

    async def __call__(self):
        if not self.ACCESS_TOKEN:
            await self.request_token()
        await self.login(requisites={'username': self.username, 'password': self.password})
        await self.fetch_multiple_pages(self.GET_LINKS)

    async def request_token(self):
        token = await self.fetch_page(self.TOKEN_LINK, _fetching_token=True)
        self.ACCESS_TOKEN = token['authToken']

    async def login(self, requisites):
        await self.fetch_page('auth/login', method='post', data=requisites)

    async def fetch_page(self, url, method='get', _fetching_token=False, data={}):
        if not self.ACCESS_TOKEN and not _fetching_token:
            print(self.ACCESS_TOKEN)
            await self.request_token()

        headers = {}

        if self.ACCESS_TOKEN:
            headers = {
                'authToken': self.ACCESS_TOKEN,
                'deviceId': '2f653a8e-e336-4312-bf34-a76cd9eb4631',
                'deviceType': 'MOBILE'
            }

        full_url = urllib.parse.urljoin(self.BASE_URL, url)
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(full_url, headers=headers, data=json.dumps(data)) as response:
                print(full_url, response.status)

                if response.status != 200:
                    print('OOps, something wrong')
                    print(await response.text())
                    return

                resp = await response.json()

                if resp.get('result') == False:
                    print(resp)
                    return

                self.dump_data(url, resp)

                return resp

    async def fetch_multiple_pages(self, sources=[]):
        tasks = []

        for url in sources:
            tasks.append(self.fetch_page(url))

        self.running_group = asyncio.gather(*tasks)
        await self.running_group

    def _get_entry(self, stubbed_url):
        self.cursor.execute("""SELECT *
                            FROM stubs
                            WHERE stubbed_url=?""",
                            (stubbed_url,))
        return self.cursor.fetchone()

    def dump_data(self, url, data):
        stub = self._get_entry(url)

        if stub:
            try:
                self.cursor.execute("""UPDATE stubs
                                       SET stubbed_url = ?,
                                           content = ?,
                                           timestamp = ?,
                                           ip = ?
                                       WHERE stubbed_url =? """, (
                                            url,
                                            json.dumps(data),
                                            str(datetime.datetime.now()),
                                            'ip here',
                                            url,))

                self.db.commit()
            except sqlite3.IntegrityError:
                print('sqlite3.IntegrityError')
                # return web.HTTPFound(self.edit_stub_url)

            except:
                print('OOps, an error occupied, sorry')
                # flash(self._request, "OOps, an error occupied, sorry", "error")
        else:
            try:
                # # Insert a row of data
                self.cursor.execute("""INSERT INTO stubs (
                        stubbed_url,
                        content,
                        timestamp,
                        ip
                    ) VALUES (?,?,?,?)""", (
                        url,
                        json.dumps(data),
                        str(datetime.datetime.now()),
                        # request.remote_addr)
                        'ip here')
                    )
                self.db.commit()

            except sqlite3.IntegrityError:
                print("Such stub already exists")
                # flash(self._request, "Such stub already exists", "error")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    crawler = Crawler(loop=loop)
    loop.run_until_complete(crawler())
    loop.close()
