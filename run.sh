#!/usr/bin/env bash
cd ./p3scrapy/
pwd
echo "=====start scrapy====="
#scrapy crawl dmoz
echo "=====end scrapy====="
cd ../
pwd
echo "=====start git====="
datename=$(date +%Y-%m-%d_%H:%M)
echo $datename
git add source/*
git commit -m "$datename"
git push
