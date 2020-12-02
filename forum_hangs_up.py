import asyncio
import aiohttp
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
import re
import random
import PIL.Image
import io
import matplotlib.pyplot as plt
import logging


async def login(session: aiohttp.ClientSession, username: str, password: str):
    # get login page
    login_url = URL + '/member.php?mod=logging&action=login&infloat=yes' \
                      '&handlekey=login&inajax=1&ajaxtarget=fwin_content_login'
    async with session.get(login_url, headers=HEADERS) as response:
        login_res = await response.text()
        cookies = response.cookies
    # handle login page
    soup = BeautifulSoup(et.fromstring(login_res).text, features="html.parser")
    seccode_id = soup.find(name='span', id=re.compile('seccode_\\w+'))['id'].split('_')[1]
    login_id = soup.find(name='form', class_='cl', id=re.compile('loginform_\\w+'))['id'].split('_')[1]
    from_hash = soup.find(name='input', attrs={"name": 'formhash', "type": "hidden"})['value']

    # get img url
    seccode_url = URL + '/misc.php?mod=seccode&action=update&' \
                        'idhash={}&{}&modid=member::logging'.format(seccode_id, str(random.uniform(0, 1))[:-1])
    async with session.get(seccode_url, headers=HEADERS, cookies=cookies) as response:
        seccode_res = await response.text()
        cookies.update(response.cookies)

    # get img
    seccode_img_url = URL + '/' + \
                      re.search(r'src="misc.php\?mod=seccode&update=\d+&idhash=\w+"', seccode_res).group(
                          0).split('"')[1]
    headers = {
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }
    headers.update(HEADERS)
    async with session.get(seccode_img_url, headers=headers, cookies=cookies) as response:
        cookies.update(response.cookies)
        seccode_img = await response.read()
    plt.imshow(PIL.Image.open(io.BytesIO(seccode_img)))
    plt.show()
    code = input('input code：')

    # verify code
    code_verify_url = URL + '/misc.php?mod=seccode&action=check&inajax=1&modid=member::logging&' \
                            'idhash={}&secverify={}'.format(seccode_id, code)
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    }
    headers.update(HEADERS)
    async with session.get(code_verify_url, headers=headers, cookies=cookies) as response:
        code_verify_res = await response.text()
        cookies.update(response.cookies)
        logging.warning('code verify res:{}'.format(et.fromstring(code_verify_res).text))

    # login
    login_post_url = URL + '/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&' \
                           'loginhash={}&inajax=1'.format(login_id)
    login_data = {
        "formhash": from_hash,
        'username': username,
        'password': password,
        'loginfield': 'username',
        'questionid': '0',
        'answer': '',
        'seccodehash': seccode_id,
        'seccodemodid': 'member::logging',
        'seccodeverify': code,
        'referer': URL + '/forum.php'
    }
    headers = {
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": URL,
        "Upgrade-Insecure-Requests": "1",
    }
    headers.update(HEADERS)
    async with session.post(login_post_url, data=login_data, headers=headers, cookies=cookies) as response:
        login_post_res = await response.text()
        logging.warning('login res: {}'.format(et.fromstring(login_post_res).text))
        cookies.update(response.cookies)
    return cookies


async def get_level_gift(session: aiohttp.ClientSession, cookies):
    level_gift_url_online = URL + '/plugin.php?id=levgift:levgift'
    logging.info('start get online gift page')

    async def get_gift(soup, name, class_):
        for table in soup.find_all(name=name, class_=class_):
            award = table.find(text='领取奖励')
            if award:
                get_gift_url = URL + '/' + award.parent['href']
                gift_info = award.parent.parent.parent.parent.text.replace('\n', ' ')
                async with session.get(get_gift_url) as response:
                    cookies.update(response.cookies)
                    get_gift_status = response.status
                logging.warning('get gift:{}, result:{}'.format(gift_info, get_gift_status))

    async with session.get(level_gift_url_online, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        level_gift_online_res = await response.text()
    await get_gift(BeautifulSoup(level_gift_online_res, features="html.parser"), 'table', 'awardcon')

    async with session.get(level_gift_url_online + '&acttype=2', headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        level_gift_daily_res = await response.text()
    await get_gift(BeautifulSoup(level_gift_daily_res, features="html.parser"), 'table', 'awardcon')


async def get_daily_task(session: aiohttp.ClientSession, cookies, id: int):
    logging.info('get task:{} page'.format(id))
    task_view_url = URL + '/home.php?mod=task&do=view&id={}'.format(id)
    async with session.get(task_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        task_view_res = await response.text()
    soup = BeautifulSoup(task_view_res, features="html.parser")
    task_url = soup.find(name='img', src=True, alt='立即申请')
    if task_url:
        task_url = URL + '/' + task_url.parent['href']
        async with session.get(task_url, headers=HEADERS, cookies=cookies) as response:
            cookies.update(response.cookies)
            logging.warning('done task:{}, result:{}'.format(id, response.status))


async def clock_in(session: aiohttp.ClientSession, cookies):
    logging.info('clock in')
    clock_in_view_url = URL + '/plugin.php?id=dsu_paulsign:sign'
    async with session.get(clock_in_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        clock_in_view_res = await response.text()
    soup = BeautifulSoup(clock_in_view_res, features="html.parser")
    clock_in_url = soup.find(name='form', attrs={'name': 'qiandao', 'method': 'post', 'action': True})
    if clock_in_url:
        clock_in_url = URL + '/' + clock_in_url['action']
        form_hash = soup.find(name='input', attrs={'name': 'formhash', 'type': 'hidden', 'value': True})['value']
        data = {
            'formhash': form_hash,
            'qdxq': 'kx'
        }
        async with session.post(clock_in_url, data=data, headers=HEADERS, cookies=cookies) as response:
            cookies.update(response.cookies)
            clock_in_res = await response.text()
        logging.info('clock in res:{}'.format(BeautifulSoup(clock_in_res, features="html.parser").
                                              find(name='div', class_='c').text))


async def main(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        cookies = await login(session, username, password)

        while True:
            await get_level_gift(session, cookies)
            await asyncio.sleep(50)
            await get_daily_task(session, cookies, 1)
            await asyncio.sleep(10)
            await get_daily_task(session, cookies, 2)
            await asyncio.sleep(20)
            await clock_in(session, cookies)
            await asyncio.sleep(600)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Forum hangs up')
    parser.add_argument('-a', '--address', help='forum address', type=str, required=True)
    parser.add_argument('-p', '--password', help='forum password', type=str, required=True)
    parser.add_argument('-u', '--username', help='forum username', type=str, required=True)
    parser.add_argument('-l', '--log_level', help='log level=> 10:debug, 20:info, 30:warn, 40:error', type=int,
                        default=20)
    args = parser.parse_args()
    URL = ("" if 'http://' in args.address else 'http://') + ("" if 'www.' in args.address else 'www.') + args.address
    HEADERS = {
        'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                      r'Chrome/86.0.4240.198 Safari/537.36',
        "DNT": "1",
        "Referer": URL + "/forum.php",
        "Connection": "keep-alive",
        "Accept-Language": "zh-CN,zh;q=0.9,zh-TW;q=0.8"
    }

    logging.basicConfig(level=args.log_level, format='%(asctime)s-%(levelname)s-%(message)s')
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(args.username, args.password))
    loop.close()
