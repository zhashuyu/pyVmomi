#!/bin/bash


# 初始化数据库，已当天日期为标识
python3 prepare.py

# 获取虚拟机信息并写入数据库
python3 getallvms.py

# 获取ESX主机信息并定入数据库，此信息为特定信息，主要为ESX主机CPU、内存分配率
python3 getesxhost.py

# 导出EXCEL文件，已当天日期为标识
python3 export_excel.py
