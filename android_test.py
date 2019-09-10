import os
import sys
import digutils
import time
from PIL import Image
from PIL import ImageFont


class ADBContext:
    def __init__(self, adb="adb"):
        self.adb_path = adb


class Application:
    def __init__(self, pkg, main_activity, adb_context=ADBContext("adb")):
        self.pkg = pkg
        self.main_activity = main_activity
        self.adb = adb_context

    def enter_app(self):
        ret, out = digutils.exec_cmd("{adb} shell am start -n {pkg}/{main_act}".format(adb=self.adb.adb_path, pkg=self.pkg, main_act=self.main_activity))
        return ret

    def check_app_alive(self):
        try:
            ret, out = digutils.exec_cmd(
                "adb shell pidof {}".format(self.pkg))
            pid_app = int(out[0])
        except:
            pid_app = 0

        return pid_app


class TestCase:
    def test_app_switch_home(self, test_app, max_wait_time=5, bs_timeout=5, wait_for_frame=False):
        wait_time = 1
        step = 0
        adb = test_app.adb
        while True:
            step = step + 1
            if wait_for_frame is True:
                time.sleep(3)
                TestUtil.wait_for_frame()
            else:
                print("Wait {} secs".format(wait_time))
                time.sleep(wait_time)
                wait_time = (wait_time + 1) % (max_wait_time + 1)
                if (wait_time == 0):
                    wait_time = 1
            TestUtil.log("Enter Launcher", output_logcat=True)
            TestUtil.goHome(adb)
            print("Check black screen", end="", flush=True)
            time.sleep(bs_timeout)
            if (TestUtil.check_black_screen(adb) is True):
                print("Launcher is black screen by wait {} secs, stop test".format(wait_time))
                exit(0)

            pid_test_app = test_app.check_app_alive()
            print(pid_test_app)
            if (pid_test_app != 0):
                print("Kill {}".format(pid_test_app))
                digutils.exec_cmd("adb shell input keyevent 187")
                time.sleep(0.5)
                digutils.exec_cmd("adb shell input keyevent 19")
                time.sleep(0.5)
                digutils.exec_cmd("adb shell input tap 1839 278")
                time.sleep(0.5)
                digutils.exec_cmd("adb shell input tap 1277 731")

            time.sleep(2)
            print("Enter {}".format(test_app.pkg))
            test_app.enter_app()

    def test_launcher_home_press(self, max_count=5, max_wait_time=5, step_add=True, step=0.5):
        log = TestUtil.log
        log("test_launcher_home_press")
        while True:
            count = 0
            wait_time = 0 + step
            while count < max_count:
                log("Enter Launcher {} steps".format(count))
                TestUtil.goHome()
                log("Wait {} secs".format(wait_time))
                time.sleep(wait_time)
                count = count + 1
                wait_time = (wait_time + step) % max_wait_time + step
            log("Check black screen", end="", flush=True)
            if TestUtil.check_black_screen() is True:
                log("Error")
                log("Test ended at {count} step, wait for {wait_time}".format(count=count, wait_time=wait_time))
                exit(0)
            log("OK")


class TestUtil:
    @staticmethod
    def check_black_screen(adb=ADBContext("adb"), no_print=False):
        cmd_cap_pic = "{adb} shell screencap -p /sdcard/current.png".format(adb=adb.adb_path)
        cmd_pull_pic = "{adb} pull /sdcard/current.png .".format(adb=adb.adb_path)

        if no_print is False:
            print(".", end="", flush=True)
        digutils.exec_cmd(cmd_cap_pic)

        if no_print is False:
            print(".", end="", flush=True)
        digutils.exec_cmd(cmd_pull_pic)

        if no_print is False:
            print(".", end="", flush=True)
        im = Image.open("current.png")

        if no_print is False:
            print(".", end="", flush=True)
        crl = im.getcolors()

        if no_print is False:
            print(".", end="", flush=True)
        if (crl is not None and len(crl) == 1):
            return True
        else:
            return False

    @staticmethod
    def wait_for_frame(frame=None):
        print("Waiting for frame", end="", flush=True)
        while True:
            if (TestUtil.check_black_screen(no_print=True) is True):
                print(".", end="", flush=True)
                time.sleep(1)
            else:
                print(" done")
                break

    @staticmethod
    def log(msg, output_logcat=False, end="\n", flush=False, adb=ADBContext("adb")):
        #print(adb.adb_path)
        if output_logcat is True:
            digutils.exec_cmd("{adb} shell logwrapper echo {msg}".format(adb=adb.adb_path, msg=msg))
        print(msg, end=end, flush=flush)

    @staticmethod
    def goHome(adb=ADBContext("adb")):
        cmd = "{adb} shell input keyevent 26".format(adb=adb.adb_path)
        digutils.exec_cmd(cmd)

    @staticmethod
    def get_current_pkg_and_act(adb):
        print("--")


def test_app_switch(app1_pkg, app2_pkg, timeout=5, main_activity="com.unity3d.player.UnityPlayerActivity"):
    wait_time = 1
    step = 0
    while True:
        step = step + 1
        print("Step {}: wait {} secs".format(step, wait_time))
        logcat("Step {}: wait {} secs".format(step, wait_time))
        time.sleep(wait_time)
        wait_time = (wait_time + 1) % 5
        if (wait_time == 0):
            wait_time = 1
        # start app1
        digutils.exec_cmd("adb shell am start -n {pkg}/{main_activity}".format(pkg=app1_pkg, main_activity=main_activity))
        # check if app2 is alive
        try:
            ret, out = digutils.exec_cmd(
                "adb shell pidof {}".format(app2_pkg))
            pid_app2 = int(out[0])
        except:
            pid_app2 = 0
        # kill app2
        if (pid_app2 != 0):
            print("Kill {}".format(pid_app2))
            digutils.exec_cmd("adb shell input keyevent 187")   # menu
            time.sleep(0.5)
            digutils.exec_cmd("adb shell input keyevent 19")    # down
            time.sleep(0.5)
            digutils.exec_cmd("adb shell input tap 1839 278")   # close app2
            time.sleep(0.5)
            digutils.exec_cmd("adb shell input tap 1277 731")   # back to app1

        print("back to {}".format(app1_pkg))
        time.sleep(timeout)
        print("check black screen", end="", flush=True)
        is_bs = check_black_screen()
        if (is_bs is True):
            print("{} is black screen by wait {} secs, stop test".format(app1_pkg, wait_time))
            exit(0)
        digutils.exec_cmd("adb shell am start -n {pkg}/{main_activity}".format(pkg=app2_pkg, main_activity=main_activity))


def test_PIL(pic):
    im = Image.open(pic)
    r, g, b = im.split()
    im_merge = Image.merge("RGB", [r, g, b])
    ifont = ImageFont.truetype('Arial.ttf', 36)


if __name__ == "__main__":
    adb = ADBContext("adb")
    def_main_act = "com.unity3d.player.UnityPlayerActivity"
    TestUtil.goHome(adb)
    boxworld = Application("com.polyengine.Boxworld_0909", def_main_act, adb)
    tc = TestCase()
    tc.test_launcher_home_press(max_count=10, max_wait_time=2, step=0.2)
    # tc.test_app_switch_home(boxworld)
