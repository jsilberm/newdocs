#!/usr/bin/python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from PIL import Image
import requests
from io import BytesIO
import hashlib
from bs4 import BeautifulSoup
import time
import parse_gdoc
import sys
import argparse
import os
from datetime import datetime
import unicodedata
import re



###################################################################################################################################
#
#
# Dependencies:
# =============
#
# Python Modules:
# ---------------
# selenium
# chromium
# google-api-python-client
# google-auth-httplib2
# google-auth-oauthlib
# BeautifulSoup4
# python2-lxml
#
# Python code files dependencies (located in same dir):
# -----------------------------------------------------
# parse_gdoc.py
# readgdoc.py
# credentials.json
#
# Example 1:
# Read the doc <ID> hedless and store all bitmat images in /home/roger/final/images and store the md file in /home/roger/final 
#
# ./readgdoc headless -i <Document ID> -b "/home/roger/final/images" -d "/home/roger/final"
#
# Example 2:
# If the readgdoc.py scrip need to write images to a mounted path that is different than the md file will read the imnages, use relative path 
# (Lets assume that /my_mount_2_dest is mounted to: /home/roger/final, when readgdoc.py executes)
# Read the doc <ID> hedless and store all bitmat images in /my_mount_2_dest/images and store the md file in /my_mount_2_dest, with the md file references the images by relative path "./images"
#
# ./readgdoc headless -i <Document ID> -b "/my_mount_2_dest/images" -d "/my_mount_2_dest" -r "./images"
#
# Example 3:
# To scan the doc and get report only:
# ./readgdoc scan -i <Document ID>
#
###################################################################################################################################

class Paragraph:
    def __init__(self):
        self.alignment = None
        self.alignment_flag = False
        self.alignment_prev = None
        self.alignment_change = None

    def set_alignment(self, alignment):
        if self.alignment != alignment:
            self.alignment_change = self.alignment
        self.alignment_prev = self.alignment
        self.alignment = alignment

debug = False
headless = False
scan = False

username = "release@pensando.io"


home_dir = os.path.expanduser('~')
pwdfile = home_dir + "/.gdocs"
download_dir = home_dir + "/Downloads"
current_dir = os.getcwd()
doc_meta_dir = current_dir + '/meta4docs'

final_dir_bm = ""
final_dir_md = ""
bitmap_path_md = ""
site = None
vp = False
#args = None

raw_text = ""

DOCUMENT_ID = None
DOCUMENT_TITLE = None
DOCUMENT_URL = None
SUGGEST_MODE="PREVIEW_WITHOUT_SUGGESTIONS"

para = Paragraph()

doc_meta = {}
fonts_stats = {}
fonts_family_stats = {}
fonts_word = []
font_prev = None
fonts_size_word = []
font_size_prev = None
words_list = []
figure_list = []

Dcount = 0
fenced_flag = False
code_flag = False
bullet_flag = False
footnote_flag = False

bullet_count = 0
fenced_count = 0
footnote_count = 0
nestinglevel = ""
lists = {}
footnotes = {}
text_cache = ''

syntax_exlude_map={}
syntax_incusive_map={}

image_stats = {}
image_stats['drawing'] = 0
image_stats['bitmap'] = 0

escape_char = {}
escape_char['\t'] = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"


char_scrub = {}
char_scrub[u'\x0a'] = '\n'
a= u'\x0a'
char_list = []
char_list.append('\n')
char_list.append(' ')
char_list.append(',')
char_list.append('.')
char_list.append('”')
char_list.append('"')
char_list.append('[')
char_list.append(']')
char_list.append('(')
char_list.append(')')
char_list.append('{')
char_list.append('}')

char_escape = {}
char_escape['_'] = '&#95;'

headings = {}
headings['TITLE'] = '# '
headings['HEADING_1'] = '## '
headings['HEADING_2'] = '### '
headings['HEADING_3'] = '#### '
headings['HEADING_4'] = '##### '
headings['HEADING_5'] = '###### '
headings['HEADING_6'] = '####### '

wrong_words = {}
wrong_words['venice'] = "Policies and Services Manager"
wrong_words['naples'] = "Distributed Services Card"
wrong_words['dsp'] = "** Remove, we dont use DSP as abrivation **"
wrong_words['\nwe '] = "Distributed Services Card"
wrong_words[' we '] = "Distributed Services Card"
wrong_words['\ni '] = "** Rewite Sentence, to remove I **"
wrong_words[' i '] = "** Rewite Sentence, to remove I **"


namedStyleType = {}
namedStyleType['NORMAL_TEXT'] = ''
namedStyleType['SUBTITLE'] = ''
for key, value in headings.items():
    namedStyleType[key] = value

textStyle = {}
textStyle['bold'] = {'Begin': '**', 'End': '**'}
textStyle['italic'] = {'Begin': '*', 'End': '*'}
textStyle['code'] = {'Begin': '`', 'End': '`'}
textStyle['underline'] = {'Begin': '<ins>', 'End': '</ins>'}
textStyle['fenced'] = {'Begin': '\n\n```\n', 'End': '\n```\n'}
textStyle['strikethrough'] = {'Begin': '~~', 'End': '~~'}


css_def = (
    '<style>\n'
    '   .p-table th {\n'
    '       align: center;\n'
    '       border: 1px solid #ccc;\n'
    '       text-align: center;\n'
    '       background: #44546A;\n'
    '       border-color: white;\n'
    '       font-weight: bold;\n'
    '       color: white;\n'
    '   }\n'
    '\n'
    '   .p-table table {\n'
    '       margin-left:auto;\n'
    '       margin-right:auto;\n'
    '   }\n'
    '\n'
    '   .p-table td {\n'
    '       border: 1px solid #ccc;\n'
    '       text-align: left;\n'
    '       border-left: none;\n'
    '       border-right: none;\n'
    '   }\n'
    '</style>\n'
)

def get_doc_meta(documentid):
    global doc_meta_dir

    meta = False

    filename = doc_meta_dir + "/" + documentid + ".meta"

    if os.path.isfile(filename):
        verbose_print("Found and importing meta file: %s" % filename)
        with open(filename, "r") as read_file:
            meta = json.load(read_file)
    
    return meta

def clean_string(text):
    text = text.replace('\n', '<NL>')
    text = text.replace('\t', '<TA>')
    return text

def normalize_string(old_text, new_content):
    result = (old_text + new_content)[-40:]
    return result

def verbose_print(text, dedupe=True):
    global vp, text_cache

    if vp and (text_cache != text or dedupe == False):
        text_cache = text
        print(text)
        return True

    return False

def look4words(text_local, font):
    global words_list

    local_flag = False

    if font != None and 'Courier New' in font:
        verbose_print("Found Courier New, skipping word check...")
        return False
    for key, value in wrong_words.items():
        if key in text_local.lower():
            words_list.append("(Incorrect word found: '" + key + "') : 'Suggestion: '" + value + "'")
            local_flag = True
    return local_flag

def add_syntax_exlusion(parser_name, cmds):
  global syntax_exlude_map

  if not parser_name in syntax_exlude_map:
    syntax_exlude_map[parser_name] = cmds.split(":")
  else:
    print("Syntax error, add_exlusion function was called multiple times with same name, check your python code", file=sys.stderr)
    exit (1)
  return True

def add_syntax_inclusion(parser_name, cmds):
  global syntax_incusive_map

  if not parser_name in syntax_incusive_map:
    cmds = cmds.replace("-", "_")
    syntax_incusive_map[parser_name] = cmds.split(":")
  else:
    print("Syntax error, add inclusion function was called multiple times with same name, check your python code", file=sys.stderr)
    exit (1)
  return True

def check_syntax(cmds):
  global parser
  cmd_list = vars(cmds)
  stop_flag = False

  message=""
  #pprint(cmds)
  if cmds.command and cmds.command in syntax_exlude_map:
    for a in syntax_exlude_map[args.command]:
      count=[]
      for b in a.split(','):
        command = b.strip()
        if command in cmd_list and cmd_list[command] is not None and cmd_list[command] is not False:
          count.append("--" + command)
      if len(count) > 1:
        parser.print_help()
        print("\nSyntax error:\nMutually exlusive argument received for the positional argument: '" + args.command + "'\n" + "\n".join(count) + "\n", file=sys.stderr)
        stop_flag = True

  stop_flag2 = True
  found_one=False
  if cmds.command and cmds.command in syntax_incusive_map:
    for a in syntax_incusive_map[args.command]:
      count=[]
      for b in a.split(','):
        command=b.strip()
        if command in cmd_list and cmd_list[command] is not None and cmd_list[command] is not False:
          count.append("--" + command)
          found_one=True

      if len(count) > 0 and len(count) == len(a.split(',')):
        stop_flag2 = False


      if len(count) > 0 and len(count) < len(a.split(',')):
        if stop_flag != True:
          message = message + "\nSyntax error:\n"

        message = message + "\nMutually inclusive argument missing for the positional argument: '" + args.command + "'\n"
        for b in a.split(','):
          message = message + "--" + b.strip().replace("_", "-") + "\n"


  if stop_flag == True:
    if len(message) > 0:
      print(message, file=sys.stderr)
    exit(1)

  if found_one == True and stop_flag2 == True:
    parser.print_help()
    print(message, file=sys.stderr)
    exit(1)
  else:
    return True


def populate_footnotes(doc_footnotes):
    global footnotes

    if doc_footnotes is None:
        return False

    for key, item in doc_footnotes.items():
        if 'content' in item:
            footnotes[key] = item['content']

    return True

def populate_lists(doc_list):
    global lists

    if doc_list is None:
        return False

    for key, item in doc_list.items():
        if 'listProperties' in item:
            if 'nestingLevels' in item['listProperties']:
                if len(item['listProperties']['nestingLevels']) > 0:
                    list_item = item['listProperties']['nestingLevels'][0]
                    if 'glyphSymbol' in list_item:
                        lists[key] = "bullet_list"    
                    
                    elif 'glyphType' in list_item and list_item['glyphType'] == "DECIMAL":
                        lists[key] = "number_list"

                    elif 'glyphType' in list_item and list_item['glyphType'] == "ALPHA":
                        lists[key] = "alpha_list"
    return True

def save_object_file(filename, object):
    with open(filename, 'wb') as handle:
        pickle.dump(object, handle)
    return True

def read_object_file(filename):
    with open(filename, 'rb') as handle:
        return pickle.loads(handle.read())

def add_end(text, add_text):
    idx = find_rindent(text)
    if idx:
        text = text[:idx] + add_text + text[idx:]
    else:
        text += add_text
    return text

def add_front(text, add_text):
    idx = 0
    if text == '':
        text += add_text
        return text

    while idx < len(text) and (text[idx] == ' ' or text[idx] == '\n'):
        idx += 1

    if idx > 0:
        text = text[:idx] + add_text + text[idx:]
    else:
        text = add_text + text
    return text

def dump_md(text):
    with open("result/test.md", 'w') as f:
        f.write(text)
    f.close()

def imgage2string(image):
    img = image.convert("L")
    pixel_data = ''.join(map(str,list(img.getdata())))
    return pixel_data

def sha1(data):
    result = hashlib.sha1(data.encode()).hexdigest()
    return result

def masage_image(filename):
    global image_stats, final_dir_bm, scan

    image_stats['drawing'] += 1

    img = Image.open(filename)
    sha1_value = sha1(imgage2string(img))
    name = sha1_value + "." + img.format.lower()
    if scan == False:
        img.save(final_dir_bm + "/" + name)
    return name

def download_image(url):
    global image_stats, final_dir_bm, scan

    image_stats['bitmap'] += 1

    response = requests.get(url, timeout=8.0)
    if response.status_code != requests.codes.ok:
        time.sleep(5)
        response = requests.get(url, timeout=8.0)
        if response.status_code != requests.codes.ok:
            assert False, 'Status code error: {}.'.format(response.status_code)
    
    img = Image.open(BytesIO(response.content))
    sha1_value = sha1(imgage2string(img))
    name = sha1_value + "." + img.format.lower()
    if scan == False:
        img.save(final_dir_bm + "/" + name)
    return name

def dump_stats():
    global fonts_stats, image_stats, fonts_family_stats, SUGGEST_MODE, figure_list

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    line = '*' * 150

    verbose_print("\n%s" % line)
    verbose_print("*")
    verbose_print("*  Document Title: %s" % DOCUMENT_TITLE)
    verbose_print("*  Document ID: %s" % DOCUMENT_ID)
    verbose_print("*  Document URL: %s" % DOCUMENT_URL)
    verbose_print("*  Suggestions: %s" % SUGGEST_MODE)
    verbose_print("*  Date and Time: %s" % dt_string)
    verbose_print("*")
    verbose_print("%s" % line)

    verbose_print("\nFonts Statistics:")
    verbose_print("-----------------")
    for key in sorted(fonts_family_stats.keys()):
        if 'Arial' in key or 'Courier New' in key:
            verbose_print("Font: %s : %s" % (key, fonts_family_stats[key]))
        else:
            verbose_print("Font: %s" % key)
            count = 0
            for item in fonts_family_stats[key]:
                count += 1
                print("      %s. %s" % (count, clean_string(item)))

    verbose_print("\nFonts Changes:")
    verbose_print("--------------")
    count = 0
    for item in fonts_word:
        cleaned_string = clean_string(item)
        if not cleaned_string.endswith("<Arial>:'"):
            count += 1
            print("      %s. %s" % (count, clean_string(item)))

    verbose_print("\nFonts Size Changes:")
    verbose_print("-------------------")
    count = 0
    for item in fonts_size_word:
        count += 1
        verbose_print("      %s. %s" % (count, clean_string(item)))    

    verbose_print("\nIncorrect words found:")
    verbose_print("----------------------")
    count = 0
    for item in words_list:
        count += 1
        verbose_print("      %s. %s" % (count, clean_string(item))) 

    verbose_print("\nFonts Size Statistics:")
    verbose_print("----------------------")
    for key, value in sorted (fonts_stats.items(), key=lambda item: float(item[0])) :  
        verbose_print("Size: %4s : %s" % (round(float(key), 2), value))

    total_images = image_stats['drawing'] + image_stats['bitmap']
    verbose_print("\nImage Statistics:")
    verbose_print("-----------------")    
    verbose_print("# of Bitmap Objects: %s" % image_stats['bitmap'])
    verbose_print("# of Drawings Objects: %s" % image_stats['drawing'])
    verbose_print("# of Total images: %s" % total_images)


    verbose_print("\nfiguresGroup Meta Filtering:")
    verbose_print("----------------------------")

    image_adjust = 0
    if 'figuresGroup' in doc_meta:
        for key,value in doc_meta['figuresGroup'].items():
            if value > 1:
                image_adjust += (value - 1)
                verbose_print("Figure: %s is expected to have: %s Figures." % (key, value))
        
    # Exclude Pensando Logo, it is expected...
    if total_images > 0:
        image_adjust += 1

    duplicates = getDuplicatesWithCount(figure_list)
    verbose_print("\nFigure Counter Statistics:")
    verbose_print("--------------------------")
    verbose_print("\n    Duplicated Figure References: %s" % (len(duplicates)))

    count = 0
    dup_number_2many = 0
    dup_number_2few = 0
    for key, value in duplicates.items():
        if 'figuresGroup' in doc_meta:
            if not key in doc_meta['figuresGroup']: 
                if value > 1:
                    count +=1
                    verbose_print("        %s. Figure: %s # To Many Occurrences, Expected: 1 Found: %s" % (count, key, value))
                    dup_number_2few += (value - 1)
            else:
                expected_value = doc_meta['figuresGroup'][key]
                if expected_value != value:
                    if expected_value < value:
                        count +=1
                        verbose_print("        %s. Figure: %s # To Many Occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
                        dup_number_2many += (value - expected_value)
                    else:
                        count +=1
                        verbose_print("        %s. Figure: %s # To Few Occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
                        dup_number_2few += (expected_value - value)
                else:
                    count +=1
                    verbose_print("        %s. Figure: %s # of occurrences: %s - Correct" % (count, key, value))


    verbose_print("\n    Missing Figure references: %s" % (total_images - image_adjust - (len(figure_list) - dup_number_2many) + dup_number_2few))
    count = 0
    for x in range(1,total_images - image_adjust):
        if not str(x) in figure_list:
            count +=1
            verbose_print("        %s. Expected 'Figure: %s.'" % (count, x))

    figure_order = True
    image_prev = 0

    for x in range(0,len(figure_list)):
        figure_value = int(figure_list[x])        
        if figure_value >= image_prev:
            image_prev = figure_value
        else:
            figure_order = False

    verbose_print("\n    Figures are numbered in sequence (Independent of missing or duplicate Figures): %s" % figure_order)


    verbose_print("\n%s" % line)

def getDuplicatesWithCount(listOfElems):
    ''' Get frequency count of duplicate elements in the given list '''
    dictOfElems = dict()
    # Iterate over each element in list
    for elem in listOfElems:
        # If element exists in dict then increment its value else add it in dict
        if elem in dictOfElems:
            dictOfElems[elem] += 1
        else:
            dictOfElems[elem] = 1    
 
    # Filter key-value pairs in dictionary. Keep pairs whose value is greater than 1 i.e. only duplicate elements from list.
    dictOfElems = { key:value for key, value in dictOfElems.items() if value > 1}
    # Returns a dict of duplicate elements and thier frequency count
    return dictOfElems

def font_size_converter(font_size):
    global fonts_stats

    fsize = str(font_size)

    if not fsize in fonts_stats:
        fonts_stats[fsize] =0

    fonts_stats[fsize] += 1

    if font_size < 11:
        font_size=1

    if font_size >= 11 and font_size < 24:
        font_size=2

    if font_size >= 24 and font_size < 37:
        font_size=3

    if font_size >= 37 and font_size < 50:
        font_size=4

    if font_size >= 50 and font_size < 63:
        font_size=5

    if font_size >= 63 and font_size < 76:
        font_size=6
    
    if font_size >= 76:
        font_size=7

    return font_size

def find_lindent(text_local):
    if text_local == '':
        return False
    idx = 0
    while idx < len(text_local) and text_local[idx] == ' ':
        idx += 1
    if text_local[0] != ' ':
        return False
    return idx

def count_crlf_end(text_local):
    if text_local == '':
        return 0
    count = 0
    idx = 0
    while idx >= 0:
        idx = len(text_local) -1
        if text_local[-1:] == ' ':
            text_local = text_local[:-1]
        elif text_local[-1:] == '\n':
            count += 1
            text_local = text_local[:-1]
        else:
             idx = -1
    return count

def find_rindent(text_local):
    if text_local == '':
        return False
    end_char = text_local[-1]
    if len(text_local) == 0 or (end_char != ' ' and end_char != '\n'):
        return False
    idx = len(text_local) -1
    while idx >= 0 and (text_local[idx] == ' ' or (idx == len(text_local) -1 and text_local[idx] == '\n')):
        idx -= 1

    return idx+1

def check_heading(text_local):
    global headings

    if text_local == '':
        return False
    if text_local.endswith('\n'):
        return False        

    idx = len(text_local) -1
    while idx >= 0 and text_local[idx] != '\n':
        idx -= 1

    if idx == 0:
        return False

    str2process = text_local[idx+1:]

    for key, value in headings.items():
        if str2process.startswith(value):
            return True

    if '![image' in str2process:
        return True

    return False

def parse_fontFamily(textStyle):
    fontFamily = None
    if 'weightedFontFamily' in textStyle and 'fontFamily' in textStyle['weightedFontFamily']:
        fontFamily = textStyle['weightedFontFamily']['fontFamily']
    return fontFamily

def parse_fontsize(textStyle):
    global fonts_stats, bullet_flag

    font_begin = None
    font_end = None
    actual_size = None

    if 'fontSize' in textStyle:
        size = textStyle['fontSize']['magnitude']
        actual_size = size
        size = font_size_converter(size)
        if bullet_flag:
            font_begin = "<font size='" + str(size) + "'>"
        else:
            font_begin = "<font size='" + str(size) + "'>"
        font_end = "\n</font>"
    else:
        fsize = "12"

        if not fsize in fonts_stats:
            fonts_stats[fsize] = 0
        
        fonts_stats[fsize] += 1

    return font_begin, font_end, str(actual_size)

def replace_escape_characters(text_local):
    global escape_char
    for key, value in escape_char.items():
        text_local = text_local.replace(key, value)
    return text_local

def scrub_characters(text_local):
    global char_scrub
    for key, value in char_scrub.items():
        text_local = text_local.replace(key, value)
    return text_local

def escape_characters(text_local):
    global char_escape
    for key, value in char_escape.items():
        text_local = text_local.replace(key, value)
    return text_local

def check_first_char(text_local):
    global char_list

    for item in char_list:
        if text_local[0] == item:
            return False
     
    return True 

def check_last_char(text_local):
    global char_list

    for item in char_list:
        if text_local[-1] == item:
            return False
     
    return True 

def read_paragraph_element(element, tblscsr, current_text, flags, listid):
    global para, textStyle, fenced_flag, code_flag, Dcount, bullet_flag, bullet_count, footnote_flag, footnote_count, fenced_count, nestinglevel, lists, scan, fonts_family_stats, raw_text, fonts_word, font_prev, font_size_prev

    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    empty_header = None
    
    text_local = ''
    list_local = []
    text_run = element.get('textRun')
    text_textStyle = text_run.get('textStyle')
    text_font_begin,text_font_end, text_font_size = parse_fontsize(text_textStyle)
    text_font_family = parse_fontFamily(text_textStyle)
    text_content_raw_read = text_run.get('content')
    text_content_raw = unicodedata.normalize("NFKD",text_content_raw_read)
    text_content_esc = replace_escape_characters(text_content_raw)
    text_content = escape_characters(text_content_esc)

    look4words(text_content_raw, text_font_family)

    if 'Kind or Tag (arbitrary' in text_content_raw:
        print("Stop")

    if font_size_prev != None:
        if font_size_prev != text_font_size and len(raw_text) > 0 and len(text_content) > 0:
            if check_last_char(raw_text) and check_first_char(text_content):
                if text_font_size == "None":
                    text_fs = '12'
                else:
                    text_fs = text_font_size

                if font_size_prev == "None":
                    font_sp = '12'
                else:
                    font_sp = font_size_prev

                words_raw = raw_text.split()
                words_content = text_content.split()

                if len(words_raw) > 0:
                    word_first_part = words_raw[-1]
                else:
                    word_first_part = ''

                if len(words_content) > 0:
                    word_last_part = words_content[0]
                else:
                    word_last_part = ''

                fonts_size_word.append("(Near: '" + raw_text + "') : (Font size changes in word: '" + word_first_part + word_last_part + "') : '<Size: " + font_sp + ">" + word_first_part + "<Size: " + text_fs + ">" + word_last_part + "'")


    if font_size_prev != text_font_size:
        font_size_prev = text_font_size


    if font_prev != None:
        if font_prev != text_font_family and len(raw_text) > 0 and len(text_content) > 0:
            if check_last_char(raw_text) and check_first_char(text_content):
                if text_font_family == None:
                    text_ff = 'Arial'
                else:
                    text_ff = text_font_family

                if font_prev == None:
                    font_p = 'Arial'
                else:
                    font_p = font_prev

                words_raw = raw_text.split()
                words_content = text_content.split()

                if len(words_raw) > 0:
                    word_first_part = words_raw[-1]
                else:
                    word_first_part = ''

                if len(words_content) > 0:
                    word_last_part = words_content[0]
                else:
                    word_last_part = ''

                fonts_word.append("(Near: '" + raw_text + "') : (Font changes in word: '" + word_first_part + word_last_part + "') : '<" + font_p + ">" + word_first_part + "<" + text_ff + ">" + word_last_part + "'")


    if font_prev != text_font_family:
        font_prev = text_font_family

    if text_font_family == None or 'Arial' in text_font_family:
        if 'Arial' in fonts_family_stats:
            fonts_family_stats['Arial'] += 1
        else:
            fonts_family_stats['Arial'] = 1
    else:
        if text_font_family in fonts_family_stats:
            if 'Courier New' in text_font_family:
                fonts_family_stats[text_font_family] += 1
            else:
                fonts_family_stats[text_font_family].append("(Near: '" + raw_text + "') : -->" + clean_string(text_content_raw)[-40:] + "<--")

        else:
            if 'Courier New' in text_font_family:
                fonts_family_stats[text_font_family] = 1
            else:
                fonts_family_stats[text_font_family] = []
                fonts_family_stats[text_font_family].append("(Near: '" + raw_text + "') : -->" + clean_string(text_content_raw)[-40:] + "<--")
    
    raw_text = normalize_string(raw_text, text_content_raw)

    #if 'Please check the Release Notes' in text_content_raw:
    #    verbose_print('Here')

    # Fenced
    if fenced_flag == False and code_flag == False and text_content.isspace() == False and (tblscsr or (text_font_family == "Courier New" and text_content.startswith('#'))):
        text_local += textStyle['fenced']['Begin']
        fenced_flag = True

    if fenced_flag == True and not tblscsr and text_font_family != "Courier New":
        text_local += textStyle['fenced']['End']
        fenced_flag = False

    #Code
    if fenced_flag == False and text_content.isspace() == False and code_flag == False and text_font_family == "Courier New":
        text_local += textStyle['code']['Begin']
        code_flag = True

    if fenced_flag == False and code_flag and text_font_family != "Courier New":
            text_local += textStyle['code']['End']
            code_flag = False

    #Bullets
    text_cache = current_text + text_local
    if fenced_flag == False and text_content.isspace() == False and code_flag == False and bullet_flag == False and 'bullet' in flags and text_cache.endswith('\n'):
        count = count_crlf_end(current_text + text_local)
        if count < 2:
            text_local += '\n' * (2 - count)
        bullet_flag = True

    if fenced_flag == False and code_flag ==False and bullet_flag and not 'bullet' in flags:
        text_local += '  \n'
        bullet_flag = False

    if footnote_flag:
        footnote_count +=1
    else:
        footnote_count = 0

    if bullet_flag:
        bullet_count += 1
    else:
        bullet_count = 0

    if fenced_flag:
        fenced_count += 1
    else:
        fenced_count = 0

    if tblscsr or fenced_flag or code_flag:
        if fenced_count == 1:
            text_local += text_content_raw 
        else:
            text_local = add_end(text_local, text_content_raw)
    else:
        if text_content == ' ':
            if footnote_count == 1:
                footnote_count = 0
                return text_local, empty_header
            else:
                text_local += text_content
            return text_local, empty_header

        #Center
        if para.alignment == "CENTER" and para.alignment_flag == False:
            para.alignment_flag = True
            text_local += '<div style="text-align:center">'

        if bullet_flag and ((current_text + text_local).endswith('\n')):
            list_type = lists[listid]

            if list_type == 'bullet_list':
                text_local += nestinglevel + '- '

            elif list_type == 'number_list' or list_type == 'alpha_list':
                if footnote_flag == True:
                    text_local = add_front(text_local, nestinglevel + '    1. ')
                else:
                    text_local += nestinglevel + '1. '

            else:
                text_local += nestinglevel + '- '

        # Remove empty headers
        if text_content == '\n':
            tocut = 0 
            for key1 ,value1 in headings.items():          
                if current_text.endswith(value1):
                    tmpcut = len(value1)
                    if tmpcut > tocut:
                        tocut=tmpcut
                    
            if tocut > 0:
                empty_header = tocut



        if text_font_begin:
            if footnote_flag == True:
                if text_content == '\n':
                    return text_local, empty_header
                text_local += text_font_begin.strip()
            elif text_local + text_content == '\n':
                return '\n', empty_header
            elif bullet_count == 1:
                text_local += text_font_begin.strip()
            else:
                text_local += text_font_begin

        if not text_run:
            return '', empty_header

        # Add textStyle before text
        if text_content != '\n':
            for key in text_textStyle:
                if text_textStyle[key] == True and key in textStyle:
                    text_local += textStyle[key]['Begin']
                    if bullet_flag:
                        text_local = text_local.rstrip()
                    list_local.append(key)
        
        idx = find_lindent(text_content)
        if idx and len(list_local) > 0:
            text_local = text_content[:idx] + text_local + text_content[idx:]
        elif footnote_count == 1:
            text_local += text_content.lstrip()
        else:
            text_local += text_content

        # Add textStyle after text
        if para.alignment != "CENTER" and para.alignment_flag:
            para.alignment_flag == False
            text_local += '</div>'
        

        for key in reversed(list_local):
            text_local = add_end(text_local, textStyle[key]['End'])
            if bullet_flag:
                text_local = text_local.rstrip()

        #idx = find_rindent(text_local)
        if text_font_end:
            if footnote_count == 1:
                text_local = text_local.rstrip() + text_font_end.strip() + '\n\n'
            elif footnote_count > 1:
                text_local = text_local.rstrip() + text_font_end.strip() + '\n'
            elif bullet_flag:
                text_local = add_end(text_local, text_font_end.strip())
            else:
                text_local = add_end(text_local, text_font_end) + '\n'

        #Add Extra nl if needed
        #if not text_font_begin and text_local.endswith('\n') and not text_local.endswith('  \n') and bullet_flag == False:
        #    idx = find_rindent(text_local)
        #    a = 2 - (len(text_local) - idx - 1)
        #    if a > 0:
        #        text_local = text_local[:idx] + (' ' * a) + text_local[idx:]

    return text_local, empty_header


def read_strucutural_elements(document, elements, current_text, current_footnotes_text, tblscsr):
    global para, namedStyleType, testStyle, Dcount, urls_map, fenced_flag, code_flag, bullet_flag, footnote_flag, nestinglevel,final_dir_bm, image_stats, scan

    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    footnotes_text = ''
    listid = ''
    for value in elements:
        Dcount += 1
        if Dcount == 221:
            verbose_print('*** STOP ***')

        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            paragraph = value.get('paragraph')
            paragraph_style_namedStyleType = paragraph.get('paragraphStyle').get('namedStyleType')
            para.set_alignment (paragraph.get('paragraphStyle').get('alignment'))
            for elem in elements:
                flags=""
                if 'bullet' in paragraph:
                    listid = paragraph['bullet']['listId']
                    flags += "bullet"
                    if 'nestingLevel' in paragraph['bullet']:
                        nlevel = paragraph['bullet']['nestingLevel']
                        nestinglevel = '   ' + ('    ' * nlevel)
                    else:
                        nestinglevel = ''
                text_run = elem.get('textRun')
                if text_run:
                    text_textStyle = text_run.get('textStyle')
                    text_font_family = parse_fontFamily(text_textStyle)
                    text_content_raw = text_run.get('content')

                    if fenced_flag == True and not tblscsr and text_font_family != "Courier New":
                        text += textStyle['fenced']['End']
                        fenced_flag = False
    
                    if fenced_flag == False and code_flag and text_font_family != "Courier New":
                        if bullet_flag:
                            text = add_end(text, textStyle['code']['End'])
                        else:
                            text = add_end(text, textStyle['code']['End'])
                        code_flag = False

                    if fenced_flag == False and code_flag and text_font_family == "Courier New" and text.endswith('\n'):
                        last_code_index = text.rfind(textStyle['code']['Begin'])
                        text = text[:last_code_index] + textStyle['fenced']['Begin'] + text[last_code_index+1:]
                        code_flag = False
                        fenced_flag = True

                    if fenced_flag == False and code_flag ==False and bullet_flag and not 'bullet' in flags:
                        text += '  \n'
                        bullet_flag = False

                    if para.alignment != "CENTER" and para.alignment_flag:
                        para.alignment_flag = False
                        text += '</div>'

                if tblscsr == False and paragraph_style_namedStyleType:
                    text_cache = current_text + text
                    ch = check_heading(text_cache)

                    if 'inlineObjectElement' in elem:
                        text += '  \n'
                    elif paragraph_style_namedStyleType in namedStyleType:
                        if ch == False and text_cache != '' and not text_cache.endswith('\n') and paragraph_style_namedStyleType != "NORMAL_TEXT":
                            text += '\n'
                        if ch == False:
                            text += namedStyleType[paragraph_style_namedStyleType]
                    else:
                        print("Found unsopported namedStyleType", file=sys.stderr)
                        sys.exit(0)

                if tblscsr == False and 'inlineObjectElement' in elem:
                    if 'inlineObjectId' in elem['inlineObjectElement']:
                        inlineObjectId = elem['inlineObjectElement']['inlineObjectId']
                        if 'imageProperties' in document.get('inlineObjects').get(inlineObjectId).get('inlineObjectProperties').get('embeddedObject'):
                            verbose_print('Reading Bitmap inline image')
                            if scan == False:
                                url = document.get('inlineObjects').get(inlineObjectId).get('inlineObjectProperties').get('embeddedObject').get('imageProperties').get('contentUri')
                                name = download_image(url)
                                if not text.endswith('\n'):
                                    text += '\n'
                                text += "![image alt text](" + bitmap_path_md + "/" + name + ")"
                                if 'e97d284661e1' in name:
                                    print("**Stop**)")
                            else:
                                image_stats['bitmap'] += 1
                        else:
                            verbose_print('Reading Drawing inline image')
                            if scan == False:
                                image_file = files_map[inlineObjectId]
                                name = masage_image(image_file)
                                if not text.endswith('\n'):
                                    text += '\n'
                                text += "![image alt text](" + bitmap_path_md + "/" + name + ")"
                            else:
                                image_stats['drawing'] += 1

                elif 'footnoteReference' in elem:
                    verbose_print("Parsing footNote")
                    footnoteReference = elem['footnoteReference']
                    footnoteId = footnoteReference['footnoteId']
                    footnotenoteNumber = footnoteReference['footnoteNumber']
                    text += '[^' + footnoteId + ']'
                    footnote = footnotes[footnoteId]
                    flags += 'footnote'
                    footnote_flag = True
                    text_tmp = read_strucutural_elements(document, footnote, current_text, footnotes_text, False)
                    footnote_flag = False
                    footnotes_text += '[^' + footnoteId + ']: ' + text_tmp.lstrip()
                elif 'pageBreak' in elem:
                    verbose_print("Ignoring pageBreak")
                else:
                    text_tmp, rmtxt = read_paragraph_element(elem, tblscsr, text, flags, listid)
                    if rmtxt == None:
                        text += text_tmp
                    else:
                        verbose_print("Removing Empty Header")
                        text = text[:-rmtxt]
                        text += text_tmp
            
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table_header = True
            table = value.get('table')
            if table['rows'] == 1 and table['columns'] == 1:
                for row in table.get('tableRows'):
                    cells = row.get('tableCells')
                    for cell in cells:
                        cell_content_element = cell.get('content')
                        cell_content = read_strucutural_elements(document, cell_content_element, text, footnotes_text, True)
                        text += cell_content
            else:
                text += '<div class="p-table center"><div></div>\n\n'
                for row in table.get('tableRows'):
                    cells = row.get('tableCells')
                    for cell in cells:
                        cell_content_element = cell.get('content')
                        cell_content = read_strucutural_elements(document, cell_content_element, text, footnotes_text, False)
                        cell_content = cell_content.rstrip()
                        cell_content = cell_content.replace('\n', '<br>')  
                        text += "| " + cell_content + " "

                    text += "|\n"

                    if table_header:
                        table_header = False
                        text += "|"
                        columns = table.get('columns')
                        for x in range(0,columns):
                            text += ' --- |'
                text += '\n</div>\n'

        elif 'tableOfContents' in value:
            verbose_print("Ignoring pageBreak")       
        elif 'sectionBreak' in value:
            verbose_print("Ignoring sectionBreak")
        else:
            verbose_print("Unkown Element Found... Please add to code")

    text += '  \n  \n' + footnotes_text

    return text

def main():
    global current_dir, final_dir_md, final_dir_bm, doc_lists, headless, files_map, urls_map, download_dir, bitmap_path_md, vp, scan, DOCUMENT_ID, DOCUMENT_TITLE, DOCUMENT_URL, SUGGEST_MODE, figure_list, doc_meta, doc_meta_dir

    if 'accept_suggestions' in args and args.accept_suggestions:
        SUGGEST_MODE="PREVIEW_SUGGESTIONS_ACCEPTED"

    if 'verbose' in args:
        vp = args.verbose

    if args.command == "headless":
        headless = True
    elif args.command == "headful":
        headless = False
    elif args.command == "scan":
        scan = True
        vp = True
    else:
        headless = False

    if not os.path.exists(download_dir) and scan == False:
        verbose_print("Creating %s folder for Chromium downloads (fixed location)" % download_dir)
        os.makedirs(download_dir)

    DOCUMENT_ID = args.id[0]
    DOCUMENT_URL = "https://docs.google.com/document/d/" + DOCUMENT_ID

    if args.command == "headless" or args.command == "headful":
        final_dir_bm = args.bitmap_destination[0].rstrip('/')
        final_dir_md = args.doc_destination[0].rstrip('/')
        
        if 'relative_path' in args and args.relative_path != None:
            bitmap_path_md = args.relative_path[0].rstrip('/')
        else:
            bitmap_path_md = final_dir_md

    if scan == False and args.cache_enable == False:
        files_map, urls_map = parse_gdoc.parseDocument(DOCUMENT_URL, username, pwdfile, download_dir, headless, vp)
        if args.write_cache:
            save_object_file(current_dir + "/" + DOCUMENT_ID + "_files_map.picl", files_map)
            save_object_file(current_dir + "/" + DOCUMENT_ID + "_urls_map.picl", urls_map)

    if scan == False and args.cache_enable:
        files_map = read_object_file(current_dir + "/" + DOCUMENT_ID + "_files_map.picl")
        urls_map = read_object_file(current_dir + "/" + DOCUMENT_ID + "_urls_map.picl")
        for key, value in files_map.items():
            verbose_print("files_map['%s'] = '%s'" % (key, value))
        for key, value in urls_map.items():
            verbose_print("urls_map['%s'] = '%s'" % (key, value))

    if 'meta_ignore' in args and args.meta_ignore == False:
        doc_meta_result = get_doc_meta(DOCUMENT_ID)
        if doc_meta_result != False:
            doc_meta = doc_meta_result

    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
 
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

    creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        #with open('token.pickle', 'wb') as token:
        #    pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID, suggestionsViewMode=SUGGEST_MODE).execute()

    DOCUMENT_TITLE = document.get('title')
    doc_title_name = final_dir_md + "/" + DOCUMENT_TITLE.replace(' ', '_') + ".md"

    verbose_print('Processing document: {}'.format(document.get('title')))

    doc_content = document.get('body').get('content')
    doc_lists = document.get('lists')
    #doc_footers = document.get('footers')
    doc_footnotes = document.get('footnotes')

    #print(json.dumps(document, indent=4, sort_keys=True))
    #print(json.dumps(doc_footnotes, indent=4, sort_keys=True))

    populate_lists(doc_lists)
    populate_footnotes(doc_footnotes)

    md = read_strucutural_elements(document, doc_content, '', '', False)

    md = css_def + md

    if scan == False:
        with open(doc_title_name, 'w', encoding='utf-8') as f:
            f.write(md)
        f.close()

        verbose_print("Final MD file: %s" % doc_title_name)

    # Post Parsing
    regex = r"(?<=[^\*\*]\*Figure\s)\d{1,3}(?=\.)"
    figure_list = re.findall(regex, md, re.MULTILINE)
    dump_stats()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Pensando Goole Document to MD Document converter tool: 1.0 (2020)", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(help='Available Commands:')
    subparsers.dest = 'command'
  
    # create the parser for the "headless" command
    parser_name="headless"
    parser_a = subparsers.add_parser(parser_name, help='Converts a Google doc to MD format with headless browser')
    parser_a.add_argument('-a', '--accept_suggestions', action='store_true', help='Reads the document as if all suggestions where accepted, if not set suggestions are ignored.')
    parser_a.add_argument('-b', '--bitmap_destination', required=True, nargs=1, help='<Destination folder for bitmap images>', metavar="")
    parser_a.add_argument('-c', '--cache_enable', action='store_true', help='Use cache files created by -w flag')
    parser_a.add_argument('-d', '--doc_destination',required=True, nargs=1, help='<Destination folder for MD document>', metavar="")
    parser_a.add_argument('-i', '--id', required=True, nargs=1, help='Google Doc ID', metavar="")
    parser_a.add_argument('-m', '--meta_ignore', action='store_true', help='Ignores any metafile associated with this doc.')
    parser_a.add_argument('-r', '--relative_path', nargs=1, help='Relative path to images, used in md file, if obitted bitmap_destination is used', metavar="")
    parser_a.add_argument('-v', '--verbose', action='store_true', help='Verbose text and with Screenshots')
    parser_a.add_argument('-w', '--write_cache', action='store_true', help='Stores the map liks to current dir, after successful run, needed by -c flag')
    add_syntax_inclusion(parser_name, "id,bitmap_destination, doc_destination")
    add_syntax_exlusion(parser_name, "cache_enable, write_cache")

    parser_name="headful"
    parser_b = subparsers.add_parser(parser_name, help='Converts a Google doc to MD format with browser visible')
    parser_b.add_argument('-a', '--accept_suggestions', action='store_true', help='Reads the document as if all suggestions where accepted, if not set suggestions are ignored.')
    parser_b.add_argument('-b', '--bitmap_destination', required=True, nargs=1, help='<Destination folder for bitmap images>', metavar="")
    parser_b.add_argument('-c', '--cache_enable', action='store_true', help='Use cache files created by -w flag')
    parser_b.add_argument('-d', '--doc_destination',required=True, nargs=1, help='<Destination folder for MD document>', metavar="")
    parser_b.add_argument('-i', '--id',required=True, nargs=1, help='Google Doc ID', metavar="")
    parser_b.add_argument('-m', '--meta_ignore', action='store_true', help='Ignores any metafile associated with this doc.')
    parser_b.add_argument('-r', '--relative_path', nargs=1, help='Relative path to images, used in md file, if obitted bitmap_destination is used', metavar="")
    parser_b.add_argument('-v', '--verbose', action='store_true', help='Verbose text')
    parser_b.add_argument('-w', '--write_cache', action='store_true', help='Stores the map liks to current dir, after successful run, needed by -c flag')
    add_syntax_inclusion(parser_name, "id,bitmap_destination, doc_destination")
    add_syntax_exlusion(parser_name, "cache_enable, write_cache")


    parser_name="scan"
    parser_c = subparsers.add_parser(parser_name, help='Scans a Google Doc and reports stats')
    parser_c.add_argument('-a', '--accept_suggestions', action='store_true', help='Reads the document as if all suggestions where accepted, if not set suggestions are ignored.')
    parser_c.add_argument('-m', '--meta_ignore', action='store_true', help='Ignores any metafile associated with this doc.')
    parser_c.add_argument('-i', '--id', required=True, nargs=1, help='Google Doc ID', metavar="")
    add_syntax_inclusion(parser_name, "id")

    if len(sys.argv)==1:
      parser.print_help()
      exit(0)

    args = parser.parse_args()

    check_syntax(args)

    main()
