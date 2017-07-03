#!/usr/bin/env python

import numpy as np
import os, cv2, sys, string
import math, time, socket, urllib
from flickrapi2 import FlickrAPI
from datetime import datetime
import os.path as osp

socket.setdefaulttimeout(30)

FLICKR_PUBLIC = 'XX'
FLICKR_SECRET = 'XX'

fapi = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET)

def maybe_create(dir_path):
    if not osp.exists(dir_path):
        os.makedirs(dir_path)

def get_urls(query_string, desired_num):
    extras='url_m'
    urls = []

    try:
        rsp = fapi.photos_search(api_key=FLICKR_PUBLIC,
                                ispublic="1",
                                media="photos",
                                license="2",
                                per_page="500",
                                page='1',
                                text=query_string,
                                extras=extras)
        time.sleep(1)
        fapi.testFailure(rsp)
    except KeyboardInterrupt:
        print('Keyboard exception while querying for images, exiting\n')
        raise
    except:
        print sys.exc_info()[0]
        print ('Exception encountered while querying for images\n')

    num_pages = int(rsp.photos[0]['pages'])
    for i in xrange(num_pages):
        print 'page number ' + str(i)
        try:
            rsp = fapi.photos_search(api_key=FLICKR_PUBLIC,
                                    ispublic="1",
                                    media="photos",
                                    per_page="500",
                                    license="2",
                                    page=str(i),
                                    sort="interestingness-desc",
                                    text=query_string,
                                    extras=extras)
            time.sleep(0.5)
            fapi.testFailure(rsp)
        except KeyboardInterrupt:
            print('Keyboard exception while querying for images, exiting\n')
            raise
        except:
            print sys.exc_info()[0]
            print ('Exception encountered while querying for images\n')
        else:
            # and print them
            k = getattr(rsp, 'photos', None)
            if k:
                m = getattr(rsp.photos[0], 'photo', None)
                if m:
                    for b in rsp.photos[0].photo:
                        if b != None and b['url_m'] != 'null':
                            urls.append(b['url_m'])
        tmp = set(urls)
        if len(tmp) > desired_num:
            break
    return urls

def download_images(query_string, desired_num):
    urls = get_urls(query_string, desired_num)
    urls = set(urls)
    print query_string, len(urls)
    #urls = list(urls)

    i = 1
    out_file = open('%s.txt'%query_string,'w')
    for item in urls:
        out_file.write('%06d  %s\n'%(i, item))
        i += 1
    out_file.close()

    maybe_create(query_string)
    maybe_create(osp.join(query_string, 'original_images'))

    i = 1
    for item in urls:
        ext = osp.splitext(os.path.basename(item))[-1]
        raw_path = osp.join(query_string, 'original_images', '%09d'%i + ext)
        urllib.urlretrieve(item, raw_path)
        i += 1
        print i
        time.sleep(0.1)

if __name__ == '__main__':
    cates = ['room', 'classroom' 'dining room', 'kitchen', 'living room', 'bath room', 'bedroom', 'powder room', 'family room', 'sunroom', 'home theater', 'pantry', 'great room']
    desired_num = 100000
    for x in cates:
        download_images(x, desired_num)
