#!/usr/bin/env python
import requests
import json
import time
from os.path import expanduser

class hollaback(object):
    """
    Used to interact with the hollaback callback server
    """

    cred_file = expanduser("~") + "/.config/hollaback.json"

    def __init__(self):
        self.ses = requests.Session()
        self.parse_cred_file()
        if not self.login():
            raise Exception("Login failed")
            

    def login(self):
        """ 
        Log into the api server
        """
        url = "%s%s" % (self.serv, "/holla/login.php")
        res = self.ses.post(url, data=self.creds)

        if res.ok and res.json()["Success"]:
            return True
        else:
            return False

    def check(self, token):
        url = "%s%s" % (self.serv, "/holla/check.php")
        res = self.ses.get(url, params={"token":token})
        try:
            return res.json()
        except:
            return res.content
        
        
    def enque(self, comment="", test_name="", cust_name="", reply_method="", ttl=0, consume=0):
        url = "%s%s" % (self.serv, "/holla/save.php")
        res = self.ses.post(url, data=locals())
        return res.json()

        
    def parse_cred_file(self):
        with open(self.cred_file, "r") as fp:
            data = json.load(fp);
        self.creds = data["creds"]
        self.serv  = data["serv"]

def _holla_fail(msg):
    print(msg)
    exit(1)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Interact with a Hollaback Server")
    parser.add_argument('-g','--get', action="store_true", help='Get a callback url')
    parser.add_argument('-c','--check', action="store_true", help='Check on a callback token (-t required)')
    parser.add_argument('-b','--block', action="store_true", help='Check every second until callback is used (-t required)')
    parser.add_argument('-t','--token', help='Token value')
    parser.add_argument('--comment', help='Comment to save on server')
    parser.add_argument('--test_name', help='Test name to save on server')
    parser.add_argument('--cust_name', help='Customer name to save on server')
    parser.add_argument('--ttl', help='TTL of callback URL')
    parser.add_argument('--reply_method', help='How it should respond') # does not work on server yet
    parser.add_argument('--consume', help='Int number of times used before consumed')

    args = parser.parse_args()
    if args.get and args.check:
        _holla_fail(  "Cant check and get yet" )


    holla = hollaback()
    if args.get:
        if args.token: _holla_fail("Can't use token here, exiting")
        a =  vars(args)
        for i in ["get", "check", "block", "token"]: del a[i]
        print a
        a = holla.enque(**a)
        print( "token: %s" % a["token"] )
        print( "url: %s" % a["url"] )
    elif args.check:
        if not args.token: _holla_fail("Need token to check")
        d = holla.check(args.token)
        if d["Success"] != True:
            _holla_fail("Could not get info for token %s\nmsg: %s" % ( args.token, d["msg"]))

        comment = d["comment"]
        del d["comment"]
        del d["Success"]
        for key, value in d.iteritems():
            if value:
                print "%-15s %s" % (key, value)
        if comment:
            print "Comment:"
            print comment
    elif args.block:
        from time import sleep
        if not args.token: _holla_fail("Need token to check")
        d = holla.check(args.token)
        if d["Success"] != True:
            _holla_fail("Could not get info for token %s\nmsg: %s" % ( args.token, d["msg"]))

        start = d[ "visited" ]
        print ("URL current visit: %d waiting till it is %d" % ( start, start+1 ))
        while True:
            sleep(1)
            d = holla.check(args.token)
            if d["visited"] <= start:
                continue
            else:
                print("Got visits!!!")
                break

        comment = d["comment"]
        del d["comment"]
        del d["Success"]
        for key, value in d.iteritems():
            if value:
                print "%-15s %s" % (key, value)
        if comment:
            print "Comment:"
            print comment
