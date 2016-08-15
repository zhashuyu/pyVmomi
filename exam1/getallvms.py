#!/usr/bin/env python3
# -*- coding: utf8 -*-

# 在Python中进行两个整数相除的时候，在默认情况下都是只能够得到整数的值，而在需要
# 进行对除所得的结果进行精确地求值时，想在运算后即得到浮点值，需要导入实除法模块
# 结果即为浮点数
from __future__ import division

import re
import ssl
import atexit
import sqlite3
import datetime

from pyVim import connect
from pyVmomi import vim

SQLFile = 'data/taizhang.' + datetime.datetime.now().strftime('%Y%m%d') +'.sqlite3'
database = sqlite3.connect(SQLFile)
# database.set_character_set('utf8')


def import_guestos(database, records):
    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    for item in records:
        # cursor.execute("INSERT INTO guestos VALUES " + str(item) )
        sql = "INSERT INTO guestos VALUES " + str(item)
        cursor.execute(sql)
    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()
    database.close()


def get_vm_info(virtual_machine, cluster_list, vc):

    summary = virtual_machine.summary

    # summary.config.guestFullName,

    if summary.runtime.connectionState == 'disconnected':
        VM_INFO = ()
        return VM_INFO

    VM_User = ''
    VM_Usage = ''
    VM_Deadline = ''
    for i in virtual_machine.summary.customValue:
        if i.key == 102:
            VM_Usage = i.value
        elif i.key == 703:
            VM_Deadline = i.value
        elif i.key == 702:
            VM_User = i.value

    ESX_HOST = summary.runtime.host.name
    # If host not in any cluster, then cluster name is null
    Cluster_Name = ''
    for cluster_name in cluster_list:
        for host in cluster_name.host:
            if host.name == ESX_HOST:
                Cluster_Name = cluster_name.name
    # 列举DISK
    disk_list = []
    hardware = virtual_machine.config.hardware
    for each_vm_hardware in hardware.device:
        if (each_vm_hardware.key >= 2000) and (each_vm_hardware.key < 3000):
            disk_list.append('{} | {:.1f}GB | Thin: {} | {}'.format(each_vm_hardware.deviceInfo.label,
                                                         each_vm_hardware.capacityInKB/1024/1024,
                                                         each_vm_hardware.backing.thinProvisioned,
                                                         each_vm_hardware.backing.fileName))

    ip_list = []
    proip_list = []
    manip_list = []
    othip_list = []
    mac_list = []
    for net in virtual_machine.guest.net:
        # print(net.ipConfig.ipAddress)
        if len(net.ipAddress) > 0:
            ip_list.extend(net.ipAddress[:])
        mac_list.append('{}'.format(net.macAddress))
    # for i in ip_list:
    #     if i.startswith("fe80"):
    #         ip_list.remove(i)
    #     if i.startswith("169"):
    #         ip_list.remove(i)
    for i in ip_list:
        if i.startswith("10."):
            proip_list.append(i)
        elif i.startswith("172."):
            manip_list.append(i)
        elif i.startswith("192"):
            othip_list.append(i)

    Space_Used = summary.storage.committed/1024/1024/1024
    Space_Used = "%.2f" % Space_Used
    Space_Provisioned = (summary.storage.uncommitted + virtual_machine.summary.storage.committed)/1024/1024/1024
    Space_Provisioned = "%.2f" % Space_Provisioned

    if summary.guest.hostName is None:
        hostname = ''
        abbsys = ''
    else:
        hostname = summary.guest.hostName
        abbsys = re.sub('[0-9].*', '', hostname)
    if summary.config.annotation is None:
        mark = ''
    else:
        mark = summary.config.annotation
    VM_INFO = (
        summary.runtime.powerState,
        summary.config.name,
        hostname,
        summary.config.guestFullName,
        # '\n'.join(ip_list),
        ' '.join(proip_list),
        ' '.join(manip_list),
        ' '.join(othip_list),
        # '\n'.join(mac_list),
        Space_Used,
        Space_Provisioned,
        vc,
        Cluster_Name,
        summary.runtime.host.name,
        # VM_User,
        # VM_Usage,
        # VM_Deadline,
        # 是否为模板
        # summary.config.template,
        summary.config.vmPathName,
        summary.config.memorySizeMB,
        summary.config.numCpu,
        summary.config.numEthernetCards,
        abbsys,
        summary.config.uuid,
        # 注释
        mark
        # '\n'.join(disk_list)
    )
    return VM_INFO


def connect_vc(host, user, password):

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE
    si = connect.SmartConnect(host=host, user=user, pwd=password, sslContext=context)
    atexit.register(connect.Disconnect, si)
    content = si.RetrieveContent()
    container = content.rootFolder  # starting point to look into
    recursive = True  # whether we should look into it recursively
    VM_viewType = [vim.VirtualMachine]  # object types to look for
    VM_containerView = content.viewManager.CreateContainerView(container, VM_viewType, recursive)
    CLS_viewType = [vim.ClusterComputeResource]  # object types to look for
    CLS_containerView = content.viewManager.CreateContainerView(container, CLS_viewType, recursive)
    VM_Children = VM_containerView.view
    CLS_Children = CLS_containerView.view

    Record_All = []
    for child in VM_Children:
        Record = get_vm_info(child, CLS_Children, host)
        if len(Record) == 0:
            continue
        # print(Record)
        Record_All.append(Record)

    import_guestos(database, Record_All)


def main():

    connect_vc("10.0.0.101", "root", "123456")


# Start program
if __name__ == "__main__":
    main()
