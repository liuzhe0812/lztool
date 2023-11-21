# -*- coding: utf-8 -*-
import threading,configparser,winreg,os,codecs


def get_desktop_path():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                          r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, "Desktop")[0]

def get_files(path,all_files):
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            get_files(cur_path, all_files)
        else:
            all_files.append(cur_path)
    return all_files

def ipIncrease(ip, i):
    ip2num = lambda x:sum([256**j*int(i) for j,i in enumerate(x.split('.')[::-1])])
    num = ip2num(ip)
    num2ip = lambda x: '.'.join([str(x//(256**i)%256) for i in range(3,-1,-1)])
    return num2ip(num+ i)


class job(threading.Thread):

    def __init__(self):
        super(job, self).__init__()
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def start(self, method):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            method()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False


def new_thread(method, args=(), join=False):
    thread = threading.Thread(target=method, args=args)
    thread.setDaemon(True)
    thread.start()
    if join:
        thread.join()
    return thread

def get_config(section,key, config_file='config.ini',config=None):
    if not config:
        config = configparser.ConfigParser()
    config.read(config_file)
    val = config.get(section,key)
    return val

def set_config(section,key,val,config_file='config.ini',config=None):
    if not config:
        config = configparser.ConfigParser()
    config.read(config_file)
    config.set(section,key,val)
    config.write(open(config_file, "r+"))

def get_download_path():
    return get_config('ssh','download_path')

def int_to_mask(mask_int):
    bin_arr = ['0' for i in range(32)]
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)

def mask_to_int(mask):
    count_bit = lambda bin_str: len([i for i in bin_str if i == '1'])
    mask_splited = mask.split('.')
    mask_count = [count_bit(bin(int(i))) for i in mask_splited]
    return sum(mask_count)

def checkmask(mask):
    if mask == '0.0.0.0':
        return False
    mask = mask.split(".")
    masknum = [int(num) for num in mask]
    maskbin = ''

    for num in masknum:
        item = bin(num).split('0b')[1]

        if len(item) != 8:
            zeronum = '0' * (8 - len(item))
            item = zeronum + item
        maskbin += item

    if '01' in maskbin:
        return False
    else:
        return True

def getLabelFromEVT(evt):
    menu = evt.GetEventObject()
    item = menu.FindItemById(evt.GetId())
    label = item.GetItemLabel()
    return label

def bytes2human(n,start=None):
    symbols = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    if start:
        index = symbols.index(start)
        symbols = symbols[index+1:]
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value,s)
    if start:
        return '%s%s'%(n,start)
    else:
        return '%sB' % n

def is_utf8(s):
    try:
        codecs.decode(s, 'utf-8')
        return True
    except UnicodeDecodeError:
        return False