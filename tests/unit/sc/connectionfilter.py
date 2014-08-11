import sclib
import os
import io
import StringIO
import urllib
import xml.sax

from sclib.sc.connection import SCConnection

class SCConnectionFilter(SCConnection):
    #===========================================================================
    # A filter connection class to simulate request. 
    # The class also capture Request and Response into specified result folder.
    #===========================================================================
    def __init__( self, host_base, broker_name=None, broker_passphase=None, 
                  result_path=None):
        SCConnection.__init__(self, host_base, broker_name, broker_passphase, True)

        # pseudo sample path
        self.result_path = result_path
        
        if os.path.isdir(self.result_path) == False:
            os.makedirs(self.result_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        fake = None
        resfile = reqfile = action.replace('/', '.')
        reqfile = os.path.join(self.result_path, '[Request]-%s %s.xml' % (method, reqfile ) )
        resfile = os.path.join(self.result_path, '[Response]-%s %s.xml' % (method, resfile) )


        # serialize Request data
        sclib.log.debug("---------- RESTFul Request ---------- " )
        sclib.log.debug('%s %s' % (method, action))
        rf = io.open(reqfile, 'w')
        if data:
            # Format request data
            formated = self.nice_format(data)
            rf.write(formated)

            # Debug - request data
            sclib.log.debug('\n%s' % (formated))
        rf.close()

        # make request to securecloud
        response = SCConnection.make_request(self, action, params, headers, data, method)
        if response:
            sclib.log.debug("---------- RESTFul Response (%s) ---------- " % (response.code) )
            body = response.read()
            
            # serialize Response data
            f = io.open(resfile, 'w')
            if body:
                # Format response data
                formated = self.nice_format(body)
                f.write(formated)

                # Debug - response data
                if formated: sclib.log.debug('\n%s' % (formated))
            f.close()

            #make fake response
            resfp = StringIO.StringIO(body)
            fake = urllib.addinfourl(resfp, response.info(), response.geturl(), response.getcode())
            

        sclib.log.debug("------------------------------------------\n")
        return fake

    def read_object(self, filepath, obj):
        
        f = io.open(filepath, 'rb')
        if f:
            body = f.read()
            h = sclib.handler.XmlHandler(obj, None)
            xml.sax.parseString(body, h)
            return obj
        return None

