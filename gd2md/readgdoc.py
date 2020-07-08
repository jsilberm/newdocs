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

md_doc_global = ''

username = "release@pensando.io"


home_dir = os.environ['HOME']
pwdfile = home_dir + "/.gdocs"
download_dir = home_dir + "/Downloads"
current_dir = os.getcwd()
doc_meta_dir = current_dir + '/meta4docs'

final_dir_bm = ""
final_dir_md = ""
bitmap_path_md = ""
site = None
vp = False
report = False
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
words_list_text = []
figure_list = []
table_list =[]
spaces_list = []
nl_list = []
issues_headers = {}

table_counter = 0

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
wrong_words = {}

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

def fix_illigal_headers(local_text, local_illigal_headers):
    
    local_text = local_text.lstrip()
    for value in local_illigal_headers:
        if '</div>\n' in value:
            local_text = local_text.replace(value, '</div>\n\n')
        else:
            local_text = local_text.replace(value, '\n\n')

    return local_text

def get_illigal_headers(local_text, title, searchtext):
    global issues_headers

    new_dict = {}
    issues_headers[title] = {'illigal_text': '', 'pre_illigal_text': ''}

    regex = r"(#+\s*(\W|</div>)\n)"
    illigal_text = [m[0] for m in re.findall(regex, local_text)]
    issues_headers[title]['illigal_text'] = illigal_text
    illigal_pos = [m.start() for m in re.finditer(regex, local_text)]

    pretext_offset = len(searchtext)
    local_text_tmp = searchtext + local_text
    before_text_tmp = []
    before_txt = []
    for pos in illigal_pos:
        before_text_tmp.append(local_text_tmp[max(pretext_offset + pos-60,0):pretext_offset + pos])
        text_tmp = local_text[max(pos-60,0):pos]
        before_txt.append(text_tmp)

    issues_headers[title]['pre_illigal_text'] = before_text_tmp
    new_dict = dict(zip(illigal_text,before_txt))

    return new_dict

def change_filename_characters(local_text):

    local_text = local_text.replace(' ', '_')
    local_text = local_text.replace(':','-')
    local_text = local_text.replace('/','-')
    local_text = local_text.replace('\\','-')
    local_text = local_text.replace('*','-')
    local_text = local_text.replace('?','-')
    local_text = local_text.replace('<','(')
    local_text = local_text.replace('>',')')
    local_text = local_text.replace('[','(')
    local_text = local_text.replace(']',')')
    local_text = local_text.replace('{','(')
    local_text = local_text.replace('}',')')
    local_text = local_text.replace('|','-')
    local_text = local_text.replace('"',"'")
    local_text = local_text.replace('&',"and")
    local_text = local_text.replace('%',"-")
    local_text = local_text.replace('$',"-")
    local_text = local_text.replace('~',"-")
    local_text = local_text.replace('+',"-")
    local_text = local_text.replace('=',"-")
    local_text = local_text.replace(';',"-")
    local_text = local_text.replace('`',"-")
    local_text = local_text.replace('^',"-")

    while '__' in local_text:
        local_text = local_text.replace('__','_')

    while '--' in local_text:
        local_text = local_text.replace('--','-')

    return local_text

def get_hugo_header(header_title, categories, weight, doc_title):

    header_title = header_title.replace('_', ' ')   
    while '  ' in header_title:
        header_title = header_title.replace('  ',' ')

    doc_title = doc_title.replace('_', ' ')   
    while '  ' in doc_title:
        doc_title = doc_title.replace('  ',' ')

    header = '---\n'
    header += 'title: "' + header_title + '"\n'
    header += 'menu:\n'
    if not doc_title == '':
        header += '  docs:\n'
        header += '    parent: "' + doc_title + '"\n'
    else:
        header += '  main:\n'
    header += 'weight: ' + str(weight + 1) + '\n'
    if categories != '':
        header += 'categories: ' + categories + '\n'
    header += 'toc: true\n'
    header += '---\n'

    return header, header_title

def clean_md_dict(md_dict):
    global headings, doc_meta, DOCUMENT_TITLE


    md_dict = handle_bad_headers(md_dict)

    new_dict = {}
    count = 0
    local_text = ""
    pointer="MAIN"
    categories = ''
    doc_title = DOCUMENT_TITLE

    new_dict[pointer] = {'table': False, 'name': '','doc_title': '','categoris': '', 'title': '', 'text': '', 'hugo_header': '', 'images': {}}


    for key, value in md_dict.items():
        if not '_table' in key:
            value = value.strip() + '\n'

            if value.startswith(headings['HEADING_1']):
                new_dict[pointer]['text'] = local_text

                if 'categories' in doc_meta and doc_meta['categories'] != '':
                    categories = doc_meta['categories']

                if 'parent' in doc_meta and doc_meta['parent'] != '':
                    doc_title = doc_meta['parent']
                
                if 'MAIN' == pointer:
                    new_dict[pointer]['name'] = 'Main'
                    new_dict[pointer]['doc_title'] = doc_title
                    new_dict[pointer]['categoris'] = categories
                    new_dict[pointer]['hugo_header'], new_dict[pointer]['title'] = get_hugo_header('Main', categories, count, doc_title)

                    regex = r"(?<=\!\[image alt text\]\().+?(?=\))"
                    header_list = re.findall(regex, local_text, re.MULTILINE)
                    if len(header_list) > 0:
                        new_dict[pointer]['images'] = header_list                    
                else:
                    regex = r"(?<=[#]{2}\s).+?(?=\n)"
                    header_list = re.findall(regex, local_text, re.MULTILINE)
                    if len(header_list) == 0:
                        print("Error: Post Processing, could not locate header.", file=sys.stderr)
                        exit (1)

                    new_dict[pointer]['name'] = change_filename_characters(header_list[0])
                    new_dict[pointer]['doc_title'] = doc_title
                    new_dict[pointer]['categoris'] = categories         
                    new_dict[pointer]['hugo_header'], new_dict[pointer]['title'] = get_hugo_header(header_list[0], categories, count, doc_title)

                    regex = r"(?<=\!\[image alt text\]\().+?(?=\))"
                    header_list = re.findall(regex, local_text, re.MULTILINE)
                    if len(header_list) > 0:
                        new_dict[pointer]['images'] = header_list


                count += 1
                pointer = '_index_' + str(count)
                new_dict[pointer] = {'table': False, 'name': '','doc_title': '','categoris': '', 'title': '', 'text': '', 'hugo_header': '', 'images': {}}

                local_text = value
            else:
                local_text += value
        else:

            if value:
                new_dict[pointer]['table'] = value
    
    new_dict[pointer]['text'] = local_text
    regex = r"(?<=[#]{2}\s).+?(?=\n)"
    header_list = re.findall(regex, local_text, re.MULTILINE)
    if len(header_list) == 0:
        print("Error: Post Processing, could not locate header.", file=sys.stderr)
        exit (1)

    new_dict[pointer]['name'] = change_filename_characters(header_list[0])
    new_dict[pointer]['doc_title'] = doc_title
    new_dict[pointer]['categoris'] = categories

    if 'categories' in doc_meta and doc_meta['categories'] != '':
        categories = doc_meta['categories']

    new_dict[pointer]['hugo_header'], new_dict[pointer]['title'] = get_hugo_header(header_list[0], categories, count, doc_title)


    regex = r"(?<=\!\[image alt text\]\().+?(?=\))"
    header_list = re.findall(regex, local_text, re.MULTILINE)
    if len(header_list) > 0:
        new_dict[pointer]['images'] = header_list

    return new_dict

def handle_bad_headers(local_dict):

    new_dict = {}
    prev_key = ''
    searchtext = ''
    for key, value in local_dict.items():
        if not '_table' in key:
            searchtext += value
            illigal_headers = get_illigal_headers(value, key, searchtext)
            if len(illigal_headers) > 0 or value.startswith('\n'):
                value = fix_illigal_headers(value, illigal_headers)
                if not prev_key == '':
                    new_dict[prev_key] += value
                    new_dict[prev_key + '_table'] = new_dict[prev_key + '_table'] | local_dict[key + '_table']
                else:
                    new_dict[key] = value
                    prev_key = key
            else:
                new_dict[key] = value
                prev_key = key
        else:
            if not 'MAIN' in key:
                tmp_list = key.split('_')
                if '_index_' + tmp_list[2] in new_dict:
                    new_dict[key] = value
            else:
                new_dict[key] = value
    
    fix_issues_headers(new_dict)

    return compact_dict(new_dict)

def fix_issues_headers(local_dict):
    global issues_headers

    issues_headers_tmp = {}

    local_pointer = "MAIN"
    for key, value in issues_headers.items():
        if key in local_dict:
            local_pointer = key
            issues_headers_tmp[local_pointer] = issues_headers[local_pointer]
        else:
            issues_headers_tmp[local_pointer]['illigal_text'].extend(issues_headers[key]['illigal_text'])
            issues_headers_tmp[local_pointer]['pre_illigal_text'].extend(issues_headers[key]['pre_illigal_text'])

    issues_headers = issues_headers_tmp

    return True

def compact_dict(local_dict):
    global issues_headers

    issues_headers_tmp = {}
    new_dict = {}
    index_counter = 0 
    for key, value in local_dict.items():
        if 'MAIN' in key:
            new_dict[key] = value

            if not '_table' in key:
                issues_headers_tmp[key] = issues_headers[key]
        else:
            if not '_table' in key:
                index_counter +=1
                new_dict['_index_' + str(index_counter)] = value
                issues_headers_tmp['_index_' + str(index_counter)] = issues_headers[key]
            else:
                new_dict['_index_' + str(index_counter) + '_table'] = value

    issues_headers = issues_headers_tmp

    return new_dict

def get_json_file(location, filename_only):
    global wrong_words

    content = None

    filename = location + "/" + filename_only

    if os.path.isfile(filename):
        verbose_print("Using config file: %s" % filename)
        with open(filename, "r") as read_file:
            content = json.load(read_file)
    else:
        print("Error: Could not locate config file: %s" % filename, file=sys.stderr)
        exit (1)
    

    return content

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
    global vp, report, text_cache

    if (vp or report) and (text_cache != text or dedupe == False):
        text_cache = text
        print(text)
        return True

    return False

def scan4words(text_local):
    global words_list_text

    local_flag = False

    if not 'badwords' in wrong_words:
        print("Error: could not find the Bad Word Dict, exiting", file=sys.stderr)
        exit (1)

    if not 'badwordsok' in wrong_words:
        print("Error: could not find the Bad Word OK Dict, exiting", file=sys.stderr)
        exit (1)

    if not 'badwordscase' in wrong_words:
        print("Error: could not find the Bad Case Dict, exiting", file=sys.stderr)
        exit (1)

    for key, value in wrong_words['badwords'].items():
        count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(key), text_local.lower()))
        if count > 0:
            bad_flag = True
            for keyok, valueok in wrong_words['badwordsok'].items():
                if keyok in text_local.lower():
                    bad_flag = False
                    break
            if bad_flag:    
                words_list_text.append("Incorrect word found: '" + key + "' : Occurences: " + str(count) + " : Suggestion: '" + value + "'")
                local_flag = True

    for key, value in wrong_words['badwordscase'].items():
        count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(key), text_local))
        if count > 0:
            bad_flag = True
            for keyok, valueok in wrong_words['badwordsok'].items():
                if keyok in text_local.lower():
                    bad_flag = False
                    break
            if bad_flag:    
                words_list_text.append("Incorrect word found: '" + key + "' : Occurences: " + str(count) + " : Suggestion: '" + value + "'")
                local_flag = True

    return local_flag


def look4words(text_local, font):
    global words_list

    local_flag = False

    if font != None and 'Courier New' in font:
        verbose_print("Found Courier New, skipping word check...")
        return False

    if not 'badwords' in wrong_words:
        print("Error: could not find the Bad Word Dict, exiting", file=sys.stderr)
        exit (1)

    if not 'badwordsok' in wrong_words:
        print("Error: could not find the Bad Word OK Dict, exiting", file=sys.stderr)
        exit (1)

    for key, value in wrong_words['badwords'].items():
        if key in text_local.lower():
            bad_flag = True
            for keyok, valueok in wrong_words['badwordsok'].items():
                if keyok in text_local.lower():
                    bad_flag = False
                    break
            if bad_flag:    
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

def get_image(url, retries, wait):

    count = 0
    while count < retries:
        try:
            response = requests.get(url, timeout=wait)
            response.raise_for_status()
    
        except requests.exceptions.HTTPError as errh:
            verbose_print("Http Error: %s" % str(errh))

        except requests.exceptions.ConnectionError as errc:
            verbose_print("Error Connecting: %s" % str(errc))

        except requests.exceptions.Timeout as errt:
            verbose_print("Timeout Error: %s" % str(errt))

        except requests.exceptions.RequestException as err:
            verbose_print("Something happend on google side, could not get image: %s" % str(err))

        if response.status_code == requests.codes.ok:
            count = retries
        else:
            count += 1
            if count < retries:
                verbose_print("Waiting 5 sec, attempt %s of %s" % (str(count), str(retries)))
                time.sleep(5)
            else:
                print("Error: Giving up on image, exiting...", file=sys.stderr) 
                exit(1)

    return response


def download_image(url):
    global image_stats, final_dir_bm, scan

    image_stats['bitmap'] += 1

    response = get_image(url, 3, 8.0)
    
    img = Image.open(BytesIO(response.content))
    sha1_value = sha1(imgage2string(img))
    name = sha1_value + "." + img.format.lower()
    if scan == False:
        img.save(final_dir_bm + "/" + name)
    return name

def dump_stats():
    global issues_headers, table_counter, vp, report, scan, fonts_stats, image_stats, fonts_family_stats, SUGGEST_MODE, figure_list,table_list, words_list, words_list_text, spaces_list, nl_list

    if vp or scan:
        report = True

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
                verbose_print("      %s. %s" % (count, clean_string(item)))

    verbose_print("\nFonts Changes:")
    verbose_print("--------------")
    count = 0
    for item in fonts_word:
        cleaned_string = clean_string(item)
        if not cleaned_string.endswith("<Arial>:'"):
            count += 1
            verbose_print("      %s. %s" % (count, clean_string(item)))

    verbose_print("\nFonts Size Changes:")
    verbose_print("-------------------")
    count = 0
    for item in fonts_size_word:
        count += 1
        verbose_print("      %s. %s" % (count, clean_string(item)))    

    # verbose_print("\nIncorrect words found:")
    # verbose_print("----------------------")
    # count = 0
    # for item in words_list:
    #    count += 1
    #    verbose_print("      %s. %s" % (count, clean_string(item))) 

    verbose_print("\nIncorrect words found:")
    verbose_print("----------------------")
    count = 0
    for item in words_list_text:
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
    verbose_print("# of Total images (Exluding First page Pensando logo image): %s" % total_images)

    #Dont Count Document History Table as table
    if table_counter > 0:
        table_counter -=1
    verbose_print("\nTable Statistics:")
    verbose_print("-----------------")    
    verbose_print("# of Tables found (Exluding Doc. History table): %s" % table_counter)


    verbose_print("\nfigure and Table Groups Meta Filtering:")
    verbose_print("----------------------------------------")

    image_adjust = 0
    table_adjust = 0
    if 'figuresGroup' in doc_meta:
        for key,value in doc_meta['figuresGroup'].items():
            if value > 1:
                image_adjust += (value - 1)
                verbose_print("Figure: %s is expected to have: %s Figures." % (key, value))

    if 'tablesGroup' in doc_meta:
        for key,value in doc_meta['tablesGroup'].items():
            if value > 1:
                table_adjust += (value - 1)
                verbose_print("Table: %s is expected to have: %s Tables." % (key, value))
              
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
                    verbose_print("        %s. Figure: %s # To Many occurrences, Expected: 1 Found: %s" % (count, key, value))
                    dup_number_2few += (value - 1)
            else:
                expected_value = doc_meta['figuresGroup'][key]
                if expected_value != value:
                    if expected_value < value:
                        count +=1
                        verbose_print("        %s. Figure: %s # To Many occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
                        dup_number_2many += (value - expected_value)
                    else:
                        count +=1
                        verbose_print("        %s. Figure: %s # To Few occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
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

    ######### TABLE #############

    duplicates = getDuplicatesWithCount(table_list)
    verbose_print("\nTable Counter Statistics:")
    verbose_print("--------------------------")
    verbose_print("\n    Duplicated Table References: %s" % (len(duplicates)))

    count = 0
    dup_number_2many = 0
    dup_number_2few = 0
    for key, value in duplicates.items():
        if 'tablesGroup' in doc_meta:
            if not key in doc_meta['tablesGroup']: 
                if value > 1:
                    count +=1
                    verbose_print("        %s. Table: %s # To Many occurrences, Expected: 1 Found: %s" % (count, key, value))
                    dup_number_2few += (value - 1)
            else:
                expected_value = doc_meta['tablesGroup'][key]
                if expected_value != value:
                    if expected_value < value:
                        count +=1
                        verbose_print("        %s. Table: %s # To Many occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
                        dup_number_2many += (value - expected_value)
                    else:
                        count +=1
                        verbose_print("        %s. Table: %s # To Few occurrences, Expected: %s Found: %s" % (count, key, expected_value, value))
                        dup_number_2few += (expected_value - value)
                else:
                    count +=1
                    verbose_print("        %s. Table: %s # of occurrences: %s - Correct" % (count, key, value))


    verbose_print("\n    Missing Table references: %s" % (table_counter - table_adjust - (len(table_list) - dup_number_2many) + dup_number_2few))
    count = 0
    for x in range(1,table_counter - table_adjust):
        if not str(x) in table_list:
            count +=1
            verbose_print("        %s. Expected 'Table: %s.'" % (count, x))

    table_order = True
    table_prev = 0

    for x in range(0,len(table_list)):
        table_value = int(table_list[x])        
        if table_value >= table_prev:
            table_prev = table_value
        else:
            table_order = False

    verbose_print("\n    Tables are numbered in sequence (Independent of missing or duplicate Tables): %s" % table_order)

    duplicates = getOccurenses(spaces_list)
    verbose_print("\nRepetitive Spaces:")
    verbose_print("-------------------")

    count = 0
    for key, value in duplicates.items():
        count +=1
        verbose_print("%s. Repetitive Spaces found: %s occurrences (Expected: 1), Found: %s" % (count, value, key.count(' ')))

    duplicates = getOccurenses(nl_list)
    verbose_print("\nRepetitive NewLine Characters:")
    verbose_print("-------------------------------")

    count = 0
    for key, value in duplicates.items():
        count +=1
        verbose_print("%s. Repetitive NewLine found: %s occurrences (Expected: < 3), Found: %s" % (count, value, len(key)))

    verbose_print("\nEmpty headers:")
    verbose_print("---------------")
    count = 0
    for key, value in issues_headers.items():
        for x in range(len(value['pre_illigal_text'])):
            count += 1
            pre_illigal_text = clean_string(value['pre_illigal_text'][x])
            verbose_print("%s. Near (Ignore MD format) '%s'" % (count, pre_illigal_text))            


    verbose_print("\n%s" % line)

    report = False

    return True

def getOccurenses(listOfElems):
    ''' Get frequency count of duplicate elements in the given list '''
    dictOfElems = dict()
    # Iterate over each element in list
    for elem in listOfElems:
        # If element exists in dict then increment its value else add it in dict
        if elem in dictOfElems:
            dictOfElems[elem] += 1
        else:
            dictOfElems[elem] = 1    

    return dictOfElems

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

    # Obsolited, replaced with scan4words
    # look4words(text_content_raw, text_font_family)

    if 'PSM Enterprise Edition Design Best Practice' in text_content_raw:
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
                return text_local, empty_header, text_content_raw
            else:
                text_local += text_content
            return text_local, empty_header, text_content_raw

        #Center
        if para.alignment == "CENTER" and para.alignment_flag == False:
            para.alignment_flag = True
            text_local += '<div style="text-align:center">'

        if bullet_flag and ((current_text + text_local).endswith('\n')):

            if '\n' in text_local:
                text_local = text_local.rstrip() + '\n'
            else:
                current_text = current_text.rstrip() + '\n'

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
                    return text_local, empty_header, text_content_raw
                text_local += text_font_begin.strip()
            elif text_local + text_content == '\n':
                return '\n', empty_header, text_content_raw
            elif bullet_count == 1:
                text_local += text_font_begin.strip()
            else:
                text_local += text_font_begin

        if not text_run:
            return '', empty_header, text_content_raw

        # Add textStyle before text
        if text_content != '\n':
            for key in text_textStyle:
                if text_textStyle[key] == True and key in textStyle:
                    text_local += textStyle[key]['Begin']
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

    return text_local, empty_header, text_content_raw


def read_strucutural_elements(document, elements, current_text, current_footnotes_text, tblscsr):
    global md_doc_global, table_counter, para, namedStyleType, testStyle, Dcount, urls_map, fenced_flag, code_flag, bullet_flag, footnote_flag, nestinglevel,final_dir_bm, image_stats, scan

    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = {}
    md_index = 0
    md_index_str = 'MAIN'
    md_index_str_table = md_index_str + '_table'
    text[md_index_str] = ''
    text[md_index_str_table] = False
    text_only_doc = ''
    footnotes_text = ''
    listid = ''
    for value in elements:
        Dcount += 1
        #if Dcount == 221:
        #    verbose_print('*** STOP ***')

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
                        text[md_index_str] += textStyle['fenced']['End']
                        fenced_flag = False
    
                    if fenced_flag == False and code_flag and text_font_family != "Courier New":
                        if bullet_flag:
                            text[md_index_str] = add_end(text[md_index_str], textStyle['code']['End'])
                        else:
                            text[md_index_str] = add_end(text[md_index_str], textStyle['code']['End'])
                        code_flag = False

                    if fenced_flag == False and code_flag and text_font_family == "Courier New" and text[md_index_str].endswith('\n'):
                        last_code_index = text[md_index_str].rfind(textStyle['code']['Begin'])
                        text[md_index_str] = text[md_index_str][:last_code_index] + textStyle['fenced']['Begin'] + text[md_index_str][last_code_index+1:]
                        code_flag = False
                        fenced_flag = True

                    if fenced_flag == False and code_flag ==False and bullet_flag and not 'bullet' in flags:
                        text[md_index_str] += '  \n'
                        bullet_flag = False

                    if para.alignment != "CENTER" and para.alignment_flag:
                        para.alignment_flag = False
                        text[md_index_str] += '</div>'

                if tblscsr == False and paragraph_style_namedStyleType:
                    text_cache = current_text + text[md_index_str]
                    ch = check_heading(text_cache)

                    if 'inlineObjectElement' in elem:
                        text[md_index_str] += '  \n'
                    elif paragraph_style_namedStyleType in namedStyleType:
                        if ch == False and text_cache != '' and not text_cache.endswith('\n') and paragraph_style_namedStyleType != "NORMAL_TEXT":
                            text[md_index_str] += '\n'
                        if ch == False:
                            if paragraph_style_namedStyleType == 'HEADING_1':
                                md_index +=1
                                md_doc_global += text[md_index_str]
                                md_index_str = '_index_' + str(md_index)
                                md_index_str_table = md_index_str + '_table'
                                text[md_index_str] = ""
                                text[md_index_str_table] = False

                            text[md_index_str] += namedStyleType[paragraph_style_namedStyleType]
                    else:
                        print("Found unsopported namedStyleType", file=sys.stderr)
                        sys.exit(0)

                if tblscsr == False and 'inlineObjectElement' in elem:
                    if 'inlineObjectId' in elem['inlineObjectElement']:
                        inlineObjectId = elem['inlineObjectElement']['inlineObjectId']
                        if 'imageProperties' in document.get('inlineObjects').get(inlineObjectId).get('inlineObjectProperties').get('embeddedObject'):
                            verbose_print('Reading Bitmap inline image')
                            text_only_doc += '<IMAGE>'
                            if scan == False:
                                url = document.get('inlineObjects').get(inlineObjectId).get('inlineObjectProperties').get('embeddedObject').get('imageProperties').get('contentUri')
                                name = download_image(url)
                                if not text[md_index_str].endswith('\n'):
                                    text[md_index_str] += '\n'
                                text[md_index_str] += "![image alt text](" + bitmap_path_md + "/" + name + ")"
                            else:
                                image_stats['bitmap'] += 1
                        else:
                            verbose_print('Reading Drawing inline image')
                            text_only_doc += '<IMAGE>'                                
                            if scan == False:
                                image_file = files_map[inlineObjectId]
                                name = masage_image(image_file)
                                if not text[md_index_str].endswith('\n'):
                                    text[md_index_str] += '\n'
                                text[md_index_str] += "![image alt text](" + bitmap_path_md + "/" + name + ")"
                            else:
                                image_stats['drawing'] += 1

                elif 'footnoteReference' in elem:
                    verbose_print("Parsing footNote")
                    footnoteReference = elem['footnoteReference']
                    footnoteId = footnoteReference['footnoteId']
                    footnotenoteNumber = footnoteReference['footnoteNumber']
                    text[md_index_str] += '[^' + footnoteId + ']'
                    footnote = footnotes[footnoteId]
                    flags += 'footnote'
                    footnote_flag = True
                    text_tmp, text_only_doc_tmp, _ = read_strucutural_elements(document, footnote, current_text, footnotes_text, False)
                    footnote_flag = False
                    footnotes_text += '[^' + footnoteId + ']: ' + text_tmp.lstrip()
                    text_only_doc += text_only_doc_tmp
                elif 'pageBreak' in elem:
                    verbose_print("Ignoring pageBreak")
                else:
                    text_tmp, rmtxt, text_only_doc_tmp = read_paragraph_element(elem, tblscsr, text[md_index_str], flags, listid)
                    text_only_doc += text_only_doc_tmp
                    if rmtxt == None:
                        text[md_index_str] += text_tmp
                    else:
                        verbose_print("Removing Empty Header")
                        text[md_index_str] = text[md_index_str][:-rmtxt]
                        text[md_index_str] += text_tmp
            
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table_header = True
            table = value.get('table')
            if table['rows'] == 1 and table['columns'] == 1:
                text_only_doc += '<TABLE_1x1_BEGIN>\n'
                for row in table.get('tableRows'):
                    cells = row.get('tableCells')
                    for cell in cells:
                        cell_content_element = cell.get('content')
                        cell_content, text_only_doc_tmp, _ = read_strucutural_elements(document, cell_content_element, text[md_index_str], footnotes_text, True)
                        text[md_index_str] += cell_content
                        text_only_doc += text_only_doc_tmp
                text_only_doc += '<TABLE_1x1_END>\n'    
            else:
                text[md_index_str_table] = True
                table_counter += 1
                text[md_index_str] += '<div class="p-table center"><div></div>\n\n'
                text_only_doc += '<TABLE_BEGIN>\n'
                for row in table.get('tableRows'):
                    cells = row.get('tableCells')
                    for cell in cells:
                        cell_content_element = cell.get('content')
                        cell_content, text_only_doc_tmp, _ = read_strucutural_elements(document, cell_content_element, text[md_index_str], footnotes_text, False)
                        cell_content = cell_content.rstrip()
                        cell_content = cell_content.replace('\n', '<br>')  
                        text[md_index_str] += "| " + cell_content + " "
                        text_only_doc += text_only_doc_tmp

                    text[md_index_str] += "|\n"

                    if table_header:
                        table_header = False
                        text[md_index_str] += "|"
                        columns = table.get('columns')
                        for x in range(0,columns):
                            text[md_index_str] += ' --- |'
                text[md_index_str] += '\n</div>\n'
                text_only_doc += '<TABLE_END>\n'

        elif 'tableOfContents' in value:
            ## Remove contents if exist in _index1
            if md_index_str == '_index_1':
                text[md_index_str] = text[md_index_str].replace("\n\n<font size=\'2\'>**Contents**\n</font>\n\n", '\n\n')
                text[md_index_str] = text[md_index_str].replace("<font size=\'2\'>**Contents**\n</font>\n\n", '')
                text[md_index_str] = text[md_index_str].replace("\n\n<font size=\'2\'>Contents\n</font>\n\n", '\n\n')
                text[md_index_str] = text[md_index_str].replace("<font size=\'2\'>Contents\n</font>\n\n", '')

            verbose_print("Ignoring pageBreak")
            text_only_doc += '<TOC>\n'     
        elif 'sectionBreak' in value:
            verbose_print("Ignoring sectionBreak")
            text_only_doc += '<SECTION_BREAK>\n'
        else:
            verbose_print("Unkown Element Found... Please add to code")

    text[md_index_str] += '  \n  \n' + footnotes_text

    return text[md_index_str], text_only_doc, text

def main():
    global issues_headers, md_doc_global, wrong_words, current_dir, final_dir_md, final_dir_bm, doc_lists, headless, files_map, urls_map, download_dir, bitmap_path_md, vp, scan, DOCUMENT_ID, DOCUMENT_TITLE, DOCUMENT_URL, SUGGEST_MODE, figure_list, table_list, spaces_list, nl_list, doc_meta, doc_meta_dir

    wrong_words = get_json_file(".","config.json")

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
    else:
        headless = False

    if 'wordlist_show' in args and args.wordlist_show and scan:
        count = 0
        print("\nIncorrect Words defined:")
        print("------------------------")
        print("Case Insensitive words:")
        for key, value in wrong_words['badwords'].items():
            count += 1
            print("   %s. '%s' --> '%s'" % (count, key, value))

        count = 0
        print("\nCase Sensitive words:")
        for key, value in wrong_words['badwordscase'].items():
            count += 1
            print("   %s. '%s' --> '%s'" % (count, key, value))

        count = 0
        print("\nExceptions for sentences with bad words:")
        for key, value in wrong_words['badwordsok'].items():
            count += 1
            print("   %s. '%s' --> '%s'" % (count, value, key))

        sys.exit(0)

    if not os.path.exists(download_dir) and scan == False:
        verbose_print("Creating: %s folder for Chromium downloads (fixed location)" % download_dir)
        os.makedirs(download_dir)

    DOCUMENT_ID = args.id[0]
    DOCUMENT_URL = "https://docs.google.com/document/d/" + DOCUMENT_ID

    if args.command == "headless" or args.command == "headful":
        final_dir_bm = args.bitmap_destination[0].rstrip('/')
        final_dir_md = args.doc_destination[0].rstrip('/')
        
        if 'reference_path' in args and args.reference_path != None:
            bitmap_path_md = args.reference_path[0].rstrip('/')
        else:
            bitmap_path_md = final_dir_md

        if not os.path.exists(final_dir_bm):
            print("Error: Image destination given %s does not exist, exiting..." % final_dir_bm, file=sys.stderr)
            exit (1)

        if not os.path.exists(final_dir_md):
            print("Error: MD file destination given %s does not exist, exiting..." % final_dir_md, file=sys.stderr)
            exit (1)

    if scan == False and args.cache_enable == False:
        files_map, urls_map = parse_gdoc.parseDocument(DOCUMENT_URL, username, pwdfile, download_dir, headless, vp)
        if args.write_cache:
            save_object_file(current_dir + "/cache/" + DOCUMENT_ID + "_files_map.picl", files_map)
            save_object_file(current_dir + "/cache/" + DOCUMENT_ID + "_urls_map.picl", urls_map)

    if scan == False and args.cache_enable:
        files_map = read_object_file(current_dir + "/cache/" + DOCUMENT_ID + "_files_map.picl")
        urls_map = read_object_file(current_dir + "/cache/" + DOCUMENT_ID + "_urls_map.picl")
        for key, value in files_map.items():
            verbose_print("files_map['%s'] = '%s'" % (key, value))
        for key, value in urls_map.items():
            verbose_print("urls_map['%s'] = '%s'" % (key, value))


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
    doc_title_name = DOCUMENT_TITLE.replace(' ', '_')
    doc_title_name_text_only = DOCUMENT_TITLE.replace(' ', '_')

    verbose_print('Processing document: {}'.format(document.get('title')))

    doc_content = document.get('body').get('content')
    doc_lists = document.get('lists')
    #doc_footers = document.get('footers')
    doc_footnotes = document.get('footnotes')

    #print(json.dumps(document, indent=4, sort_keys=True))
    #print(json.dumps(doc_footnotes, indent=4, sort_keys=True))

    populate_lists(doc_lists)
    populate_footnotes(doc_footnotes)

    md, text_only_doc, md_doc = read_strucutural_elements(document, doc_content, '', '', False)

    ## Add last text to the global md file ##
    md_doc_global += md

    ## Strip any itmes with only NL and spaces, have to start with heading '##' to be kept ## 
    md_doc = clean_md_dict(md_doc)

    if scan == False:

        ns_path = final_dir_md + '/' + doc_title_name
        md_path = final_dir_md + '/MD'
        txt_path = final_dir_md + '/TXT'

        if not os.path.exists(final_dir_md):
            verbose_print("Creating %s folder for final md files" % final_dir_md)
            os.makedirs(final_dir_md)
        else:
            verbose_print("Folder: %s exists, using it, will overwrite any existing files with same name" % final_dir_md)

        if args.full_docset:

            if not os.path.exists(txt_path):
                verbose_print("Creating: %s folder for final txt file" % txt_path)
                os.makedirs(txt_path)
            else:
                verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name: %s" % (txt_path, doc_title_name_text_only))

            local_name = txt_path + '/' + doc_title_name_text_only + '.txt'
            verbose_print("Creating file: %s" % (local_name))

            ## Writing the full TXT file ##
            with open(local_name , 'w', encoding='utf-8') as f:
                f.write(text_only_doc)
            f.close()

        if 'hugo_split' in doc_meta and doc_meta['hugo_split'] == "True":

            ## reconstruct md_doc_global from clean dict
            md_doc_global = ''
            for key, value in md_doc.items():
                md_doc_global += md_doc[key]['text']

            ## Add table to global md
            md_doc_global = css_def + md_doc_global

            for key, value in md_doc.items():
                idx_path = final_dir_md + '/' + value['name']
                idx_filename = key + '.md'
                img_path = final_dir_bm + '/' + value['name']

                pwd_path = os.getcwd()
                verbose_print("My working dir is: %s" % pwd_path)

                if not value['name'] == 'Main' or args.full_docset:
                    if not os.path.exists(idx_path):
                        verbose_print("Creating: %s folder for final md file" % idx_path)
                        os.makedirs(idx_path)
                    else:
                        verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name: %s" % (idx_path, idx_filename))

                    if not os.path.exists(img_path):
                        verbose_print("Creating: %s folder for the images for Heading: %s" % (img_path, value['name']))
                        os.makedirs(img_path)
                    else:
                        verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name" % idx_path)

                    if value['table']:
                        value['text'] = css_def + value['text']

                    value['text'] = value['hugo_header'] + value['text']
                    
                    local_name = idx_path + '/' + idx_filename
                    for iname in value['images']:
                        iname_basename = os.path.basename(iname)
                        iname_path = os.path.dirname(iname)
                        iname_new = iname_path + '/' + value['name'] + '/' + iname_basename
                        iname_current = final_dir_bm + '/' + iname_basename
                        iname_new_absoule = img_path + '/' + iname_basename

                        if os.path.isfile(iname_new_absoule):
                            verbose_print("Removing file: %s " % iname_new_absoule)
                            os.remove(iname_new_absoule)
                        verbose_print("Moving file: %s to %s" % (iname_current, iname_new_absoule))
                        os.rename(iname_current, iname_new_absoule)
                        value['text'] = value['text'].replace(iname, iname_new)
                        md_doc_global = md_doc_global.replace(iname, iname_new)


                    verbose_print("Creating file: %s" % (local_name))
                    ## Writing the full idx file ##
                    with open(local_name, 'w', encoding='utf-8') as f:
                        f.write(value['text'])
                    f.close()
        else:
            ## reconstruct md_doc_global from clean dict
            md_doc_global = ''
            for key, value in md_doc.items():
                if not 'MAIN' in key:
                    md_doc_global += md_doc[key]['text']

            ## Add table to global md
            md_doc_global = css_def + md_doc_global

            img_path = final_dir_bm + '/' + doc_title_name
            if not os.path.exists(img_path):
                verbose_print("Creating: %s folder for the images" % (img_path))
                os.makedirs(img_path)
            else:
                verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name" % (img_path))

            table_flag = False
            for key, value in md_doc.items():
                if value['table']:
                    table_flag = True

                for iname in value['images']:
                        iname_basename = os.path.basename(iname)
                        iname_path = os.path.dirname(iname)
                        iname_new = iname_path + '/' + doc_title_name + '/' + iname_basename
                        iname_current = final_dir_bm + '/' + iname_basename
                        iname_new_absoule = img_path + '/' + iname_basename

                        if os.path.isfile(iname_new_absoule):
                            verbose_print("Removing file: %s " % iname_new_absoule)
                            os.remove(iname_new_absoule)

                        if not 'MAIN' in key:
                            verbose_print("Moving file: %s to %s" % (iname_current, iname_new_absoule))
                            os.rename(iname_current, iname_new_absoule)
                            md_doc_global = md_doc_global.replace(iname, iname_new)
                        else:
                            verbose_print("Removing image, belongs to MAIN: %s" % (iname_current))
                            os.remove(iname_current)

            if table_flag:
                md_doc_global = css_def + md_doc_global

            hugoheader,_ = get_hugo_header(md_doc['MAIN']['doc_title'], md_doc['MAIN']['categoris'], 0, '' )
            md_doc_global = hugoheader + md_doc_global

            local_name = ns_path + '/_index_1.md'
            if not os.path.exists(ns_path):
                verbose_print("Creating %s folder for final md file" % ns_path)
                os.makedirs(ns_path)
            else:
                verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name: %s" % (ns_path, '_index_1'))

            verbose_print("Creating file: %s" % (local_name))
            ## Writing the full MD file ##
            with open(local_name, 'w', encoding='utf-8') as f:
                f.write(md_doc_global)
            f.close()

        if args.full_docset:
            local_name = md_path + '/' + doc_title_name + '.md'

            if not os.path.exists(md_path):
                verbose_print("Creating %s folder for final md file" % md_path)
                os.makedirs(md_path)
            else:
                verbose_print("Folder: %s exists, using it, will overwrite any existing file with same name: %s" % (md_path, local_name))

            verbose_print("Creating file: %s" % (local_name))
            ## Writing the full MD file ##
            with open(local_name, 'w', encoding='utf-8') as f:
                f.write(md_doc_global)
            f.close()

        verbose_print("Final MD folder: %s" % final_dir_md)

    # Post Parsing
    regex = r"(?<=[^\*\*]\*Figure\s)\d{1,3}(?=\.)"
    figure_list = re.findall(regex, md, re.MULTILINE)

    regex = r"(?<=[^\*\*]\*Table\s)\d{1,3}(?=\.)"
    table_list = re.findall(regex, md, re.MULTILINE)

    regex = r"[ ]{2,}"
    spaces_list = re.findall(regex, text_only_doc, re.MULTILINE)

    regex = r"[\n]{3,}"
    nl_list = re.findall(regex, text_only_doc, re.MULTILINE)

    scan4words(text_only_doc)
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
    parser_a.add_argument('-f', '--full_docset', action='store_true', help='Generates the Main, MD and TXT folders')
    parser_a.add_argument('-i', '--id', required=True, nargs=1, help='Google Doc ID', metavar="")
    parser_a.add_argument('-r', '--reference_path', nargs=1, help='Relative or Absolute path to images, used in md file, if obitted bitmap_destination is used', metavar="")
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
    parser_b.add_argument('-f', '--full_docset', action='store_true', help='Generates the Main, MD and TXT folders')
    parser_b.add_argument('-i', '--id',required=True, nargs=1, help='Google Doc ID', metavar="")
    parser_b.add_argument('-r', '--reference_path', nargs=1, help='Relative or Absolute path to images, used in md file, if obitted bitmap_destination is used', metavar="")
    parser_b.add_argument('-v', '--verbose', action='store_true', help='Verbose text')
    parser_b.add_argument('-w', '--write_cache', action='store_true', help='Stores the map liks to current dir, after successful run, needed by -c flag')
    add_syntax_inclusion(parser_name, "id,bitmap_destination, doc_destination")
    add_syntax_exlusion(parser_name, "cache_enable, write_cache")


    parser_name="scan"
    parser_c = subparsers.add_parser(parser_name, help='Scans a Google Doc and reports stats')
    parser_c.add_argument('-a', '--accept_suggestions', action='store_true', help='Reads the document as if all suggestions where accepted, if not set suggestions are ignored.')
    parser_c.add_argument('-m', '--meta_ignore', action='store_true', help='Ignores any metafile associated with this doc.')
    parser_c.add_argument('-i', '--id', required=False, nargs=1, help='Google Doc ID', metavar="")
    parser_c.add_argument('-w', '--wordlist_show', action='store_true', help='Shows the Bad Words and exception sentences.')
    add_syntax_exlusion(parser_name, "id, wordlist_show")

    if len(sys.argv)==1:
      parser.print_help()
      exit(0)

    args = parser.parse_args()

    check_syntax(args)

    main()
