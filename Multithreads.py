#!/usr/bin/env python
# coding: utf-8

#获取全网棋谱
import requests
import codecs
import re
import os
from lxml import etree
import json
import jsonpath
from tkinter import *
from bs4 import BeautifulSoup
import random
import sys
import time
import threading
from tkinter.filedialog import askdirectory
import tkinter.messagebox

head={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}


url5= 'http://www.xicidaili.com/nn/'#代理IP获取网址
def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies
ip_list = get_ip_list(url5, headers=head)#获取IP


class Request:
    id=0
    def __init__(self,name):
        self.name=name
        Request.id+=1
        self.show_information()
        self.head=head={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}
        self.urls=[]
        self.usedurl=[]
        self.response=[]
        self.data=[]
    def show_information(self):
        print("我是 %s 爬虫\n编号%s"%(self.name,self.id))
    def requests(self,mathod,url,data=None,params=None,encode='utf-8'):
        for i in url:
            if i not in self.usedurl:
                if mathod=='get':
                    html=requests.get(i,headers=self.head,params=params)
                    html.encoding=encode
                    self.response.append(html)
                else:
                    html=requests.post(i,headers=self.head,data=data)
                    html.encoding=encode
                    self.response.append(html)
                self.usedurl.append(i)
    def multithreads_requests(self,mathod,urls,k,data=None,params=None,encode='utf-8'):#多线程发送请求
        threads = []#存放线程的数组，相当于线程池
        p=0
        k=k#间隔
        while p+k<=len(urls):
            thread =threading.Thread(target=self.requests,args=(mathod,urls[p:p+k],data,params,encode))#指定线程i的执行函数为myThread
            p+=k
            threads.append(thread)#先讲这个线程放到线程threads
        if p!=len(urls):
            thread =threading.Thread(target=self.requests,args=(mathod,urls[p:len(urls)],data,params,encode))
            threads.append(thread)
        for t in threads:#让线程池中的所有数组开始
            t.start()
        for t in threads:#让线程池中的所有数组开始 
            t.join()

class Spider:
    def __init__(self,url,name):
        self.start_url=url#起始位置
        self.main_url=[]#分页面
        self.sgfs_url=[]#文件地址
        self.path='C://'#存储路径
        self.name=name#网站名
        self.pages=1#下载页数
        self.data=[]
        self.urls=[]
    def get_total_page(self):
        pass
    def produce_url(self,m,n,model):#生产urls
        for i in range(m,n):#页数
            self.main_url.append(model[0]+str(i)+model[-1])
        print(len(self.main_url))
    def match(self,url,model,encoding='utf-8'):#model匹配
        a=Request(self.name)
        a.multithreads_requests('get',url,10)
        for i in a.response:
            ele=etree.HTML(i.text)
            self.data.append(ele.xpath(model))
    def ex(self,datas):
        for i in datas:
            data={'pid':re.findall('player/.*/(.+?)/',i)[0],'csrfmiddlewaretoken': 'qLoEijOiXKsLDx0Kp0xStpREln2KCN6xBhOUc5FsmWFChpLAWB1c4412j7mbvmOT'}
            head.update({'Referer':self.start_url+i})
            head.update({'Cookie':'csrftoken=lc19HSZjUwDGkah4dnspC2OMTPd8HRpgwIrpBEQtjIQxY22UKYWJdHYaRzxzAq7C'})
            html=requests.post('https://www.101weiqi.com/chessbook/download_sgf/',headers=head,data=data)
            html.encoding='utf-8'
            ll=re.findall('purl": "(/f.*sgf)"}',html.text)
            if len(ll)>=1:
                self.sgfs_url.append(self.start_url+ll[0])
    def add_players(self,m,n):
        self.match([self.start_url+'/chessbook/playerlist/'],'/html//div[@class="col-md-2 left"]/a/@href','utf-8')
        for i in self.data[0][m:n]:
            self.urls.append(self.start_url+i)
        self.data.clear()
        
        for i in self.urls:
            self.match([i],'/html//ul[@class="pagination pull-right"]/li[last()-1]/a/@href','utf-8')
        for i in range(len(self.data)):
            self.produce_url(0,int(str(self.data[i][0]).split('=')[1]),[self.urls[i]+'?page=',''])
    def excuate_url(self,text,re_):
        for i in text:
            for j in i:
                self.sgfs_url.append(re.findall(re_,j)[0])
    def excuate_url_2(self,text,re_):
        for i in text:
            if len(i)>1:
                for j in i:
                    self.sgfs_url.append(self.start_url+re.findall(re_,j)[0]+'.sgf')
    def excuate_url_3(self,text,re_):
        for i in text:
            if len(i)>1:
                for j in i:
                    if len(j)>1:
                        self.sgfs_url.append(re_+j.split('=')[1])
    def excuate_url_4(self,text,re_):
        for i in text:
            if len(i)>1:
                for j in i:
                    self.sgfs_url.append('http://www.qipai.org.cn/web/qpk/replay-info/id/'+re.findall(re_,j)[0])
    def excuate_url_5(self):
        a=Request('弈招围棋')
        a.multithreads_requests('get',self.main_url,10)
        for i in a.response:
            j=json.loads(i.text)
            for k in j['data']:
                self.sgfs_url.append('http://yi.weiqitv.com/pub/kifureview/'+k['id'])
    def excuate_url_6(self,text):
        for i in text:
            for j in i:
                self.sgfs_url.append(j)
    def excuate_url_7(self,k):
        a=Request(self.name)
        a.multithreads_requests('get',self.main_url,10)
        dat=[]
        for i in a.response:
            txt=etree.HTML(i.text)
            for j in txt.xpath('/html//tr/td[1]/a/@href'):
                dat.append(j)
        
        threads = []#存放线程的数组，相当于线程池
        p=0
        k=k#间隔
        while p+k<=len(dat):
            thread =threading.Thread(target=self.ex,args=(dat[p:p+k],))#指定线程i的执行函数为myThread
            p+=k
            threads.append(thread)#先讲这个线程放到线程threads
        if p!=len(dat):
            thread =threading.Thread(target=self.ex,args=(dat[p:len(dat)],))
            threads.append(thread)
        for t in threads:#让线程池中的所有数组开始
            t.start()
        for t in threads:#让线程池中的所有数组开始 
            t.join()
    def download(self,encode='utf-8'):
        global path_
        self.path=path_+'/'
        if not os.path.exists(self.path+'/sgfs'):
            os.mkdir(self.path+'/sgfs/')
        if not os.path.exists(self.path+'/sgfs/'+self.name):
            os.mkdir(self.path+'/sgfs/'+self.name)
        a=Request(self.name)
        a.multithreads_requests('get',self.sgfs_url,10,encode=encode)
        for i in a.response:
            st=str(i.text)
            t1=re.findall('PB\[(.+?)\]',st)#用正则表达式提取棋手名字信息
            t2=re.findall('PW\[(.+?)\]',st)#用正则表达式提取棋手名字信息
            t3=re.findall('DT\[(.+?)\]',st)#用正则表达式提取比赛时间信息
            t4=re.findall('TE\[(.+?)\]',st)#用正则表达式提取比赛场次信息
            t5=re.findall('RE\[(.+?)\]',st)#用正则表达式提取比赛结果信息
            if t1==[]:
                t1.append('unknown')
            if t2==[]:
                t2.append('unknown')
            if t3==[]:
                t3=re.findall('RD\[(.+?)\]',st)
            if t3==[]:
                t3.append('unknown')
            if t4==[]:
                t4=re.findall('EV\[(.+?)\]',st)
            if t4==[]:
                t4=re.findall('C\[(.+?)\]',st)
            if t4==[]:
                t4=re.findall('GN\[(.+?)\]',st)
            if t4==[]:
                t4.append('未知比赛')
            if t5==[]:
                t5.append('结果未知')
            rr=str(t3[0].replace('/','-'))+'+'+str(t4[0].replace('/',''))+'+'+str(t1[0].replace('/',''))+''+'VS'+''+str(t2[0].replace('/',''))+'+'+str(t5[0].replace('/','%'))+''+'.sgf'
            print(rr)
            try:
                f=codecs.open(self.path+'/sgfs/'+self.name+'/'+rr,"w",'utf-8')
                f.write(st)
                f.close()
            except:
                print('写入错误！')

def Lol(m,n):
    #137位棋手
    Lol=Spider('https://www.101weiqi.com','101围棋')
    Lol.add_players(m,n)#137位棋手
    Lol.excuate_url_7(10)#线程间隔10
    Lol.download('utf-8')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def KGS(m,n):
    #2000页，每页20张
    KGS=Spider('http://gokifu.com','KGS')
    KGS.produce_url(m,n,['http://gokifu.com/?p=',''])
    KGS.match(KGS.main_url,"/html//div[@class='player_block cblock_3']/div[@class='game_type'][last()]/a[2]/@href",'utf-8')
    KGS.excuate_url_6(KGS.data)
    KGS.download('utf-8')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def YiZhao(m,n):
    #共有88,128页，每页10张
    YiZhao=Spider('http://www.weiqitv.com/kifu','弈招围棋')
    YiZhao.produce_url(m,n,['http://yi.weiqitv.com/pub/kifu?start=','&len=10&kifuTp=%E5%85%A8%E9%83%A8&gameSort=false&'])
    YiZhao.excuate_url_5()
    YiZhao.download('utf-8')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def ChinaGo(m,n):
    #823页，每页20张
    ChinaGo=Spider('http://www.qipai.org.cn','中国围棋')
    ChinaGo.produce_url(m,n,['http://www.qipai.org.cn/web/qpk/list/game/weiqi/page/','/num/20?PHPSESSID=6fmuao0dgc8a5gtsqo1vv645a7'])
    ChinaGo.match(ChinaGo.main_url,"/html//table[@class='search-result-table']//a/@href",'utf-8')
    ChinaGo.excuate_url_4(ChinaGo.data,'code/(.+?)\?')
    ChinaGo.download('utf-8')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def HongTong(m,n):
    #1355页，每页100张
    HongTong=Spider('http://hotongo.com/','弘通围棋')
    HongTong.produce_url(m,n,['http://hotongo.com/matchlatest_2011.jsp?pn=',''])
    HongTong.match(HongTong.main_url,'/html//tr/td[3]/p/a/@href','utf-8')#model匹配
    HongTong.excuate_url_3(HongTong.data,'http://hotongo.com/chessmanualsgf.jsp?id=')
    HongTong.download('gbk')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def Sina(m,n):
    #总共960页，每页50张
    Sina=Spider('http://duiyi.sina.com.cn/gibo/new_gibo.asp','新浪围棋')
    Sina.produce_url(m,n,['http://duiyi.sina.com.cn/gibo/new_gibo.asp?cur_page=',''])#下载3页
    Sina.match(Sina.main_url,"/html//tr[@class='body_text1']/td[2]/a/@href",encoding='utf-8')
    Sina.excuate_url(Sina.data,"load\('(.+?)'\);")
    Sina.download('gbk')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录下的sgfs文件夹下')

def TOM(m,n):
    #总共40页，每页150张
    TOM=Spider('http://weiqi.tom.com','TOM围棋')
    TOM.produce_url(m,n,['http://weiqi.tom.com/php/listqipu_0','.html'])
    TOM.match(TOM.main_url,"/html//li[@class='c']/a/@href",'utf-8')#model匹配
    TOM.excuate_url_2(TOM.data,"../..(.+?).sgf")
    TOM.download('gbk')
    tkinter.messagebox.showinfo('下载信息：','下载完成！\n棋谱文件在所选目录的sgfs文件夹下')


def selectPath():
    global path_
    path_=askdirectory()
    path.set(path_)

def start():
    tkinter.messagebox.showinfo('下载信息：','保存路径:'+path_+'\n围棋站点:'+str(v.get())+'\n下载数量（页）:'+str(int(e1.get())+1-int(e2.get())))
    if v.get()==1 and int(e1.get())<823:
        ChinaGo(int(e2.get()),int(e1.get()))
    elif  v.get()==2 and int(e1.get())<88128:
        YiZhao(int(e2.get()),int(e1.get()))
    elif  v.get()==3 and int(e1.get())<960:
        Sina(int(e2.get()),int(e1.get()))
    elif  v.get()==4 and int(e1.get())<137:
        Lol(int(e2.get()),int(e1.get()))
    elif  v.get()==5 and int(e1.get())<40:
        TOM(int(e2.get()),int(e1.get()))
    elif  v.get()==6 and int(e1.get())<1355:
        HongTong(int(e2.get()),int(e1.get()))
    elif  v.get()==7 and int(e1.get())<1999:
        KGS(int(e2.get()),int(e1.get()))
def show():
    tkinter.messagebox.showinfo('统计','新浪围棋 总共959页 每页50张 \nTOM围棋 总共39页，每页150张\n 弘通围棋 总共1354页，每页100张\n 中国围棋 总共822页，每页20张 \n弈招围棋 总共88,127页，每页10张 \nKGS 总共2000页，每页20张\n101围棋网 收录136位棋手')


#界面
root=Tk()
la=[('中国围棋','1'),('弈招围棋','2'),('新浪围棋','3'),('101围棋','4'),('TOM围棋','5'),('弘通围棋','6'),('KGS围棋','7')]
v=IntVar()
v.set(0)
i=1
b_=[]
path_='C://'
for l,n in la:
    b=Radiobutton(root,text=l,variable=v,value=n,indicatoron=False)
    b.grid(row=i,column=2)
    b_.append(b)
    i+=1
Button(root, text='查询总页数', command=show).grid(row=4, column=0, sticky=W, pady=4)
path= StringVar()

e3=Entry(root, textvariable = path).grid(row =3, column =1)
Button(root, text = "路径选择", command = selectPath).grid(row =3, column=0)
l1=Label(root,text='起始页')
l1.grid(row=1,column=0)
l2=Label(root,text='终止页')
l2.grid(row=2,column=0)
l1=Label(root,text='选择下载站点')
l1.grid(row=0,column=2)
e2=Entry(root)
e2.grid(row=1,column=1)
e1=Entry(root)
e1.grid(row=2,column=1)
b=Button(root,text='开始下载',command=start)
b.grid(row=4,column=1)
root.mainloop()
