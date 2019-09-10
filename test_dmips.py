import sys  
import os
import subprocess
import time

def __exec_cmd__(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    cmm_out = p.communicate()
    out = (cmm_out[0].decode('utf-8'), cmm_out[1])
    ret = p.returncode
    return ret, out

def __set_speed__(freq, core):
    cmd = 'adb shell echo "{freq} > /sys/devices/system/cpu/cpu{core}/cpufreq/scaling_setspeed"'.format(freq=freq, core=core)
    __exec_cmd__(cmd)


def __dmips_init__(core):
    if (core >= 0 and core < 4):
        cluser = 0
    elif (core >= 4 and core < 8):
        cluser = 4
    else:
        print('Unsupport cpu ' + core)
        exit(-1)

    cmd = 'adb shell "echo userspace >  /sys/devices/system/cpu/cpufreq/policy{cluser}/scaling_governor'.format(cluser=cluser)
    return __exec_cmd__(cmd)
    

def __dmips_uninit__(core):
    if (core >= 0 and core < 4):
        cluser = 0
    elif (core >= 4 and core < 8):
        cluser = 4
    else:
        print('Unsupport cpu ' + core)
        exit(-1)
    cmd = 'adb shell "echo interactive >  /sys/devices/system/cpu/cpufreq/policy{cluser}/scaling_governor'.format(cluser=cluser)
    return __exec_cmd__(cmd)


def do_dmips(freq, core):
    __set_speed__(freq, core)
    if (core >= 4 and core <= 7):
        cluser = 4
    elif (core >=0 and core <= 3):
        cluser = 0
    else:
        print('Unsupport cpu ' + core)
        return -1;
    
    if (cluser == 4):
        cpu_set = 'f0'
    else:
        cpu_set = 'f'

    if(freq > 1420800):
        nums_of_dry = 15000000
    else:
        nums_of_dry = 10000000

    cmd = 'adb shell taskset {cpuset} gcc_dry2 {nums_of_dry}'.format(cpuset=cpu_set, nums_of_dry=nums_of_dry)
    #cmd = 'adb shell gcc_dry2 {nums_of_dry}'.format(cpuset=cpu_set, nums_of_dry=nums_of_dry)
    ret,out = __exec_cmd__(cmd)
    if (ret == 0):
        #print(out)
        arr_out = out[0].replace('\r','').split('\n')[:-2]
        mspd = arr_out[0].split(' ')[-2]
        dmips = arr_out[1].split(' ')[-2]
        return 0,mspd, dmips
    else:
        print(ret)
        return ret,0,0

def __get_avaliable_freqstr__(core):
    cmd = 'adb shell cat /sys/devices/system/cpu/cpu{core}/cpufreq/scaling_available_frequencies'.format(core=core)
    ret, out = __exec_cmd__(cmd)
    if (ret >= 0):
        return ret,out[0].replace('\r', '').split(' ')[:-1]
    else:
        return ret,''

def __get_max_freq__(core):
    cmd = 'adb shell cat /sys/devices/system/cpu/cpu{core}/cpufreq/cpuinfo_max_freq'.format(core=core)
    ret,out = __exec_cmd__(cmd)
    if (ret >= 0):
        return ret,out[0].replace('\r', '')
    else:
        return ret,''

def __get_all_freq_dmips__(core):
    #avaliable_freqstr="300000 345600 422400 499200 576000 652800 729600 806400 902400 979200 1056000 1132800 1190400 1267200 1344000 1420800 1497600 1574400 1651200 1728000 1804800 1881600 1958400 2035200 2112000 2208000 2304000"
    ret, avaliable_freqs = __get_avaliable_freqstr__(core)
    if (ret >= 0):
        print(avaliable_freqs)

        ret, out = __dmips_init__(core)
        if (ret < 0):
            print('error for dmips init')
            exit(-1)

        for freq in avaliable_freqs:
            ret,mspd,dmips=do_dmips(freq, core)
            if (ret == 0):
                print("{freq},{dmips},{mspd}".format(freq=freq, dmips=dmips, mspd=mspd))
            else:
                print('dmips for {freq} failed.'.format(freq=freq))
    else:
        print('error get {core} avaliable_freqs'.format(core=core))
                    
    __dmips_uninit__(core)
    

def __dmips_stat__(core):
    ret, out = __dmips_init__(core)
    if (ret >= 0):
        cmd_get_current = 'adb shell cat /sys/class/power_supply/battery/current_now'
        cmd_get_voltage = 'adb shell cat /sys/class/power_supply/battery/voltage_now'
        cmd_get_cur_freq = 'adb shell cat /sys/devices/system/cpu/cpu{core}/cpufreq/cpuinfo_cur_freq'.format(core=core)
        filename='e:\cpu_stat.log'
        f=open(filename, "w+")
        while True:
            ret,out = __exec_cmd__(cmd_get_current)
            cur = out[0].replace("\r\n", "")
            ret,out = __exec_cmd__(cmd_get_voltage)
            vol = out[0].replace("\r\n", "")
            ret,out = __exec_cmd__(cmd_get_cur_freq)
            cur_freq = out[0].replace("\r\n", "")
            ret,mspd,dmips = do_dmips(2304000, 4)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(round(time.time()*1000))/1000))
            strline="{timestamp},{current},{voltage},{dmips},{cur_freq}".format(timestamp=timestamp,current=cur, voltage=vol, dmips=dmips, cur_freq=cur_freq)
            f.write(strline+'\n')
            f.flush()
            print(strline)
    else:
        print(ret)
    f.close()


def __get_current__(sample_rate=5000):
    while (True):
        print(time.perf_counter())
        __usleep__(0.000001)

def __usleep__(delay): 
    _ = time.perf_counter() + delay
    while time.perf_counter() < _:
        pass

if __name__ == "__main__":
    __dmips_stat__(4)
    #__get_current__(sample_rate=5000)

