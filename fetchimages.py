import urllib2
import re
import os
import sys
import tempfile
import logging
from datetime import date
from os.path import basename
from os.path import splitext
from os.path import exists
from urlparse import urlsplit
from urlparse import urljoin
from urlparse import urlparse

BUF_SIZE=65536

class FetchImages:
    """Image fetcher class"""
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    def __init__(self,webPageURL):
        """Initializes instance"""
        self.logger = self.setLogger('FetchImages')
        self.baseurl = webPageURL
        self.headers={'User-Agent':self.user_agent}
        self.image_urls = []
        self.tempdir_name = ''
        self.tempfile_name = ''
        self.fetchimages_url_map = {}
        self.saveimages_url_map = {}
        self.logger.info('FetchImages instance created')

    def setLogger(self, name):
        logger = logging.getLogger(name)
        hdlr = logging.FileHandler('%s.log'%name)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.DEBUG)
        return logger

    def fetchImageUrls(self):
        """Fetches image urls from webpage"""

        print 'Fetch Image URLs'
        self.logger.info('Fetch Image URLs')
        
        status=False
        try:
            request=urllib2.Request(self.baseurl,None,self.headers) #The assembled request
            response = urllib2.urlopen(request)
            lines = response.read() # The data u need
            p=re.compile('<[Ii][Mm][Gg](.*[\s]+)[Ss][Rr][Cc][\s]*=[\s]*(")(.*?")')

            iterator =p.finditer(lines)
            for match in iterator:
                src= match.group()                
                p=re.compile('(.*src *= *)(")(.*)(")')
                slist= p.split(src)
                imgurl = slist[3]
                url = self.getAbsoluteUrl(imgurl)
                if url not in self.image_urls:
                	self.image_urls.append(url)
                	self.logger.info('Image URL : %s' % url)
                
            if self.createImageUrlMap() > 0:
                status=True
                
        except urllib2.HTTPError, e:
            self.logger.error('Failed to fetch web page.')
            self.logger.error('Error code: %s' % e.code)
            print 'Failed to fetch web page.'
        except urllib2.URLError, e:
            self.logger.error('Failed to open web page. Server request error.')
            self.logger.error('Reason: %s' % e.reason)
            print 'Failed to open web page. Server request error.'
        except ValueError, e:
            self.logger.error('Failed to open image url. Invalid URL')
            self.logger.error('Reason: %s' % e.reason)
            print 'Failed to open image url. Invalid URL'
        except IOError, e:
            self.logger.error('I/O error: %s, %s' %(e.errno, e.strerror))
            print 'I/O error, failed to open web page.'
        except:
            self.logger.error('Unexpected error: %s' % sys.exc_info()[0])
            print 'Unexpected error, failed to open web page.'
        finally:
            return status
            
  
    def downloadImages(self):
        """Download images and save to disk"""

        print 'Download Images'
        self.logger.info('Download Images')

        self.createTempImagesDir()
        
        for fname in self.fetchimages_url_map.keys():
            try:
                self.logger.info('Download image URL :%s' % self.fetchimages_url_map[fname])
                fpath = os.path.join(self.tempdir_name, fname)
                saveimage = file(fpath, "wb")
                request=urllib2.Request(self.fetchimages_url_map[fname],None,self.headers) #The assembled request
                fhandle = urllib2.urlopen(request)
                while True:
                    buf = fhandle.read(BUF_SIZE)
                    if len(buf) == 0:
                        break
                    saveimage.write(buf)      
            except urllib2.HTTPError, e:
                self.logger.error('Failed to download image file from web page.')
                self.logger.error('Error code: %s' % e.code)
            except urllib2.URLError, e:
                self.logger.error('Failed to open image url. Server request error.')
                self.logger.error('Reason: %s' % e.reason)
            except ValueError, e:
                self.logger.error('Failed to open image url. Invalid URL')
                self.logger.error('Reason: %s' % e.reason)
            except IOError, e:
                self.logger.error('I/O error: %s, %s' %(e.errno, e.strerror))
            except:
                self.logger.error('Unexpected error: %s' % sys.exc_info()[0])
            else:
                saveimage.close()
                fhandle.close()
                self.saveimages_url_map[fname]=self.fetchimages_url_map[fname]
                
        self.saveImageUrlToFile()

    def getAbsoluteUrl(self,url):
        """Get absolute image URL"""

        if url.startswith('http://'):
            # absolute image URL
            pass
        elif url.startswith('https://'):
            # absolute image URL
            pass
        elif url.startswith('//'):
            # absolute image URL, prefix scheme and return url
            o = urlparse(self.baseurl)
            url = "%s:%s"%(o.scheme, url[:])
        else:
            # relative image URL, construct absolute URL from this
            while True:
                if url.startswith('../'): # handle special case
                    url = url[2:]
                else:
                    break
            url = urljoin(self.baseurl, url[:])
        return url
        
    def createImageUrlMap(self):
        """Creates Image URL map"""

        self.logger.info('Create image URL map')

        d = date.today()
        filenamebase = '{:%Y-%m-%d}'.format(d)

        counter=0
        for url in self.image_urls:
            imagefilename = filenamebase + "_%d" % counter #prepare image file name using datetime
            base=basename(urlsplit(url)[2])
            filenameext=splitext(base)
            fileExt=filenameext[1]
            
            if fileExt not in '':
                imagefilename = imagefilename + filenameext[1]                
            else:   # skip image url without ext
                continue
            self.fetchimages_url_map[imagefilename] = url
            counter=counter+1

        return len(self.fetchimages_url_map)

    def createTempImagesDir(self):
        """Creates a temp folder to save image files"""

        self.logger.info('Create temp directory to save Images')

        if self.tempdir_name in '':
            self.tempdir_name = tempfile.mkdtemp("_images")

    def saveImageUrlToFile(self):
        """Saves Image urls to a temp file"""

        print 'Save Image urls to temp file'
        self.logger.info('Save Image urls to temp file')
        
        if self.tempfile_name in '':
            fd, self.tempfile_name = tempfile.mkstemp("_imageurls.txt")

        try:
            fhandle = open(self.tempfile_name,'w+')
        except IOError, e:
            self.logger.error('I/O error: %s, %s' %(e.errno, e.strerror))
        except:
            self.logger.error('Unexpected error: %s' % sys.exc_info()[0])
        else:
            for url in self.saveimages_url_map.values():
                fhandle.write(url+'\n')
            fhandle.close()
            os.close(fd)

def main(webPageURL):
    
    downloader = FetchImages(webPageURL)
    if downloader.fetchImageUrls():
        downloader.downloadImages()
    
    print "\nNumber of URLs fetched from web page: ",len(downloader.fetchimages_url_map)
    print "Number of Images saved to disk :",len(downloader.saveimages_url_map)

    if len(downloader.saveimages_url_map) > 0:
        print "\nImages saved to : %s" % downloader.tempdir_name
        print "Image URLs saved to : %s\n" % downloader.tempfile_name

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print "Usage: fetchimages.py [http://Enter URL..]"
    
