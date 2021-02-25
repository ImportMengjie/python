import asyncio
from http.cookies import SimpleCookie
import base64

import aiohttp
import aiofiles
import json
import time
import pickle
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
import re
import random
import PIL.Image
import io
import matplotlib.pyplot as plt
import logging


def random_uniform():
    return str(random.uniform(0, 1))[:-1]


async def login(session: aiohttp.ClientSession, user_config: dict):
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
                        'idhash={}&{}&modid=member::logging'.format(seccode_id, random_uniform())
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
    plt.title(user_config['username'])
    plt.show()

    while True:
        code = input('{} input code：'.format(user_config['username']))
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
        if 'succeed' in code_verify_res:
            break

    # login
    login_post_url = URL + '/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&' \
                           'loginhash={}&inajax=1'.format(login_id)
    login_data = {
        "formhash": from_hash,
        'loginfield': 'username',
        'questionid': '0',
        'answer': '',
        'seccodehash': seccode_id,
        'seccodemodid': 'member::logging',
        'seccodeverify': code,
        'referer': URL + '/forum.php'
    }
    login_data.update(user_config)
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


async def get_level_gift(session: aiohttp.ClientSession, cookies, username: str):
    level_gift_url_online = URL + '/plugin.php?id=levgift:levgift'
    logging.info('{} start get online gift page'.format(username))

    async def get_gift(soup, name, class_):
        await asyncio.sleep(5)
        for table in soup.find_all(name=name, class_=class_):
            award = table.find(text='领取奖励')
            if award:
                get_gift_url = URL + '/' + award.parent['href']
                gift_info = award.parent.parent.parent.parent.text.replace('\n', ' ')
                async with session.get(get_gift_url, headers=HEADERS, cookies=cookies) as response:
                    cookies.update(response.cookies)
                    get_gift_status = response.status
                logging.warning('{} get gift:{}, result:{}'.format(username, gift_info, get_gift_status))

    async with session.get(level_gift_url_online, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        level_gift_online_res = await response.text()
    await get_gift(BeautifulSoup(level_gift_online_res, features="html.parser"), 'table', 'awardcon')

    await asyncio.sleep(10)
    async with session.get(level_gift_url_online + '&acttype=2', headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        level_gift_daily_res = await response.text()
    await get_gift(BeautifulSoup(level_gift_daily_res, features="html.parser"), 'table', 'awardcon')

    await asyncio.sleep(10)
    async with session.get(level_gift_url_online + '&acttype=3', headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        level_gift_daily_res = await response.text()
    await get_gift(BeautifulSoup(level_gift_daily_res, features="html.parser"), 'table', 'awardcon')


async def get_daily_task(session: aiohttp.ClientSession, cookies, id: int, username: str):
    logging.info('{} get task:{} page'.format(username, id))
    task_view_url = URL + '/home.php?mod=task&do=view&id={}'.format(id)
    async with session.get(task_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        task_view_res = await response.text()
    soup = BeautifulSoup(task_view_res, features="html.parser")
    task_url = soup.find(name='img', src=True, alt='立即申请')
    if task_url:
        await asyncio.sleep(5)
        task_url = URL + '/' + task_url.parent['href']
        async with session.get(task_url, headers=HEADERS, cookies=cookies) as response:
            cookies.update(response.cookies)
            logging.warning('{} done task:{}, result:{}'.format(username, id, response.status))


async def lucky_egg_draw(session: aiohttp.ClientSession, cookies, username: str):
    draw_egg_page_url = URL + "/plugin.php?id=levegg:levegg"
    async with session.get(draw_egg_page_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        draw_egg_page_res = await response.text()
    await asyncio.sleep(5)
    soup = BeautifulSoup(draw_egg_page_res, features="html.parser")
    from_hash = soup.find(name='input', attrs={"name": 'formhash', "type": "hidden"})['value']
    draw_egg_num_url = URL + "/plugin.php?id=levegg&m=2&fh={}&{}".format(from_hash, random_uniform())
    async with session.get(draw_egg_num_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        draw_egg_times = json.loads(await response.text())
    logging.warning("{} egg times: {}".format(username, draw_egg_times))
    for egg_name, egg_num in draw_egg_times.items():
        for _ in range(egg_num):
            draw_egg_get_url = URL + "/plugin.php?id=levegg&m=1&{}&egg={}&fh={}".format(random_uniform(), egg_name[-1],
                                                                                        from_hash)
            async with session.get(draw_egg_get_url, headers=HEADERS, cookies=cookies) as response:
                cookies.update(cookies)
                draw_egg_get_res = await response.text()
            logging.warning("{} get {} res: {}".format(username, egg_name, draw_egg_get_res))
            await asyncio.sleep(10)


async def lucky_wheel_draw(session: aiohttp.ClientSession, cookies, username: str):
    wheel_award_map = {
        1: ("Nothing", 0, 0),
        2: ("10积分", 10, 0),
        5: ("100积分", 100, 0),
        7: ("500积分", 500, 0),
        9: ("one more times", 0, 0),
        4: ("50积分", 50, 0),
        8: ("1000积分", 1000, 0),
        11: ("50奖券", 0, 50)
    }
    draw_wheel_page_url = URL + "/plugin.php?id=levaward:award&doingid=1"
    async with session.get(draw_wheel_page_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        draw_wheel_page_res = await response.text()
    await asyncio.sleep(5)
    async with session.get(URL + '/plugin.php?id=levaward:award&doingid=1&mobile=no&hdr=&{}&hook=1&pg=1'.format(
            random_uniform()), headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
    soup = BeautifulSoup(draw_wheel_page_res, features="html.parser")
    from_hash = soup.find(name='input', attrs={"name": 'formhash', "type": "hidden"})['value']
    draw_wheel_num_url = URL + "/plugin.php?id=levaward:l&fh={}&m=_awardnum.1&{}".format(from_hash, random_uniform())
    await asyncio.sleep(5)
    async with session.get(draw_wheel_num_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        draw_wheel_times = int(await response.text())
    if draw_wheel_times > 0:
        total_points, total_coupon = 0, 0
        logging.warning("{} wheel draw num: {}".format(username, draw_wheel_times))
        draw_wheel_url = URL + "/plugin.php?id=levaward:l&fh={}&m=_openaward.1&ajax&_t={}".format(from_hash,
                                                                                                  random_uniform())
        while draw_wheel_times > 0:
            async with session.get(draw_wheel_url, headers=HEADERS, cookies=cookies) as response:
                cookies.update(cookies)
                award_number = int(await response.text())
            if award_number != 9:
                draw_wheel_times -= 1
            award_data = wheel_award_map.get(award_number, ("error", 0, 0))
            logging.warning("{} wheel get num:{} {} point:{}, coupon:{}, left times:{}".format(username, award_number,
                                                                                               award_data[0],
                                                                                               award_data[1],
                                                                                               award_data[2],
                                                                                               draw_wheel_times))
            total_points += award_data[1]
            total_coupon += award_data[2]
            await asyncio.sleep(8)
        logging.error("{} wheel total get points:{}, coupon:{}".format(username, total_points, total_coupon))
    else:
        logging.info("{} wheel draw num == 0".format(username))


async def slot_machine_draw(session: aiohttp.ClientSession, cookies, username: str):
    slot_machine_view_url = URL + '/plugin.php?id=levpop:levpop'
    async with session.get(slot_machine_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        slot_machine_view_res = await response.text()
    soup = BeautifulSoup(slot_machine_view_res, features="html.parser")
    await asyncio.sleep(5)
    slot_times = int(re.search(r'\$\$\("#slotop_infop"\).html\("今日还有 (\d+) 次抽奖机会"\);', slot_machine_view_res)[1])
    logging.info('{} start slot machine left times {}'.format(username, slot_times))
    while slot_times:
        from_hash = soup.find(name='input', attrs={"name": 'formhash', "type": "hidden"})['value']
        get_slot_machine_url = URL + '/plugin.php?id=levpop&m=1&{}&fh={}&_=1614250823971'.format(random_uniform(),
                                                                                                 from_hash,
                                                                                                 int(
                                                                                                     time.time() * 1000))
        async with session.get(get_slot_machine_url, headers=HEADERS, cookies=cookies) as response:
            cookies.update(cookies)
            get_slot_machine_res = await response.text()
        logging.warning('{} get slot machine res: {}'.format(username, get_slot_machine_res))
        slot_times -= 1
        await asyncio.sleep(10)


async def handle_monthly_card(session: aiohttp.ClientSession, cookies, username: str):
    logging.info('{} handle monthly card'.format(username))
    monthly_card_view_url = URL + '/plugin.php?id=yueka'
    async with session.get(monthly_card_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        monthly_card_view_res = await response.text()
    soup = BeautifulSoup(monthly_card_view_res, features="html.parser")
    monthly_card_form = soup.find(name='form', attrs={'name': re.compile(r'form\d'), 'method': 'post', 'action': True})
    if monthly_card_form:
        await asyncio.sleep(5)
        monthly_card_url = URL + '/' + monthly_card_form['action']
        form_hash = monthly_card_form.findChild(name='input')['value']
        async with session.post(monthly_card_url, data={'formhash': form_hash}, headers=HEADERS,
                                cookies=cookies) as response:
            cookies.update(response.cookies)
            monthly_card_res = await response.text()
        logging.warning(
            '{} get monthly card {}, result:{}'.format(username, monthly_card_form.text.strip(),
                                                       monthly_card_res.strip()[:20]))


async def get_credit_dict(session: aiohttp.ClientSession, cookies, _: str):
    home_credit_view_url = URL + '/home.php?mod=spacecp&ac=credit&showcredit=1'
    async with session.get(home_credit_view_url, headers=HEADERS, cookies=cookies) as response:
        cookies.update(response.cookies)
        clock_in_view_res = await response.text()
    soup = BeautifulSoup(clock_in_view_res, features="html.parser")
    credit_sum = soup.find(name='ul', class_='creditl mtm bbda cl').find_all(name='li')
    credit_dict = {}
    for credit in credit_sum:
        split_text = re.search(r'\w+: [0-9]+', credit.text)[0].split(':')
        credit_dict[split_text[0].strip()] = int(split_text[1].strip())
    return credit_dict


async def clock_in(session: aiohttp.ClientSession, cookies, username: str):
    logging.info('{} clock in'.format(username))
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
        logging.info('{} clock in res:{}'.format(username, BeautifulSoup(clock_in_res, features="html.parser").
                                                 find(name='div', class_='c').text))


async def hang_up(user_config: dict, cookies: SimpleCookie):
    username = user_config['username']
    async with aiohttp.ClientSession() as session:
        if not cookies:
            cookies = await login(session, user_config)

        loop_times = 0
        init_credit_dict = await get_credit_dict(session, cookies, username)
        logging.info("{} init credit dict:{}".format(username, init_credit_dict))
        credit_dict = init_credit_dict
        while True:
            await asyncio.sleep(10)
            await clock_in(session, cookies, username)
            await asyncio.sleep(10)
            await get_level_gift(session, cookies, username)
            if loop_times % 5 == 0:
                await asyncio.sleep(10)
                await get_daily_task(session, cookies, 1, username)
                await asyncio.sleep(10)
                await get_daily_task(session, cookies, 2, username)

            if loop_times % 30 == 0:
                await asyncio.sleep(10)
                await slot_machine_draw(session, cookies, username)
                await asyncio.sleep(10)
                await lucky_egg_draw(session, cookies, username)
                await asyncio.sleep(10)
                await lucky_wheel_draw(session, cookies, username)
                await asyncio.sleep(10)
                await handle_monthly_card(session, cookies, username)
            await asyncio.sleep(600 - random.randint(0, 300))
            next_credit_dict = await get_credit_dict(session, cookies, username)
            credit_add_log_text = ''
            for k, v in next_credit_dict.items():
                if v != credit_dict[k]:
                    credit_add_log_text += '{}:{};'.format(k, v - credit_dict[k])
            if credit_add_log_text:
                logging.warning('{} credit modify:{}'.format(username, credit_add_log_text))
            credit_dict = next_credit_dict
            loop_times += 1


async def main(config_path: str, reload: bool):
    async with aiofiles.open(config_path) as fp:
        data = json.loads(await fp.read())
    tasks = []
    tasks_parm = []
    if not data.get('cookies'):
        data['cookies'] = {}
    for account in data["accounts"]:
        username = account['username']
        async with aiohttp.ClientSession() as session:
            if not data['cookies'].get(account['username']) or reload:
                data['cookies'][account['username']] = base64.b64encode(
                    pickle.dumps(await login(session, account))).decode()
            cookies = pickle.loads(base64.b64decode(data['cookies'].get(account['username'])))
            async with session.get(URL + "/plugin.php?id=dsu_paulsign:sign", headers=HEADERS,
                                   cookies=cookies) as response:
                if username not in (await response.text()):
                    async with aiohttp.ClientSession() as new_session:
                        cookies = await login(new_session, account)
                        data['cookies'][account['username']] = base64.b64encode(pickle.dumps(cookies)).decode()
        tasks_parm.append([account, cookies])
    async with aiofiles.open(config_path, 'w') as fp:
        await fp.write(json.dumps(data, indent=4))
    for parm in tasks_parm:
        tasks.append(asyncio.create_task(hang_up(*parm)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Forum hangs up')
    parser.add_argument('-a', '--address', help='forum address', type=str, required=False)
    parser.add_argument('-p', '--password', help='forum password', type=str, required=False)
    parser.add_argument('-u', '--username', help='forum username', type=str, required=False)
    parser.add_argument('-c', '--config', help='config files', type=str, required=False)
    parser.add_argument('-r', '--reload', help='reload', action='store_true')
    parser.add_argument('-l', '--log_level', help='log level=> 10:debug, 20:info, 30:warn, 40:error', type=int,
                        default=20)
    args = parser.parse_args()
    if not args.address:
        with open(args.config, 'r') as fp:
            args.address = URL = json.load(fp)['url']
    URL = ("" if 'http://' in args.address else 'http://') + (
        "" if 'www.' in args.address else 'www.') + args.address
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
    if args.address and args.username and args.password:
        result = loop.run_until_complete(hang_up({'username': args.username, 'password': args.password}, None))
    elif args.config:
        result = loop.run_until_complete(main(args.config, args.reload))
    loop.close()
