import copy
# 计算程序运行的时间
import json
import threading
import time
import re
from tkinter.messagebox import showinfo

import xlrd
from xlutils.copy import copy
import urllib
import requests
from bs4 import BeautifulSoup
import lxml
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename

start = time.clock()

searchURL = "http://www.baidu.com/s?&wd={}&pn={}"
header = {
    'user-Agent': r'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}


# 打开excel，返回内容
def get_companylist(filename: str, column: int, start_row=0, end_row=None, sheet=0):
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(sheet)
    clos = sheet.col_values(column, start_row, end_row)
    try:
        clos2 = sheet.col_values(column + 2, start_row, len(clos))
    except BaseException as e:
        return clos
    return list(map(lambda x, y: x if not y else None, clos, clos2))


def write_to_excel(filename: str, row_num: int, companylist: list, joblist: list):
    workbook = copy(xlrd.open_workbook(filename))
    ws = workbook.get_sheet(0)
    ws.write(row_num, 2, ','.join(companylist))
    ws.write(row_num, 3, ','.join(joblist))
    workbook.save(filename)


def get_response(keyword: str, pagenum=0, tex=None):
    response = ''
    while True:
        try:
            url = searchURL.format(urllib.parse.quote(keyword), pagenum * 10)
            response = requests.get(url, header)
            break
        except BaseException as e:
            print(e)
            if tex:
                tex.insert(1.0, "休息5毫秒,尝试重连")
            time.sleep(5)
            continue
    return response


def parse_response(response: str):
    soup = BeautifulSoup(response, 'lxml')
    return soup.find_all(class_='result c-container ')


def find_hyperlink(bcontext):
    t1 = bcontext.find_all('a')
    t2 = t1[0].get("href")
    return t2


def to_string(nostring):
    return ''.join(map(str, nostring))


# 匹配对应的字符串
def find_string(fatstring, sonstring: str):
    tostr = to_string(fatstring)
    if (tostr.find(sonstring) != -1):
        return True
    else:
        return False


def get_job_qiancwy(url):
    for i in range(0, 4):
        response = requests.get(url, header)
        response.encoding = 'utf-8'
        if response.ok:
            break
        time.sleep(5)
    else:
        return []
    soup = BeautifulSoup(response.text, 'lxml')
    k = soup.find_all(class_=' zw-name')
    totalPage = 0
    if soup.find(id='hidTotal') == None:
        totalPage = 1
    else:
        totalPage = int(soup.find(id='hidTotal')['value'])
    maxPage = totalPage // 20 + 1 if totalPage % 20 > 0 else 0
    if totalPage == 1:
        return list(map(lambda i: i['title'], k))
    else:
        ajaxUrl = soup.find(id='hidAjax')['value']
        ret = list(map(lambda i: i['title'], k))
        data = {'pageno': '', 'hidTotal': str(totalPage)}
        header2 = {
            'content-type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': '*/*',
            'user-Agent': r'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        for i in range(2, maxPage + 1):
            data['pageno'] = i
            response = requests.post(ajaxUrl, data=data, headers=header2)
            soup = BeautifulSoup(response.text, 'lxml')
            soup = soup.find_all(class_=" zw-name")
            k = list(map(lambda i: i['title'], soup))
            ret.extend(k)
    return ret


def get_job_liepin(url: str):
    for i in range(0, 4):
        response = requests.get(url, header)
        response.encoding = 'utf-8'
        if response.ok:
            break
        time.sleep(5)
    else:
        return []
    soup = BeautifulSoup(response.text, 'lxml')
    # print(response.url)
    if not 'liepin.com' in response.url or 'job' in response.url:
        temp = soup.find(class_='title-info ')
        if temp and temp.h3 and temp.h3.a:
            return get_job_liepin(temp.h3.a['href'])
        return []
    if soup.find(class_='list clearfix'):
        return []
    joblist = soup.find_all(class_='title')
    maxPage = soup.find(class_='addition')
    if maxPage:
        maxPage = int(maxPage.text[1:maxPage.text.find('页')])
    else:
        maxPage = 0
    ret = list(map(lambda i: i['title'], joblist))
    if maxPage == 0:
        return ret
    cid = url.strip().split('/')
    cid = cid[-2] if cid[-1] == '' else cid[-1]
    data = {'ecompIds': cid, 'pageSize': '15', 'curPage': 0, 'keywords': '', 'dp': '', 'deptId': ''}
    header2 = {
        'content-type': r'application/x-www-form-urlencoded',
        'X-Requested-With': r'XMLHttpRequest',
        'Accept': r'application/json, text/javascript, */*; q=0.01',
        'user-Agent': r'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    for i in range(1, maxPage):
        data['curPage'] = i
        response = requests.post('https://www.liepin.com/company/sojob.json', data=data, headers=header2)
        response.encoding = 'utf-8'
        if not response.ok:
            continue
        job_info = json.loads(response.text)['data']
        for j in job_info['list']:
            ret.append(j['title'])
    return ret


def get_job_zhilian(url):
    joblist = []
    for i in range(0, 4):
        response = requests.get(url, header)
        response.encoding = 'utf-8'
        if response.ok:
            break
        time.sleep(5)
    else:
        return []
    pattern = r'.*?(CC.*?)\.htm'
    compid = re.search(pattern, response.url)
    if compid == None:
        return []
    url = "http://sou.zhaopin.com/jobs/companysearch.ashx"
    i = 1
    while (1):
        par = {'CompID': compid.group(1), 'p': '1'}
        par['p'] = str(i)
        i = i + 1
        response = requests.get(url, headers=header, params=par)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        job = soup.find_all('td', attrs={'class': 'zwmc'})
        if job == []:
            break
        joblist.extend(list(map(lambda i: i.find('div').a.string, job)))
    return joblist


def get_job_chinahr(url: str):
    for i in range(0, 4):
        response = requests.get(url, header)
        response.encoding = 'utf-8'
        if response.ok:
            break
        time.sleep(5)
    else:
        return []
    soup = BeautifulSoup(response.text, 'lxml')
    return list(map(lambda l: l.a.string, soup.find_all(class_='exj-e1')))


def get_job_nantong(url):
    for i in range(0, 4):
        response = requests.get(url, header)
        response.encoding = 'utf-8'
        if response.ok:
            break
        time.sleep(5)
    else:
        return []
    soup = BeautifulSoup(response.text, 'lxml')
    if 'job' in response.url:
        t = soup.find(class_='title-info')
        if t and t.h3 and t.h3.a:
            url = t.h3.a['href']
            if 'www.ntrc.cn' not in url:
                url = 'http://www.ntrc.cn' + url
            return get_job_nantong(url)
        if t and t.h1 and t.h1['title']:
            return [t.h1['title']]
        return []
    k = soup.find_all(class_="job-info col-md-10")
    l = list(map(lambda i: i.find('h3').a['title'], k))
    return l


recruit = [('南通人才网', get_job_nantong), ("猎聘网", get_job_liepin), ("前程无忧", get_job_qiancwy), ("智联", get_job_zhilian),
           ("中华英才网", get_job_chinahr)]


def start_job(excel: str, tex, recruit: list, page_length=3):
    if 'xlsx' in excel:
        showinfo('警告:', '警告:请一定要将excel保存为xls格式!!!')
        return
    try:
        companylist = get_companylist(excel, 0)
    except BaseException as e:
        tex.insert(2.0, "excel不能打开\n")
        print(e)
        return
    tex.insert(1.0, "一共%d个公司" % (len(companylist, )))
    for com in range(0, len(companylist)):
        if not companylist[com]:
            tex.insert(1.0, "(%d/%d),已有数据,跳过\n" % (com + 1, len(companylist)))
            continue
        job_list = []
        com_num = []
        for page in range(page_length):
            res = get_response("\"" + companylist[com] + " 招聘\"", page, tex=tex)
            context = parse_response(res.text)
            tex.insert(1.0, "(%d/%d),开始%s公司，百度第%s页.\n" % (com + 1, len(companylist), companylist[com], page,))
            for rec in range(0, len(recruit)):
                for search_res in context:
                    if find_string(search_res, recruit[rec][0]):
                        url = find_hyperlink(search_res)
                        try:
                            if str(rec + 1) not in com_num:
                                tex.insert(1.0, "保存%s的招聘信息\n" % recruit[rec][0])
                                temp = recruit[rec][1](url)
                                job_list.extend(temp)
                                tex.insert(1.0, "%s:找到%d个数据\n" % (recruit[rec][0], len(temp)))
                                if temp:
                                    com_num.append(str(rec + 1))
                                    break
                        except BaseException as e:
                            print(e)
        try:
            if not com_num or not job_list:
                com_num = ['6']
            write_to_excel(excel, com, com_num, job_list)
        except BaseException as e:
            tex.insert(2.0, "excel不能打开\n")
            print(e)
    showinfo('生成完毕', '生成完毕')


class APP:
    def __init__(self, master):
        self.path = tk.StringVar()
        tk.Label(master, text="打开文件:").grid(row=0, column=0, padx=0)
        tk.Entry(master, textvariable=self.path, width=30).grid(row=0, column=1)
        tk.Button(master, text="路径选择", width=17, command=self.selectPath).grid(row=0, column=2)
        self.start_button = tk.Button(master, text="开始", width=17, command=self.start)
        self.start_button.grid(row=0, column=3, sticky="e")
        self.tex = tk.Text(master)
        self.tex.grid(row=1, column=0, columnspan=4)
        for i in range(0, len(recruit)):
            self.tex.insert(1.0, 'num:%d==>%s\n' % (i + 1, recruit[i][0]))
        self.tex.insert(1.0, 'num:6==>None\n')

    def selectPath(self):
        path_ = askopenfilename()
        self.path.set(path_)
        self.start_button['state'] = 'normal'

    def start(self):
        self.start_button['state'] = 'disable'
        f = threading.Thread(target=start_job, args=(self.path.get(), self.tex, recruit,))
        f.start()


root = tk.Tk()
root.title("招聘信息管理")
app = APP(root)
root.mainloop()
# print(get_job_liepin('https://www.liepin.com/company/gs11665820/'))
# print(get_job_liepin('http://www.baidu.com/link?url=6ZGg7LYIN9hpdjlIRdWWkTOQU9CNDpyHSfFxvCu_EB_Pz0NEadCYJYDZdxDNYkVU2dSnOSYefxhi6v4lsvLmKK'))
# print(get_job_liepin('https://www.baidu.com/link?url=_nergAtvzYYIl54q1IW1ns-Q9qrC9djZ2drgiPoj1np7qlMlqjuFPdwFEBUrAvfSLJzGSO1_ZVgIgldMUZsu__'))
# print(get_job_nantong('http://www.ntrc.cn/html/job/260563'))
