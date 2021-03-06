#!/usr/bin/env python
# encoding: utf-8
'''
@author: liuhu
@license: (C) Copyright 2013-2018, Node Supply Chain Manager Corporation Limited.
@contact: max_liuhu@163.com
@software: pycharm
@file: catch_data.py
@time: 2018/11/7 17:26
@desc:
'''
from Tkinter import *
import subprocess
import os
import time
from datetime import datetime
import ConfigParser

temp_mtr_log = '/var/log/mtr/mtr_temp.log'
mtr_conf = '/etc/mtr/mtr.conf'
real_time_mtr_info = {'proto': None, 'package_loss': None, 'net_delay': None}
abnormal_mtr_log_loc = '/var/log/mtr/mtr_abnorm.log'
config_file = '/thinclient_config/vditerminal_config.yaml'
ip_conflict_info = {'ip_conflict': False}

is_abmormal = False


def get_target(target):
    """
    :param target: str
    :return:str
    """
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            while True:
                content = f.readline()
                if content:
                    if target in content:
                        try:
                            target_value = content.split(':', 1)[1].strip()
                            return target_value
                        except BaseException:
                            pass
                    else:
                        continue
                else:
                    break
    if target == 'userportal':
        target_value = None
    else:
        target_value = ''
    return target_value


def check_ip_wether_conflict(ifacename):
    """
    :param ifacename: str
    :return: True or False
    """
    if ifacename == '':
        return False
    commands = "ifconfig %s | grep 'inet addr' | head -1 | awk  -F'[: ]+' '{print $4}'" % ifacename
    out = subprocess.Popen(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True)
    ip = out.stdout.readline()
    if ip:
        exit_code = os.system(
            "arping -c 1 -f -D -w 1 -I %s %s" %
            (ifacename, ip))
        if exit_code != 0:
            return True
    return False


def get_mtr_conf_info(mtr_conf):
    max_abnorm_info = {'max_loss': 1, 'max_delay': 5}
    if os.path.exists(mtr_conf):
        read_config = ConfigParser.SafeConfigParser()
        read_config.read(mtr_conf)
        try:
            max_abnorm_info['max_loss'] = read_config.get('mtr', 'max_loss')
            max_abnorm_info['max_delay'] = read_config.get('mtr', 'max_delay')
        except Exception as e:
            print str(e)
    return max_abnorm_info


def mtr_loss_delay_info(ip):
    if not os.path.exists(temp_mtr_log):
        os.system(
            'sudo mkdir /var/log/mtr && sudo touch /var/log/mtr/mtr_temp.log && sudo chmod 777 {0}'.format(
                temp_mtr_log))
    else:
        os.system('sudo echo > {0}'.format(temp_mtr_log))

    command = r' mtr -4 -p -c 1 {0}'.format(ip)
    px = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True)
    pid = px.pid
    print pid

    while True:
        content = px.stdout.readline().strip()
        if content:
            if ip in content:
                break
            else:
                continue
        else:
            break
    if content:
        try:
            split_content = content.split()
            package_loss = split_content[2]
            net_delay = split_content[7]
            real_time_mtr_info['package_loss'] = package_loss
            real_time_mtr_info['net_delay'] = net_delay
            print {'after delay info  ': real_time_mtr_info}
            return real_time_mtr_info
        except IndexError:
            pass
    real_time_mtr_info['package_loss'] = None
    real_time_mtr_info['net_delay'] = None
    return real_time_mtr_info


def protocol_info():
    pro = 'protocol='
    command = r'ps aux | grep protocol='
    popen = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True)
    while True:
        content = popen.stdout.readline().strip()
        if content:
            if pro in content:
                try:
                    proto = content.split('?', 2)[2].split('&', 1)[0].split('=', 1)[1]
                except IndexError:
                    continue
                if proto:
                    real_time_mtr_info['proto'] = proto
                    return real_time_mtr_info
                else:
                    continue
            else:
                continue
        else:
            break
    real_time_mtr_info['proto'] = None
    return real_time_mtr_info


def save_abnormal_info(proto, package_loss, net_delay, ip_conflict):
    if not os.path.exists(abnormal_mtr_log_loc):
        os.system('sudo touch {0} && sudo chmod 777 {0}'.format(
            abnormal_mtr_log_loc))
    now = datetime.now()
    time_part = now.strftime('%y-%m-%d %H:%M:%S')
    global is_abmormal
    if proto == 'console' or package_loss >= max_loss or net_delay >= max_delay or ip_conflict:
        if not is_abmormal:
            is_abmormal = True
        os.system(
            r'echo {0}, protocol:{1}, package_loss:{2}, net_delay:{3},ip_conflict:{4} >> {5}'.format(
                time_part,
                proto,
                package_loss,
                net_delay,
                ip_conflict,
                abnormal_mtr_log_loc))
        center_window(root)
        return
    else:
        if is_abmormal:
            is_abmormal = False
        disappear(1)
        return


disappear_tag = 0


def disappear(event):
    global is_abmormal
    if not is_abmormal:
        center_window(root, 15, 1)
        root.attributes('-alpha', 0.5)
        root.update()


def show(event):
    center_window(root)
    root.attributes('-alpha', 0.5)
    root.update()


def center_window(root, width=500, height=25):
    screenwidth = root.winfo_screenwidth()
    window_wide_center = (screenwidth - width) / 2
    size = '%dx%d+%d+%d' % (width, height, window_wide_center, 0)
    root.geometry(size)


def set_window(root):
    root.attributes('-alpha', 0.5, '-fullscreen', False, '-topmost', True)
    root.overrideredirect(True)
    root.grid()
    center_window(root)
    root.bind(sequence='<Leave>', func=disappear)
    root.bind(sequence='<Enter>', func=show)


root = Tk()
set_window(root)
var1 = StringVar()
var2 = StringVar()
var3 = StringVar()
var4 = StringVar()


def set_label(var_test, color_num=1, width=10, row=1, column=0, padx=10, pady=2):
    colors = {1: 'blue', 2: 'Crimson'}
    Label(textvariable=var_test, fg=colors[color_num], width=width).grid(row=row, column=column, padx=padx, pady=pady)


set_label(var1, color_num=1, width=10, row=1, column=0, padx=10, pady=2)
set_label(var2, color_num=1, width=10, row=1, column=1, padx=10, pady=2)
set_label(var3, color_num=1, width=10, row=1, column=2, padx=10, pady=2)
set_label(var4, color_num=1, width=10, row=1, column=3, padx=10, pady=2)


color_display_status = {
    'proto_status': False,
    'loss_status': False,
    'delay_status': False,
    'conflict_status': False}


def change_display_info(proto, package_loss, net_delay, ip_conflict):
    proto_status = color_display_status['proto_status']
    if proto != 'console':
        if proto_status:
            color_display_status['proto_status'] = False
            set_label(var1)
        else:
            pass
    else:
        if not proto_status:
            color_display_status['proto_status'] = True
            set_label(var1, color_num=2)
        else:
            pass

    loss_status = color_display_status['loss_status']
    if package_loss < max_loss:
        if loss_status:
            color_display_status['loss_status'] = False
            set_label(var2, column=1)
        else:
            pass
    else:
        if not loss_status:
            color_display_status['loss_status'] = True
            set_label(var2, color_num=2, column=1)
        else:
            pass

    delay_status = color_display_status['delay_status']
    if net_delay < max_delay:
        print 'no max_delay'
        if delay_status:
            color_display_status['delay_status'] = False
            set_label(var3, column=2)
        else:
            pass
    else:
        if not delay_status:
            color_display_status['delay_status'] = True
            set_label(var3, color_num=2, column=2)
        else:
            pass

    conflict_status = color_display_status['conflict_status']
    if ip_conflict:
        if not conflict_status:
            color_display_status['conflict_status'] = True
            set_label(var4, column=3)
        else:
            pass
    else:
        if conflict_status:
            color_display_status['conflict_status'] = False
            set_label(var4, color_num=2, column=3)
        else:
            pass


def main_func():
    while True:
        mtr_loss_delay_info(ip)
        protocol_info()
        result_proto = real_time_mtr_info['proto']
        result_package_loss = real_time_mtr_info['package_loss']
        result_net_delay = real_time_mtr_info['net_delay']
        result_conflict = check_ip_wether_conflict(ifacename)
        save_abnormal_info(
            result_proto,
            result_package_loss,
            result_net_delay,
            result_conflict)
        change_display_info(
            result_proto,
            result_package_loss,
            result_net_delay,
            result_conflict)

        if result_proto == 'dsp':
            var1.set('连接协议：正常')
        elif result_proto == "console":
            var1.set('连接协议：维护')
        else:
            var1.set('连接协议：----')

        if result_package_loss:
            var2.set('丢包率：{0}%'.format(result_package_loss))
        else:
            var2.set('丢包率：----')

        if result_net_delay:
            var3.set('网络延迟：{0}ms'.format(result_net_delay))
        else:
            var3.set('网络延迟：----')

        if result_conflict:
            var4.set('IP冲突:是')
        else:
            var4.set('IP冲突:否')

        del result_package_loss
        del result_proto
        del result_net_delay

        time.sleep(3)


if __name__ == '__main__':
    import threading

    ip = get_target('userportal')
    max_mtr_info = get_mtr_conf_info(mtr_conf)
    max_loss = max_mtr_info['max_loss']
    max_delay = max_mtr_info['max_delay']
    ifacename = get_target('ifacename')
    t = threading.Thread(target=main_func, args=())
    t.start()
    mainloop()
