#!/usr/bin/env python3

import stat
from os import getcwd, popen, getpid, remove, getuid, chmod
from sys import exit
from json import load, dump
from time import sleep
from ast import literal_eval


def info(contents: str):
    print(f"INFO: {contents}")
    with open("servermand.log", "a+") as f:
        f.write(f"INFO: {contents}\n")

def warn(contents: str):
    print(f"WARN: {contents}")
    with open("servermand.log", "a+") as f:
        f.write(f"WARN: {contents}\n")

def error(contents: str):
    print(f"ERROR: {contents}")
    with open("servermand.log", "a+") as f:
        f.write(f"ERROR: {contents}\n")

def run(command: str):
    print(f"RUN: {command}")
    with open("servermand.log", "a+") as f:
        f.write(f"RUN: {command}\n")
    return popen(command).read()

def help(command):
    match command[0]:
        case "internet":
            internet("")
        case "" | _:
            info("servermand commands")
            info("help: show this message")
            info("stop: stop servermand")
            info("internet: modify settings related to internet connection")

def internet(command):
    match command[0]:
        case "addresses":
            info("getting internet addresses...")
            info("loading list of interfaces...")
            ifs = run("ls /sys/class/net/").split()
            info("getting each interface's ip address")
            ips = {}
            for i, iff in enumerate(ifs):
                ipp = run(f"ip -f inet addr show {iff} | sed -En -e 's/.*inet ([0-9.]+).*/\\1/p'").replace("\n", "")
                gateway = run(f"ip route show 0.0.0.0/0 dev {iff} | cut -d\  -f3").replace("\n", "")
                if ipp != "" and iff != "lo":
                    ips[f"{iff}"] = {"ip": ipp, "gateway": gateway}
        
            with open("servermand.output", "w") as f:
                f.write(str(ips))
            info("ip addresses written to output file")
        case "set":
            info("setting ip addresses")
            newips = literal_eval(command[1])
            with open("servermand.output", "w") as f:
                f.write("loading")
            info("reading data")
            for ip in newips:
                info(f"{ip.replace('.', ' ')}: {newips[ip]}")
            for ip in newips:
                ip = ip.replace(".", " ").split()
                thingtoset = ip[1]
                interface = ip[0]
                ip = newips[".".join(ip)]
                info(f"setting {thingtoset} of {interface} to {ip}")
                if thingtoset == "ip":
                    run(f"ip addr replace {ip}/24 dev {interface}")
                elif thingtoset == "gateway":
                    oldgateway = run(f'ip route show 0.0.0.0/0 dev {interface} | cut -d\  -f3').replace('\n', '')
                    run(f"ip route delete default via {oldgateway}")
                    run(f"ip route add default via {ip} dev {interface}")
            info("complete")
            info("reboot required to apply changes")
            with open("servermand.output", "w") as f:
                f.write("ok")
        case "" | _:
            info("help for command internet")
            info("addresses, noargs: write ip addresses to output file in the form of a dict/object")
            info("set, newips: change the IP address/gateway, newips: the new ip addresses to set in dict form")

def stop():
    info("stopping")
    remove("servermand.input")
    remove("servermand.output")
    remove("servermand.pid")
    exit(0)

def read():
    while True:
        with open("servermand.input", "r+") as f:
            command = f.read().split()
            try:
                match command[0]:
                    case "internet":
                        command.pop(0)
                        f.truncate(0)
                        internet(command)
                        continue
                    case "help":
                        command.pop(0)
                        f.truncate(0)
                        help(command)
                        continue
                    case "stop":
                        f.truncate(0)
                        stop()
                        continue
                    case "":
                        continue
                    case _:
                        f.truncate(0)
                        error(f"command not found: {command[0]}")
                        continue
            except IndexError:
                pass
                    

def main():
    with open("servermand.pid", "w") as f:
        f.write(str(getpid()))
    info("starting servermand v0.0.0...")
    if getuid() != 0:
        error("not running as root")
        info("stopping")
        exit(1)
    mode = "normal"
    info("loading settings...")
    settings = load(open("settings.json", "r+"))
    info("creating temp files...")
    if getcwd() != "/serverman":
        warn("not started from /serverman, running in source mode")
        mode = "source"
    else:
        error("running servermand in normal mode is not currently supported.")
        error("please run servermand from the source folder.")
        exit(1)
    warn("temp files are in this directory")
    open("servermand.input", "w").close()
    open("servermand.output", "w").close()
    open("servermand.log", "w").close()
    
    chmod("servermand.input", stat.S_IRWXO)
    chmod("servermand.output", stat.S_IRWXO)
    chmod("servermand.log", stat.S_IRWXO)
    chmod("servermand.pid", stat.S_IRWXO)
    info("started")
    read()
    

if __name__ == "__main__":
    main()