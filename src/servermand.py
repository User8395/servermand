#!/usr/bin/env python

from os import getcwd, popen, getpid, remove
from sys import exit
from json import load, dump

mode = "normal"
settings = load(open("settings.json", "r+"))
with open("servermand.pid", "w") as f:
    f.write(str(getpid()))

open("servermand.log", "w").write("")

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
    return popen(command).read().replace("\n", "<br>")

def internet(command):
    match command:
        case "status":
            info("getting internet status")
            with open("servermand.output", "r+") as f:
                f.write(run("ip a"))
        case "" | _:
            info("help for command internet")
            info("status: write internet status to servermand.output, command used is ip a")

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