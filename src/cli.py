#!/usr/bin/env python3
import sys, json, shutil, os

def list_mods():
    for p in sorted(os.listdir("modules")):
        m=f"modules/{p}/manifest.json"
        if os.path.isfile(m):
            d=json.load(open(m))
            print(f"{p}: extends {d.get('extends')}")

def install(name):
    src=f"modules/{name}"
    dst=f".jane_installed/{name}"
    shutil.rmtree(dst,ignore_errors=True)
    shutil.copytree(src,dst)
    print("installed",name)

def uninstall(name):
    shutil.rmtree(f".jane_installed/{name}", ignore_errors=True)
    print("removed",name)

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "list"
    if cmd=="list": list_mods()
    elif cmd=="install" and len(sys.argv)>2: install(sys.argv[2])
    elif cmd=="uninstall" and len(sys.argv)>2: uninstall(sys.argv[2])
    else:
        print('usage: cli.py [list|install <module>|uninstall <module>]')
