import requests
import codecs
import re
import os
from lxml import etree
s=[]
t=[]
q=[]
n=1
name="alphaleela"
head={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}
def deal_url():#处理棋谱地址格式
	for i in range(n):
		for k in range(len(t[i])):
			q.append('http://weiqi.qq.com'+t[i][k])
def download():#根据棋谱地址提取棋谱
		for l in range(len(q)):	
			url=str(q[l])
			html=requests.get(url,headers=head)
			html.encoding="utf-8"
			ele=etree.HTML(html.text)
			st=ele.xpath("/html/body//div[@class='panel-body eidogo-player-auto modal-content']/text()")
			#print(st)
			st=str(st[0])
			t1=re.findall('PB\[(.+?)\]',st)#用正则表达式提取棋手名字信息
			t2=re.findall('PW\[(.+?)\]',st)#用正则表达式提取棋手名字信息
			f=codecs.open('E:\\sgfs\\'+name+'\\'+str(t1[0])+''+'VS'+''+str(t2[0])+''+str(l)+'.sgf',"w",'utf-8')
			f.write(st)
			f.write("\n")
			f.close()
def get_url():构造棋谱地址
	for i in range(0,len(s)):
		url=s[i]
		html=requests.get(url,headers=head)
		html.encoding="utf-8"
		ele=etree.HTML(html.text)
		st=ele.xpath("/html//td/a/@href")
		t.append(st)
def product_main_url():#构造主地址
	for i in range(1,n+1):
		s.append('http://weiqi.qq.com/qipu/search/title/'+name+'//p/'+str(i)+'.html')
def check():#检查总页数
	url0="http://weiqi.qq.com/qipu/search/title/"+name+"//p/1.html"
	html0=requests.get(url0,headers=head)
	html0.encoding="utf-8"
	ele0=etree.HTML(html0.text)
	str0=ele0.xpath("//ul//li/a/@href")
	t0=str(str0[-1])
	t4=re.findall('p/(.+?)\.html',t0)
	return t4[0]
def main():
	product_main_url()
	get_url()
	deal_url()
	download()
	print('棋谱地址收集完成，总共有'+str(len(q))+'张棋谱，请打开E盘的sgfs文件夹查看！')
	exit()
if "__name__=__main__":
	name=input("请输入需要下载的棋手名字:")
	if not os.path.exists('E://sgfs'):
		os.mkdir('E://sgfs/')
	if not os.path.exists('E://sgfs/'+name):
		os.mkdir('E://sgfs/'+name)
	n=int(input("总共有"+str(check())+"页\n请输入需要下载的页数:"))
	main()





		
