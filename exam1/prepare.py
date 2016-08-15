#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sqlite3
import datetime


guestos_sql = """
CREATE TABLE IF NOT EXISTS `guestos` (
  `status` char(10) DEFAULT NULL, -- COMMENT '状态'
  `inventory` char(10) NOT NULL DEFAULT NULL, -- COMMENT '清单名'
  `hostname` char(50) DEFAULT NULL, -- COMMENT '主机名'
  `os` char(250) DEFAULT NULL, -- COMMENT '操作系统'
  `proiplist` text DEFAULT NULL, -- COMMENT '生产IP地址'
  `maniplist` text DEFAULT NULL, -- COMMENT '管理IP地址'
  `othiplist` text DEFAULT NULL, -- COMMENT '其它IP地址'
  `diskuse` float(10) DEFAULT NULL, -- COMMENT '已用空间'
  `diskpro` float(10) DEFAULT NULL, -- COMMENT '置备空间'
  `vc` char(20) DEFAULT NULL, -- COMMENT '所属VC'
  `cluster` char(20) DEFAULT NULL, -- COMMENT 'Cluster名称'
  `esxhost` char(20) DEFAULT NULL, -- COMMENT 'ESXi主机'
  `vmx` text DEFAULT NULL, -- COMMENT 'vmx文件地址'
  `mem` int(2) DEFAULT NULL, -- COMMENT '内存/G'
  `cpu` int(2) DEFAULT NULL, -- COMMENT 'CPU计数'
  `ethernet` int(2) DEFAULT NULL, -- COMMENT '网卡计数'
  `abbsys` char(20) DEFAULT NULL, -- COMMENT '英文简称'
  `uuid` char(36) DEFAULT NULL, -- COMMENT '序列号'
  `mark` text DEFAULT NULL -- COMMENT '备注'
);
"""

vt_host_sql = """
CREATE TABLE IF NOT EXISTS `vt_host` (
  `vc` char(20) DEFAULT NULL, -- COMMENT '所属VC'
  `cluster` char(20) DEFAULT NULL, -- COMMENT 'Cluster名称'
  `esxhost` char(20) DEFAULT NULL, -- COMMENT 'ESXi主机'
  `pc_model` char(20) DEFAULT NULL, -- COMMENT '服务器型号'
  `cpu_model` char(20) DEFAULT NULL, -- COMMENT 'CPU型号'
  `cpu` int(3) DEFAULT NULL, -- COMMENT 'CPU核数'
  `cpu_assign` int(3) DEFAULT NULL, -- COMMENT 'CPU分配核数'
  `mem` int(10) DEFAULT NULL, -- COMMENT '内存大小'
  `mem_assign` int(10) DEFAULT NULL -- COMMENT 'MEM分配核数'
);
"""

vt_cluster_sql = """
CREATE TABLE IF NOT EXISTS `vt_cluster` (
  `cluster` char(20) DEFAULT NULL, -- COMMENT 'Cluster名称'
  `esxhosts` char(20) DEFAULT NULL, -- COMMENT 'ESXi主机数量'
  `guestos_all` char(20) DEFAULT NULL, -- COMMENT '可建虚拟机数量'
  `guestos_num` char(20) DEFAULT NULL, -- COMMENT '已建虚拟机数量'
  `cpu_all` char(10) DEFAULT NULL, -- COMMENT 'CPU总核数'
  `cpu_assign` char(10) DEFAULT NULL, -- COMMENT 'CPU分配核数'
  `mem_all` char(10) DEFAULT NULL, -- COMMENT '内存大小'
  `mem_assign` char(10) DEFAULT NULL -- COMMENT 'MEM分配核数'
);
"""


def main():

    # basedir = os.getcwd()
    # os.path.join(path, excelfile)
    SQLFile = 'data/taizhang.' + datetime.datetime.now().strftime('%Y%m%d') + '.sqlite3'
    database = sqlite3.connect(SQLFile)

    cursor = database.cursor()
    # delete data before update
    cursor.execute(guestos_sql)
    cursor.execute(vt_host_sql)
    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()
    database.close()


# Start program
if __name__ == "__main__":
    main()
