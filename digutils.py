import subprocess


def exec_cmd(cmd, clean_result=False, quiet_err=False):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE if quiet_err is True else None)
    out_tuple = p.communicate()
    ret = p.returncode
    try:
        out = (out_tuple[0].decode('utf-8'), out_tuple[1])
        if (clean_result is True):
            out = out[0].replace("\r", "").replace("\n", "")
    except:
        out = None
    return ret, out


def sleep(sec):
    _ = time.perf_counter() + sec
    while time.perf_counter() < _:
        pass
