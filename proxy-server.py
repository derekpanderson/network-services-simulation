from twisted.internet import reactor
from twisted.web import resource, server
from twisted.python import log
import thread
import datetime
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
        logs['time']=time.time()
        self.logQueue.put(logs)

        filedata=open(self.filename,'r').read()
        request.setHeader("Server", "squid/3.1.10")
        request.setHeader("Via", "1.0 fl278 (squid/3.1.10)")

        return filedata    

def logData(dataFile,logQueue):
    day=datetime.date.today().day
    month=datetime.date.today().month
    year=datetime.date.today().year

    fileName=dataFile+"-"+str(month)+"-"+str(day)+"-"+str(year)
    logFile=open(fileName,'a')
    while True:
        log=logQueue.get()
        if day < datetime.date.today().day:
            day=datetime.date.today().day
            month=datetime.date.today().month
            year=datetime.date.today().year

            fileName=dataFile+"-"+str(month)+"-"+str(day)+"-"+str(year)
            logFile.close()
            logFile=open(fileName,'a')

        jsonData=json.dumps(log)
        logFile.write(jsonData+"\n")
	logFile.flush()


logQueue = Queue.Queue()
thread.start_new_thread(logData,("logfile",logQueue))

site = server.Site(MyResource("https://www.youtube.com/watch?v=nfWlot6h_JM","/tmp/youtube.html",logQueue))
reactor.listenTCP(80, site)
reactor.listenTCP(8080, site)
reactor.listenTCP(3128, site)
reactor.listenTCP(9064, site)
reactor.run() 

