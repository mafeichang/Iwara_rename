# -*- encoding: utf-8 -*-
#!\usr\bin\env python

import re
import requests
import os
from lxml import etree

input_path = u'.' #当前文件夹
mmd_re = re.compile(r'_[a-zA-Z0-9]{15,17}')
date_re = re.compile(r'[0-2]{1}[0-9]{3}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}')
mmd_10num_re = re.compile(r'\d{10}')
renamed_filename_re = re.compile(r'^\[.*\] [0-2]{1}[0-9]{3}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}')
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/56.0.2924.87 Safari/537.36'}
proxies = {'http': "socks5://127.0.0.1:1080", 'https': "socks5://127.0.0.1:1080"}

def main():
    for folder_tuple in os.walk(input_path):
        folder_path, _, file_list = folder_tuple
        if file_list:
            for file_name in file_list:
                renamed = re.findall(renamed_filename_re, file_name)
                before_file_path = os.path.join(folder_path, file_name)
                (_, extension) = os.path.splitext(file_name)
                if renamed or extension == '.lnk':
                    print('%s\n该文件不需重命名\n\n' % file_name)
                    continue
                else:
                    try:
                        mmd_hash = re.findall(mmd_re, file_name)
                        mmd_10num = re.findall(mmd_10num_re, file_name)
                        if mmd_hash:
                            mmd_hash = mmd_hash[0].strip('_')
                            mmd_url = 'https://ecchi.iwara.tv/videos/' + str(mmd_hash)
                            r = requests.get(mmd_url, headers=headers, proxies=proxies)
                            file_content = r.text
                            tree = etree.HTML(file_content)
                            mmd_artist = tree.xpath('//*/div[@class="node-info"]/div[1]/a/text()')[0]
                            mmd_name = tree.xpath('//*/div[@class="node-info"]/div[1]//h1/text()')[0]
                            mmd_date_re = tree.xpath('//*/div[@class="node-info"]/div[1]/text()[4]')[0]
                            mmd_date = re.findall(date_re, mmd_date_re)[0]
                            if mmd_10num:
                                output_name = '[%s] %s %s %s_%s_Source' % (
                                    mmd_artist, mmd_date, mmd_name, mmd_10num[0], mmd_hash)
                            else:
                                output_name = '[%s] %s %s_%s_Source' % (
                                    mmd_artist, mmd_date, mmd_name, mmd_hash)
                            filtered_output_name = (''.join([i for i in output_name if i not in r"/\\:*?\"<>|"])).strip()
                            after_file_path = os.path.join(folder_path, filtered_output_name) + extension
                            os.rename(before_file_path, after_file_path)
                            print('%s\n重命名为\n%s\n' % (file_name, filtered_output_name + extension))
                        else:
                            print('%s\n找不到HASH值可供重命名\n\n' % file_name)
                            continue
                    except Exception as e:
                        print('%s \n重命名失败，原因：\n%s\n' % (file_name, e))
    input('Press Enter to exit...')


if __name__ == '__main__':
    main()