# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time


class P3ScrapyPipeline(object):
    def process_item(self, item, spider):
        # fs = open(item['mdFilePath'], 'w')
        date_time = item["date_time"]
        if date_time:
            pass
        else:
            date_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        with open(item['mdFilePath'], 'w') as fs:
            fs.write('---\n')
            fs.write('title: ' + item["title"] + '\n')
            fs.write('date: ' + date_time + '\n')
            fs.write('keywords: ' + item["keywords"] + '\n')
            fs.write('description: ' + item["description"] + '\n')
            fs.write('categories: ' + item["categories"] + '\n')
            fs.write('---\n')
            fs.write(item["content"] + '\n')
            # fs.write('###### 转载自菲龙网')
            return item
