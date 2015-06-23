#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from re import findall
from sys import argv
from sys import stdout, exit
from urllib.request import urlopen
from urllib.request import urlretrieve
import math

# 
# Author: MrBot,Shrek0
# Version: 0.5
#
# The first version: http://www.hacking.org.il/showthread.php?t=4960
#
# Description: 
#     Download DigitalWhisper issues.
#

__VERSION__ = 0.5

""" getTerminalSize()
 - get width and height of console
 - works on linux,os x,windows,cygwin(windows)
 
 src: https://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python.
"""

__all__=['getTerminalSize']

current_os = ''

def getTerminalSize():
   import platform
   current_os = platform.system()
   tuple_xy=None
   if current_os == 'Windows':
       tuple_xy = _getTerminalSize_windows()
       if tuple_xy is None:
          tuple_xy = _getTerminalSize_tput()
          # needed for window's python in cygwin's xterm!
   if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
       tuple_xy = _getTerminalSize_linux()
   if tuple_xy is None:
       tuple_xy = (80, 25)      # default value
   return tuple_xy


def getTerminalSize():     
     global current_os
     
     if(current_os == ''):
          import platform
          current_os = platform.system()
          
     tuple_xy=None
     
     if current_os == 'Windows':
          tuple_xy = _getTerminalSize_windows()

          if tuple_xy is None:
               tuple_xy = _getTerminalSize_tput()  # needed for window's python in cygwin's xterm!
          
     if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
          tuple_xy = _getTerminalSize_linux()
          
     if tuple_xy is None:
          tuple_xy = (80, 25)      # default value
       
     return tuple_xy

def _getTerminalSize_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _getTerminalSize_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
       import subprocess
       proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       cols=int(output[0])
       proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       rows=int(output[0])
       return (cols,rows)
    except:
       return None


def _getTerminalSize_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

# src: "https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python" with some changes
def size(size):
   size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   if(size < 1024):
           size = float(size)/1024
           return (str(size)[0:4],size_name[0])
   i = int(math.floor(math.log(size,1024)))
   p = math.pow(1024,i)
   s = round(size/p,2)
   return (s,size_name[i])

def padding(var, to_padding, padding_char = ' '):
     return str(var) + ((to_padding - len(str(var))) * padding_char)

class DigitalWhisper(object):
     
     def __init__(self,options):
          self._options = options
          
          self.files = []
          
          self._html_cache_data = ''
          self._html_cache_id = 0
          
          if self._options.Format == 'many':
               self._lxml_cache_data = ''
               self._lxml_cache_id = 0

               try:
                    from lxml.html import fromstring
               except ImportError:
                    print("Error: lxml is not installed.")
                    from sys import exit
                    exit(1)
               global fromstring
          
          self._last_id_cache_data = -1
          
          self._titles_cache_data = []
          self._titles_cache_id = []
          
          self.content_list = ['idd', 'id', 'title', 'filename']
          
     ## Global functions.
     
     # Public function, add id for download.
     def add_to_download(self, id):
          self.files += self._get_files_list(id)
          
     # Public function, download all files that added before.
     def download(self):
               counter = 1
               files_len = len(self.files)
                
               for f in self.files:
                    path = self._options.path + '/' + f['save_name']
                    print('(%d/%d) Downloading %s to %s:' % (counter, files_len, f['link'], path))
                    self._save(path, f['link'])
                    
                    counter+=1
                    
     # Public function, return the last id. 
     def last(self):
          if self._last_id_cache_data == -1:
               source = self._request("http://www.digitalwhisper.co.il/")
               self._last_id_cache_data = int(findall('<a href="http://www.digitalwhisper.co.il/issue([0-9]+)"><b>', source)[0])
               
          return self._last_id_cache_data
     
     # Private function, return list of files to download.
     def _get_files_list(self, id):
          files  = []
          links = self._get_all_links(id)
                    
          for idd,link in enumerate(links):
               files.append({'link':self._fix_link(link), 'save_name':self._get_format_save_name(link, id, idd)})
                         
          return files

     ## Link functions.
     
     # Private function, return fixed link by link.
     def _fix_link(self, link):
          return link.replace('../../', '')
     
     def _get_all_links(self, id):
          links = []
          
          if self._options.Format == 'many':
               if self._lxml_cache_id != id:
                    self._download_html(id)
                    
                    self._lxml_cache_data = fromstring(self._html_cache_data)
                    self._lxml_cache_id = id
                    
               self._lxml_cache_data.make_links_absolute("http://www.digitalwhisper.co.il")
               
               xpaths = ['//tbody/tr/td/a',
                         '//tbody/tr/td/span/a',
                         '//tbody/tr/td/font/a']
               
               for xpath in xpaths:
                    links += self._lxml_cache_data.xpath(xpath+'/@href')
                    if len(links) > 2:
                         break
                         
          elif self._options.Format == 'one':
               links.append('http://www.digitalwhisper.co.il/files/Zines/0x%02X/DigitalWhisper%d.pdf' % (id, id))
          
          return links
     
     ## Title functions.
     
     # Private function, return title by id and idd.
     def _get_title(self, id, idd):
          if self._titles_cache_id != id:
               self._titles_cache_data = self._get_all_titles(id)
               self.titles_cache_id = id
          
          if len(self._titles_cache_data) <= idd: # if the titles length
               print("Warning: links and titles length is not equal! may be a problem with the titles. id:%d" % (id))
               return "Untitled %d|%d" % (id, idd)
               
          return self._titles_cache_data[idd]
     
     # Private function, return all titles of id.
     def _get_all_titles(self, id):
          titles = []
          
          if self._options.Format == 'many':
               # No need to check the cache again, get_all_links method was called before and did those things. 
              
               xpaths = ['//tbody/tr/td/a',
                         '//tbody/tr/td/a/font',
                         '//tbody/tr/td/span/a',
                         '//tbody/tr/td/font/a']

               for xpath in xpaths:
                    titles += self._lxml_cache_data.xpath(xpath+'/text()')
                    if len(titles) > 2:
                         break
                    
          elif self._options.Format == 'one':
               titles.append('Digital Whisper Full Issue %d' % id)
          
          return titles
     
     ## File name functions.
     
     # Private function, return file without bad characters.
     def _clear_bad_chars(self, string):
          return string.replace('/', 'or').replace('\\', 'or')

     # Private function, return file name by link.
     def _get_file_name(self, link):
          return findall('files/Zines/0x[A-F0-9]+/([-A-Za-z0-9.\/_]+).pdf', link)[0]
     
     # Private function, return the required contents for the file save format.
     # Used in get_format_save_name function.
     def _get_required_contents(self):
          contents = []
          
          for c in self.content_list:
               if self._options.SaveFormat.find(c) > -1:
                    contents.append(c)
                    
          return contents
     
     # Private function, return the save name.
     def _get_format_save_name(self,link, id, idd):
          save_name = self._options.SaveFormat
          replaces = []
          words = []
          
          required_contents = self._get_required_contents()
          
          for c in required_contents:
               words.append('#' + c)
               if c == 'idd':
                    replaces.append(str(idd))
               elif c == 'id':
                    replaces.append(str(id))
               elif c == 'title':
                    replaces.append(self._get_title(id, idd))
               elif c == 'filename':
                    replaces.append(self._get_file_name(link))
                              
          for word,replace in zip(words, replaces):
               save_name = save_name.replace(word, replace)
          
          return self._clear_bad_chars(save_name)
     
     ## Download pdf functions.
     
     # Private function, show report about the download. Used in 'save' function.
     def _report_hook(self, count, block_size, total_size):
          x,y = getTerminalSize()
          x = x-31
          
          out = "\r" # return to line begining.
                
          percentage = int((count * block_size)*100/total_size)
          progress = int(percentage*x/100)
          out += '%s %% : ' % padding(str(percentage), 3)
          
          out += '[' + padding(progress * '#', x+1) + ']'
          
          count = size((count * block_size)/1024)
          count = '%s %s' % (padding(count[0], 4), padding(count[1], 2))
          
          total_size = size(total_size/1024)
          total_size = '%s %s' % (total_size[0], total_size[1])
          
          out += '| %s of %s'% (count, total_size)
          
          stdout.write(out)
          
          stdout.flush()
     
     def _save(self, path, url):
               urlretrieve(url, path.encode('utf8'), self._report_hook)
               print
                        
     ## Download html functions.
     
     # Private function, get response by url.
     def _request(self, url):
          c = urlopen(url)
          data = c.read().decode('utf8')
          c.close()
          return data
     
     # Private function, download html of id if it not in the cache.
     def _download_html(self, id):
          if self._html_cache_id != id:
               self._html_cache_id = id
               self._html_cache_data = self._request("http://www.digitalwhisper.co.il/issue%d" %  id)

def main(options):     
     dw = DigitalWhisper(options)
     
     if options.Download == 'last':
          dw.add_to_download(dw.last())
     elif options.Download.find('-') > 0: #range
          issues_range = options.Download.split('-')
          
          if issues_range[1] == 'last': # range: something to last (9-last).
               issues_range[1] = dw.last()
               
          for i in range(int(issues_range[0]), int(issues_range[1])+1):
               dw.add_to_download(i)
               
     elif options.Download == 'all':
          for i in range(1, dw.last()):
               dw.add_to_download(i)
     else:
          dw.add_to_download(int(options.Download))
          
     # Now, download the files:
     dw.download()
     
     return
 
if __name__ == '__main__':
     
     parser = argparse.ArgumentParser(description='Digital Whisper Downloader')
     parser.add_argument("-d","--download", dest="Download", help="Digital Whisper ID for download, IDs range (Example: 10-20, 7-last), all or last [default: last]", metavar="ID", default='last') 
     parser.add_argument("-f", "--format", dest="Format", help="Digital Whisper format: one PDF [default], or many PDFs", metavar='FORMAT',default="one")
     parser.add_argument("-s", "--save", dest="SaveFormat", help="Save format [default: #filename.pdf]. Example: #id_#filename_#title_TEXT -> 4_DW4-1-HTTP-Fingerprints_HTTP Fingerprints_TEXT)", metavar='FORMAT',default="#filename.pdf")
     parser.add_argument("-v", "--version", action='version', version=str(__VERSION__))
     parser.add_argument(dest="path", help="Save files path",default="./", nargs='?')

     args = parser.parse_args()
     
     main(args)
