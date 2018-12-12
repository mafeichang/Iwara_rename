# -*- encoding: utf-8 -*-
import re
import requests
import os
from lxml import etree

input_path = u'.'
date_re = re.compile(r'[0-2]{1}[0-9]{3}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}')
renamed_filename_re = re.compile(r'^\[.*\] [0-2]{1}[0-9]{3}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}')  # 判断文件名是否已格式化
del_re = re.compile(r'^\[.*\]|1080p|2160p|4K|Iwara|60fps|Iwara|_Source|- Pornhub.com|(1080p60fps)|- 成人视频 成人')
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
           'AppleWebKit/537.36 (KHTML, like Gecko) '
           'Chrome/56.0.2924.87 Safari/537.36'}
proxies = {'http': "socks5://127.0.0.1:1080", 'https': "socks5://127.0.0.1:1080"}


def main():
    for folder_tuple in os.walk(input_path):
        folder_path, _, file_list = folder_tuple
        if file_list:
            for file_name in file_list:
                try:
                    renamed = re.findall(renamed_filename_re, file_name)
                    before_file_path = os.path.join(folder_path, file_name)
                    (search_name, extension) = os.path.splitext(file_name)
                    if renamed or extension != '.mp4':
                        print('%s\n该文件不需重命名\n\n' % file_name)
                        continue
                    else:
                        search_name = del_re.sub('', search_name)
                        search_name = search_name.replace('_', ' ')
                        mmd_url = 'https://ecchi.iwara.tv/search?query=' + search_name
                        r = requests.get(mmd_url, headers=headers, proxies=proxies)
                        file_content = r.text
                        tree = etree.HTML(file_content)
                        mmd_artist = tree.xpath('//*/div[@id="block-system-main"]/div/div/div/div/div/div/div/div/div/div/a/text()')[0]
                        mmd_name = tree.xpath('//*/div[@id="block-system-main"]/div/div/div/div/div/div/div/div/div/h3/a/text()')[0]
                        mmd_date_re = tree.xpath('//*/div[@id="block-system-main"]/div/div/div/div/div/div/div/div/div/div/text()[2]')[0]
                        mmd_hash_re = tree.xpath('//*/div[@id="block-system-main"]/div/div/div/div/div/div/div/div/div/h3/a/@href')[0]
                        mmd_date = re.findall(date_re, mmd_date_re)[0]
                        mmd_hash = mmd_hash_re[8:]
                        output_name = '[%s] %s %s_%s_Source' % (mmd_artist, mmd_date, mmd_name, mmd_hash)
                        filtered_output_name = (''.join([i for i in output_name if i not in r"/\\:*?\"<>|"])).strip()
                        after_file_path = os.path.join(folder_path, filtered_output_name) + extension
                        os.rename(before_file_path, after_file_path)
                        print('%s\n重命名为\n%s\n' % (file_name, filtered_output_name + extension))
                except Exception as e:
                    print('%s \n重命名失败，原因：\n%s\n' % (file_name, e))
    input('Press Enter to exit...')


if __name__ == '__main__':
    main()
