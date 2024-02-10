#!/usr/bin/env python

from os import getcwd, popen, getpid, remove
from sys import exit
from json import load, dump
from time import sleep


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
    match command:
        case "internet":
            internet(help)
        case "" | _:
            info("servermand commands")
            info("help: show this message")
            info("stop: stop servermand")
            info("internet: modify settings related to internet connection")
def internet(command):
    match command:
        case "addresses":
            info("getting internet addresses...")
            info("loading list of interfaces...")
            ifs = run("ls /sys/class/net/").split()
            info("getting each interface's ip address")
            ips = {}
            for i, iff in enumerate(ifs):
                print(ips)
                ipp = run(f"ip -f inet addr show {iff} | sed -En -e 's/.*inet ([0-9.]+).*/\\1/p'").replace("\n", "")
                gatewayy = run(f"ip route show 0.0.0.0/0 dev {iff} | cut -d\  -f3").replace("\n", "")
                if ipp != "" and iff != "lo":
                    ips[f"{iff}"] = {"ip": ipp, "gateway": gatewayy}
        
            with open("servermand.output", "w") as f:
                f.write(str(ips))
            info("ip addresses written to output file")
        case "" | _:
            info("help for command internet")
            info("status: write internet status to output file")

def stop():
    info("stopping")
    remove("servermand.input", "w")
    remove("servermand.output", "w")
    remove("servermand.pid")
    exit(0)

def read():
    while True:
        with open("servermand.input", "r+") as inp:
            command = inp.read().split()
            try:
                match command[0]:
                    case "internet":
                        inp.truncate(0)
                        internet(command[1])
                        continue
                    case "stop":
                        stop()
                    case "":
                        continue
                    case _:
                        error(f"command not found: {command[0]}")
                        inp.truncate(0)
                        continue
            except IndexError:
                pass
                    

def main():
    with open("servermand.pid", "w") as f:
        f.write(str(getpid()))
    info("starting servermand v0.0.0...")
    mode = "normal"
    info("loading settings...")
    settings = load(open("settings.json", "r+"))
    info("creating temp files...")
    if getcwd() != "/serverman":
        warn("not started from /serverman, running in source mode")
        warn("temp files are in this directory")
        open("servermand.input", "w").close()
        open("servermand.output", "w").close()
        open("servermand.log", "w").close()
        mode = "source"
    else:
        error("running servermand in normal mode is not currently supported.")
        error("please run servermand from the source folder.    ")
        exit(1)
    info("started")
    read()
    

if __name__ == "__main__":
    main()