#!/usr/bin/env python

import numpy as np
import os, cv2, sys, string
import math, time, socket, urllib
from flickrapi2 import FlickrAPI
from datetime import datetime

socket.setdefaulttimeout(30)

FLICKR_PUBLIC = 'Your Flickr Key'
FLICKR_SECRET = 'Your Flickr Secret Key'

fapi = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET)

def get_urls(query_string, desired_num):
    extras='url_m'
    urls = []

    try:
        rsp = fapi.photos_search(api_key=FLICKR_PUBLIC,
                                ispublic="1",
                                media="photos",
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
                                    page=str(i),
                                    sort="interestingness-desc",
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

if __name__ == '__main__':
    urls = get_urls('cow on grass', 10000)
    urls = set(urls)
    print len(urls)
    #urls = list(urls)

    out_file = open('urls.txt','w')
    i = 1
    for item in urls:
        out_file.write('%06d  %s\n'%(i, item))
        ext = os.path.splitext(os.path.basename(item))[-1]
        raw_path = os.path.join('original_images', 'image%05d'%i + ext)
        im_path  = os.path.join('images', 'image%05d.jpg'%i)
        urllib.urlretrieve(item, raw_path)
        img = cv2.imread(raw_path, cv2.IMREAD_COLOR)
        min_dim = np.minimum(img.shape[0], img.shape[1])
        offset_x = 0.5 * (img.shape[1] - min_dim)
        offset_y = 0.5 * (img.shape[0] - min_dim)
        out_img  = img[int(offset_y):int(offset_y)+img.shape[0], int(offset_x):int(offset_x)+img.shape[1], :]
        cv2.imwrite(im_path, cv2.resize(out_img, (128, 128)))
        i += 1
        print i
        time.sleep(0.1)
    out_file.close()
