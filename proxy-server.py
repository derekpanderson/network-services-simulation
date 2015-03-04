from twisted.internet import reactor
from twisted.web import resource, server
from twisted.python import log
from twisted.internet.defer import DeferredQueue
import thread
import time
import os.path
import urllib
import Queue
import json

class MyResource(resource.Resource):
    isLeaf = True
    def __init__(self,url,filename,logQueue):
        self.filename=filename
        self.logQueue=logQueue

        if not os.path.isfile(filename):
            htmlfile = urllib.URLopener()
            htmlfile.retrieve(url, filename)

    def render_GET(self, request):
        logs={}
        logs['headers']=request.getAllHeaders()
        logs['uri']= request.uri
        logs['args']= request.args
        logs['ip']= request.getClientIP()
        logs['port']= request.getHost().port

        self.logQueue.put(logs)

        filedata=open(self.filename,'r').read()
        request.setHeader("Server", "squid/3.1.10")
        request.setHeader("Via", "1.0 fl278 (squid/3.1.10)")

        return filedata    

def logData(dataFile,logQueue):
    logFile=open(dataFile,'a')
    
    while True:
        log=logQueue.get()
        jsonData=json.dumps(log)
        logFile.write(jsonData+"\n")


logQueue = Queue.Queue()
thread.start_new_thread(logData,("logfile.log",logQueue))

site = server.Site(MyResource("https://www.youtube.com/watch?v=nfWlot6h_JM","/tmp/youtube.html",logQueue))
reactor.listenTCP(80, site)
reactor.listenTCP(8080, site)
reactor.run() 

