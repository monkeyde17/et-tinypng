# coding : utf-8

from os.path import dirname
from urllib2 import Request, urlopen
from base64 import b64encode

import json
import threading
import os
import time


key = ""
outputdir = ""
inputdir = ""

filecount = 0

isize = 0
osize = 0

class shrink_thread(threading.Thread):
    def __init__(self, path, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self.path = path

    def run(self):
        tmppath = os.path.join(outputdir, self.path)
        if not os.path.exists(tmppath):
            try:
                os.makedirs(tmppath)
            except Exception as e:
                pass

        #inputfile = self.path + os.sep + self.filename
        inputfile = os.path.join(self.path, self.filename)
        #outputfile = tmppath + os.sep + self.filename
        outputfile = os.path.join(tmppath, self.filename)

        global isize
        global osize
        global filecount

        if not os.path.exists(outputfile):
            print "The input file : " + inputfile
            request = Request("https://api.tinypng.com/shrink", open(inputfile, "rb").read())

            # add the auth
            auth = b64encode(bytes("api:" + key)).decode("ascii")
            request.add_header("Authorization", "Basic %s" % auth)

            # http post request
            response = urlopen(request)


            if response.getcode() == 201:
                # get the json result
                rejson = json.loads(response.read())

                # get the url
                result = urlopen(rejson["output"]["url"]).read()

                print "The output file : " + outputfile
                open(outputfile, "wb").write(result)

                isize += rejson["input"]["size"]
                osize += rejson["output"]["size"]
            else:
                # Something went wrong! You can parse the JSON body for details.
                print "Error Code : " + response.getcode()
                print "Compression failed"

        else:
            pass
            #print "_______________Exists File______________ " + inputfile

        # end the thread
        #self.thread_stop = True
        #filecount = filecount - 1
        self.stop()

        #if filecount <= 0:
            #print "====================================="
            #print "input size : " + str(isize)
            #print "output size : " + str(osize)
            #print "rate : " + str(1.0 * osize / isize)
           
    def stop(self):
        global filecount
        self.thread_stop = True
        filecount = filecount - 1

def shrink_png_by_path(path):
    global filecount
    if os.path.isdir(path):
        #print "current path : " + path
        for curfile in os.listdir(path):
            #nextpath = path + os.sep + curfile
            nextpath = os.path.join(path, curfile)
            if os.path.isdir(nextpath):
                shrink_png_by_path(nextpath)
            elif curfile.lower().endswith(".png") or curfile.lower().endswith(".jpg"):
                filecount = filecount + 1
                #print "the input file : " + nextpath
                shrink_thread(path, curfile).start()
                #time.sleep(0.1)
    else:
        print "The path is invalid"

def load_config():
    import ConfigParser
    global key
    global outputdir
    global inputdir

    config = ConfigParser.RawConfigParser()
    config.read("etiny.cfg")

    key = config.get("etiny", "key")
    inputdir = config.get("etiny", "inputdir")
    outputdir = "__" + config.get("etiny", "outputdir") + "__" + inputdir

if __name__ == "__main__":

    load_config();
    shrink_png_by_path(inputdir)

