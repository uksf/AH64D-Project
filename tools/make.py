import sys
import os
import os.path
import shutil
import platform
import glob
import subprocess
import hashlib
import configparser
import json
import traceback
import time
import timeit
import re
import fileinput
import winreg

def find_bi_tools(work_drive):
    """Find BI tools."""

    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    try:
        k = winreg.OpenKey(reg, r"Software\bohemia interactive\arma 3 tools")
        arma3tools_path = winreg.QueryValueEx(k, "path")[0]
        winreg.CloseKey(k)
    except:
        raise Exception("BadTools","Arma 3 Tools are not installed correctly or the P: drive needs to be created.")

    addonbuilder_path = os.path.join(arma3tools_path, "AddonBuilder", "AddonBuilder.exe")
    dssignfile_path = os.path.join(arma3tools_path, "DSSignFile", "DSSignFile.exe")
    dscreatekey_path = os.path.join(arma3tools_path, "DSSignFile", "DSCreateKey.exe")
    cfgconvert_path = os.path.join(arma3tools_path, "CfgConvert", "CfgConvert.exe")

    if os.path.isfile(addonbuilder_path) and os.path.isfile(dssignfile_path) and os.path.isfile(dscreatekey_path) and os.path.isfile(cfgconvert_path):
        return [addonbuilder_path, dssignfile_path, dscreatekey_path, cfgconvert_path]
    else:
        raise Exception("BadTools","Arma 3 Tools are not installed correctly or the P: drive needs to be created.")

def find_depbo_tools(regKey):
    """Use registry entries to find DePBO-based tools."""
    stop = False

    if regKey == "HKCU":
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        stop = True
    else:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    try:
        try:
            k = winreg.OpenKey(reg, r"Software\Wow6432Node\Mikero\pboProject")
        except FileNotFoundError:
            k = winreg.OpenKey(reg, r"Software\Mikero\pboProject")
        try:
            pboproject_path = winreg.QueryValueEx(k, "exe")[0]
            winreg.CloseKey(k)
            print("Found pboproject.")
        except:
            print("ERROR: Could not find pboProject.")

        try:
            k = winreg.OpenKey(reg, r"Software\Wow6432Node\Mikero\rapify")
        except FileNotFoundError:
            k = winreg.OpenKey(reg, r"Software\Mikero\rapify")
        try:
            rapify_path = winreg.QueryValueEx(k, "exe")[0]
            winreg.CloseKey(k)
            print("Found rapify.")
        except:
            print("Could not find rapify.")

        try:
            k = winreg.OpenKey(reg, r"Software\Wow6432Node\Mikero\MakePbo")
        except FileNotFoundError:
            k = winreg.OpenKey(reg, r"Software\Mikero\MakePbo")
        try:
            makepbo_path = winreg.QueryValueEx(k, "exe")[0]
            winreg.CloseKey(k)
            print("Found makepbo.")
        except:
            print("Could not find makepbo.")
    except:
        if stop == True:
            raise Exception("BadDePBO", "DePBO tools not installed correctly")
        return -1


    #Strip any quotations from the path due to a MikeRo tool bug which leaves a trailing space in some of its registry paths.
    return [pboproject_path.strip('"'),rapify_path.strip('"'),makepbo_path.strip('"')]

def main(module):
    print("Building: {}".format(os.path.join(work_drive, module)))

    try:
        cmd = [pboproject, "-P", os.path.join(work_drive, module), "+Engine=Arma3", "-S", "+Noisy", "+G", "+Clean", "+Mod="+output, "-Key"]
        ret = subprocess.call(cmd)
        print("pboProject return code == {}".format(str(ret)))

        if ret == 0:
            print("Signing with {}.".format(key))
            ret = subprocess.call([dssignfile, key, os.path.join(output, "addons", "{}.pbo".format(module))])
            print("dssignfile return code == {}".format(str(ret)))
    except:
        raise


if __name__ == "__main__":
    global dssignfile
    global pboproject
    global work_drive
    global output
    global key
    work_drive = "P:\\"
    output = "B:\\Steam\\steamapps\\common\\Arma 3\\@ApacheLongbowTEST"
    key = os.path.join(work_drive, "private_keys", "{}.biprivatekey".format("uksf_apache_test"))

    tools = find_bi_tools(work_drive)
    dssignfile = tools[1]
    
    depbo_tools = find_depbo_tools("HKLM")
    if depbo_tools == -1:
        depbo_tools = find_depbo_tools("HKCU")
    pboproject = depbo_tools[0]

    main("fza_ah64_controls")
    main("fza_ah64_us")
    sys.exit()
