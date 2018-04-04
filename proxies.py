#encoding=utf8
#__author__ = "kingkk"

import requests, re, threading, sys, getopt, time

root_url = "http://www.xicidaili.com/wn/"
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"}
lock = threading.Lock()

def find_proxies(page_num=3):
	'''
	返回包含ip：port的字典生成器
	'''
	proxy_pool = set()
	for i in range(1,page_num+1):
		r = requests.get(root_url+str(i), headers=headers)
		proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s+<td>(\d+)</td>', r.text)	
		for proxy in proxies:
			ip, port = proxy #tuple拆包
			proxy_pool.add(proxy)
	iter_pool = (proxy for proxy in proxy_pool)
	return iter_pool

def checkout_thread(iter_pool,timeout=1,file_path=None):
	'''
	检查代理是否有用
	'''
	for proxy in iter_pool:
		ip, port = proxy
		proxies = {"http":"{ip}:{port}".format(ip=ip,port=port),
					"https":"{ip}:{port}".format(ip=ip,port=port)}
		try:
			r = requests.get("http://www.baidu.com",headers=headers,proxies=proxies,timeout=timeout)
			print(proxy)
		except:
			return

		if file_path is not None:
			with lock:
				with open(file_path,"a+") as f:
					f.write("{}\n".format(proxy))

def deal_thread(iter_pool,thread_num=100,timeout=1,file_path=None):
	'''
	开启、等待线程，默认线程数100
	'''
	thread_list = []
	if file_path is not None:
		this_time = time.ctime()
		with open(file_path,"a+") as f:
			f.write("***********starting {}, timeout is {}**************\n".format(this_time,timeout))
	for i in range(thread_num):
		t = threading.Thread(target=checkout_thread,args=(iter_pool,timeout,file_path))
		thread_list.append(t)
	for t in thread_list:
		t.start()
	for t in thread_list:
		t.join()
	if file_path is not None:
		with open(file_path,"a+") as f:
			f.write("\n\n")

def main():
	opts, args = getopt.getopt(sys.argv[1:],"t:f:")
	timeout = 1
	file_path = None
	for op, value in opts:
		if op == "-t":
			timeout = float(value)
		elif op == "-f":
			file_path = value
	iter_pool = find_proxies()
	deal_thread(iter_pool,timeout=timeout,file_path=file_path)
	
if __name__ == '__main__':
	main()