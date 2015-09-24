DigitalDown
===========

![Logo](http://www.digitalwhisper.co.il/logo.png)

## Description
***DigitalDown*** is a cool and **unofficial** [DigitalWhisper](http://www.digitalwhisper.co.il/) magazine  downloader.

## Usage Examples:
 Download the all issues:
  ```console
  ./DigitalDown.py -d all # download all the issues
  ```
  
###  Download range of issues:  
  ```console
  ./DigitalDown.py -d 10-20  # download 10-20 issues
  ```
  ```console
  ./DigitalDown.py -d 10-last  # download 10-the last issue.
  ```
###  Set a custom file name format:
  ```console
  ./DigitalDown.py -s "#id.pdf" # Set the format name to "issue ID.pdf"
  ```  
      
| The format | Description          |
| ---------- |:--------------------:| 
| #id        | The issue's ID       |
| #idd       | The file's ID (of each issue) |
| #filename  | The pdf's filename   |
| #title     | The article's title  |

### Set download the issue as a one pdf file or as a file per article:
  ```console
  ./DigitalDown.py -f article # Set to download as a file per article.
  ```
  'article' will download a PDF file for each article in the issue and 'issue' will download only one PDF file for all the articles.  
  
###  Set the download path:
  ```console
  ./DigitalDown.py /usr/bin/../../home/../etc/passwd # Set the dowload path to /etc/passwd :smile:
  ```
  
  Enjoy!
