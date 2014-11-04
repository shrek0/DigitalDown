#!/usr/bin/env python

import urllib2, re, argparse
from sys import argv
from urllib import urlretrieve
from lxml.html import fromstring
from sys import stdout
import math

# 
# Author: MrBot,Shrek0
# Version: 0.2
#
# Description: 
#	download DigitalWhisper issues.
#

__VERSION__ = 0.2


# Taken from "https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python" with some changes
def size(size):
   size_name = ('B',"KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   if(size < 1024):
	   return (str(size), size_name[0])
   i = int(math.floor(math.log(size,1024)))
   p = math.pow(1024,i)
   s = round(size/p,2)
   if (s > 0):
       return (s,size_name[i])
   else:
       return '0B'

def padding(var, to_padding, padding_char = ' '):
	return str(var) + ((to_padding - len(str(var))) * padding_char)

class DigitalWhisper(object):
	
	def __init__(self,options):
		self._options = options

	def fix_link(self, link):
		return link.replace('../../', '')
	
	def clean_bad_chars(self,string):
		return string.replace('/', 'or')
	
	def get_file_name(self, link):
		return re.findall('files/Zines/0x[A-F0-9]+/([-A-Za-z0-9.\/_]+).pdf', link)[0]
	
	def get_format_save_name(self, filename, title, id):
		save_name = self._options.SaveFormat
		
		array = ['#id', '#filename', '#title'] 
		replaces = [str(id), filename, title]
		
		for word,replace  in zip(array, replaces):
			save_name = save_name.replace(word, replace)
		
		return self.clean_bad_chars(save_name)
		
	def get_pdf_list(self,titles, links, id):
		pdfs  = []
		
		for link,title in zip(links, titles):
			pdfs.append({ 
				'id': id,
				'link':self.fix_link(link),
				'title':title,
				'save_name':self.get_format_save_name(self.get_file_name(link), title, id), 
				'filename':self.get_file_name(link)
				})
		
		return pdfs
		
        def download(self, id):
                zines = self.get_sheet(id)
                zines_len = len(zines)
                counter = 1
                for z in zines:
                        path = self._options.path + '/' + z['save_name']
			print '(%d/%d) Downloading %s to %s:' % (counter, zines_len, z['link'], path)
                        self.save(path, z['link'])
                        
                        counter+=1
        def last(self):
                source = self.request("http://www.digitalwhisper.co.il/")
                return int(re.findall('<a href="http://www.digitalwhisper.co.il/issue([0-9]+)"><b>', source)[0])
        def get_sheet(self, id):
		id = int(id)
		
		pattern = '//td/a/'
                source = self.request("http://www.digitalwhisper.co.il/issue%d" %  id)
                                
                new = []
                
		if self._options.Format == 'many':
			source = fromstring(source)
			source.make_links_absolute("http://www.digitalwhisper.co.il")
			
			links = source.xpath(pattern + "@href")
			titles = source.xpath(pattern + "text()")
			
			if len(titles) < 2 or len(links) < 2:
					titles += source.xpath("//td/font/a/text()")
					titles += source.xpath("//td/a/font/text()") 
					links += source.xpath("//td/font/a/@href")
			if len(titles) < 2 or len(links) < 2:
				titles += source.xpath("//span/a/text()")
				links += source.xpath("//span/a/@href")

			if len(links) != len(titles):
				if self._options.SaveFormat.find('#title') > -1:
					self._options.SaveFormat = '#filename.pdf'
					print "Warning: links and titles length is not equal! Setting save format '#filename.pdf' id:%d" % (id)
				else:
					print "Warning: links and titles length is not equal! id: %d" % (id)
				
				if(len(links) < len(titles)):
					while(len(links) < len(titles)):
						links.append('noname')
				if(len(titles) < len(links)):
					while(len(titles) < len(links)):
						titles.append('noname')
		else:
			links = []
			titles = []
			links.append('http://www.digitalwhisper.co.il/files/Zines/0x%02X/DigitalWhisper%d.pdf' % (id, id))
			titles.append('Digital Whisper Issue %d' % id)
		
		new = self.get_pdf_list(titles, links, id)

                return new
	
	def report_hook(self,count,block_size,total_size):
		percentage = (count * block_size)*100/total_size
		stdout.write('\r%s %% : ' % padding(str(percentage), 3))
		
		stdout.write(padding(percentage * '#', 101))
		
		count = size(count * block_size)
		count = '%s %s' % (padding(count[0], 6), padding(count[1], 2))
		
		total_size = size(total_size)
		total_size = '%s %s' % (total_size[0], total_size[1])
		
		stdout.write('| %s of %s'% (count, total_size))
		
		stdout.flush()
	
        def save(self, path, url):
                urlretrieve(url, path, self.report_hook)
                print
        def request(self, url):
                c = urllib2.urlopen(url)
                data = c.read()
                c.close()
                return data
 
def main(options):	
	dw = DigitalWhisper(options)
	
	if options.Download == 'last':
		dw.download(dw.last())
	elif options.Download.find('-') > 0: #range
		range_ = options.Download.split('-')
		for i in range(int(range_[0]), int(range_[1])+1):
			dw.download(i)
	elif options.Download == 'all':
		for i in range(1, dw.last()):
			dw.download(i)
	else:
		dw.download(options.Download)
	
	return
 
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Digital Whisper Downloader')
	parser.add_argument("-d","--download", dest="Download", help="Digital Whisper ID for download, IDs range (Example: 10-20), all or last [default: last]", metavar="ID", default='last') 
	#parser.add_argument("-a","--alert", dest="AlertMail", help="Send mail when new Digital Whisper is published", metavar="MAIL")
	parser.add_argument("-f", "--format", dest="Format", help="Digital Whisper format: one PDF [default], or many PDFs", metavar='FORMAT',default="one")
	parser.add_argument("-s", "--save", dest="SaveFormat", help="Save format [default: #filename.pdf]. Example: #id_#filename_#title_TEXT -> 4_DW4-1-HTTP-Fingerprints_HTTP Fingerprints_TEXT)", metavar='FORMAT',default="#filename.pdf")
	parser.add_argument(dest="path", help="Save files path",default="./", nargs='?')

	args = parser.parse_args()
	
	main(args)
