#!/usr/bin/env python

from os import getcwd, popen, getpid, remove
from sys import exit
from json import load, dump
from time import sleep

mode = "normal"
settings = load(open("settings.json", "r+"))
with open("servermand.pid", "w") as f:
    f.write(str(getpid()))
open("servermand.input", "w").close()
open("servermand.output", "w").close()
open("servermand.log", "w").close()

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

def internet(command):
    match command:
        case "status":
            info("getting internet status...")
            with open("servermand.output", "w") as f:
                f.write(run("ip a").replace("\n", "<br>"))
            info("internet status written to output file")
        case "interfaces":
            info("getting internet interfaces...")
            with open("servermand.output", "w") as f:
                f.write(run("ls /sys/class/net/").split())
            info("ip addresses written to output file")
        case "addresses":
            info("getting internet addresses...")
            info("loading list of interfaces...")
            ifs = run("ls /sys/class/net/").split()
            info("getting each interface's ip address")
            ips = ""
            for i in ifs:
                ip = run(f"ip -f inet addr show {i} | sed -En -e 's/.*inet ([0-9.]+).*/\\1/p'").replace("\n", " ")
                if ip != "" and i != "lo":
                    ips += ip
            with open("servermand.output", "w") as f:
                f.write(ips)
            info("ip addresses written to output file")
        case "" | _:
            info("help for command internet")
            info("status: write internet status to output file")
            info("addresses: write ip addresses to output file")

def stop():
    info("stopping")
    open("servermand.input", "w").close()
    open("servermand.output", "w").close()
    remove("servermand.pid")
    exit(0)

def read():
    while True:
        with open("servermand.input", "r+") as inp:
            command = inp.read().split()
            try:
                match command[0]:
                    case "internet":
                        internet(command[1])
                        inp.truncate(0)
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
    info("starting servermand v0.0.0")
    if getcwd() != "/serverman":
        warn("not started from /serverman, running in source mode")
        warn("input file is ./serverman.input")
        mode = "source"
    info("started")
    read()
    

if __name__ == "__main__":
    main()