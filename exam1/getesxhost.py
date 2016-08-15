#!/usr/bin/env python3
# -*- coding: utf8 -*-

# 在Python中进行两个整数相除的时候，在默认情况下都是只能够得到整数的值，而在需要
# 进行对除所得的结果进行精确地求值时，想在运算后即得到浮点值，需要导入实除法模块
# 结果即为浮点数
from __future__ import division

import ssl
import atexit
import sqlite3
import datetime

from pyVim import connect
from pyVmomi import vim


SQLFile = 'data/taizhang.' + datetime.datetime.now().strftime('%Y%m%d') + '.sqlite3'
database = sqlite3.connect(SQLFile)
# database.set_character_set('utf8')


def import_cluster(records):
    cursor = database.cursor()
    for item in records:
        sql = "INSERT INTO vt_host VALUES " + str(item)
        cursor.execute(sql)
    cursor.close()
    # Commit the transaction
    database.commit()


def get_host_info(host, vc_name, cluster_name):

    summary = host.summary

    if summary.runtime.connectionState != 'connected':
        Record = ()
        return Record
    vc = vc_name
    cluster = cluster_name
    esxhost = summary.config.name
    pc_model = summary.hardware.model
    cpu_model = summary.hardware.cpuModel

    cpu = summary.hardware.numCpuThreads
    # CPU分配数
    cursor = database.cursor()
    sql = "SELECT sum(cpu) FROM guestos WHERE esxhost = " + '\'' + esxhost + '\''
    cursor.execute(sql)
    cpu_assign = cursor.fetchall()
    cpu_assign = cpu_assign[0][0]
    cursor.close()
    database.commit()
    if cpu_assign is None:
        cpu_assign = ''

    mem = int(round(summary.hardware.memorySize/1024/1024/1024))
    # MEM分配数
    cursor = database.cursor()
    sql = "SELECT sum(mem) FROM guestos WHERE esxhost = " + '\'' + esxhost + '\''
    cursor.execute(sql)
    mem_assign = cursor.fetchall()
    mem_assign = mem_assign[0][0]
    cursor.close()
    database.commit()
    if mem_assign is None:
        mem_assign = ''

    Record = (vc, cluster, esxhost, pc_model, cpu_model, cpu, cpu_assign, mem, mem_assign)
    return Record


def get_cluster_info(cluster, vc_name):

    Record_All = []
    summary = cluster.summary

    if summary.effectiveCpu == 0:
        Record = ()
        return Record

    vc_name = vc_name
    cluster_name = cluster.name

    for host in cluster.host:
        Record = get_host_info(host, vc_name, cluster_name)
        if len(Record) == 0:
            Record = ()
            return Record
        Record_All.append(Record)
    return Record_All


def connect_vc(host, user, password):

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    si = connect.SmartConnect(host=host, user=user, pwd=password, sslContext=context)
    atexit.register(connect.Disconnect, si)
    content = si.RetrieveContent()
    container = content.rootFolder  # starting point to look into
    recursive = True  # whether we should look into it recursively
    # VM_viewType = [vim.VirtualMachine]
    # VM_containerView = content.viewManager.CreateContainerView(container, VM_viewType, recursive)
    CLS_viewType = [vim.ClusterComputeResource]  # object types to look for
    CLS_containerView = content.viewManager.CreateContainerView(container, CLS_viewType, recursive)
    # VM_Children = VM_containerView.view
    CLS_Children = CLS_containerView.view

    Record_All = []
    for child in CLS_Children:
        Record = get_cluster_info(child, host)
        if len(Record) == 0:
            continue
        Record_All.extend(Record)
    # print Record_All

    # Write to database
    import_cluster(Record_All)
    database.close()


def main():

    connect_vc("10.0.0.101", "root", "123456")


# Start program
if __name__ == "__main__":
    main()
