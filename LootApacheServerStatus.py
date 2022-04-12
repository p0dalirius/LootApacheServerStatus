#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : LootApacheServerStatus.py
# Author             : Podalirius (@podalirius_)
# Date created       : 7 Apr 2022

import requests
from bs4 import BeautifulSoup
import argparse


def get_infos(url, verify=True):
    r = requests.get(url, verify=verify)
    soup = BeautifulSoup(r.content, "lxml")
    table = soup.findAll("table")[1]
    data = []
    if table is not None:
        columns = [td.text for td in table.findAll("th")]
        for row in table.findAll("tr")[1:]:
            # Srv	PID	Acc	M	CPU 	SS	Req	Conn	Child	Slot	Client	VHost	Request
            values = [td.text for td in row.findAll("td")]
            # columns = ["Srv", "PID", "Acc", "M", "CPU", "SS", "Req", "Conn", "Child", "Slot", "Client", "VHost", "Request"]
            values = {columns[k]: values[k] for k in range(len(values))}
            if len(values.keys()) != 0:
                data.append(values)
    return data


def parseArgs():
    print("LootApacheServerStatus v1.1 - by @podalirius_\n")

    parser = argparse.ArgumentParser(description="A script to automatically dump all URLs present in /server-status to a file locally.")
    parser.add_argument("-t", "--target", dest="target", action="store", type=str, required=True, help="URL of the Apache server-status to connect to.")
    parser.add_argument("-l", "--logfile", dest="logfile", action="store", type=str, required=False, default=None, help="Output URLs to specified logfile.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help='Verbose mode. (default: False)')
    parser.add_argument("-k", "--insecure", dest="insecure_tls", action="store_true", default=False, help="Allow insecure server connections when using SSL (default: False)")
    return parser.parse_args()


if __name__ == '__main__':
    options = parseArgs()

    if not options.target.startswith("http://") and not options.target.startswith("https://"):
        options.target = "http://" + options.target

    if options.insecure_tls:
        # Disable warings of insecure connection for invalid certificates
        requests.packages.urllib3.disable_warnings()
        # Allow use of deprecated and weak cipher methods
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            pass

    urls = []

    r = requests.get(options.target, verify=(not options.insecure_tls))
    if b"Apache Server Status" in r.content:
        running = True
        while running:
            try:
                data = get_infos(options.target, verify=(not options.insecure_tls))
                for entry in data:
                    host = entry['VHost']
                    if " " in entry['Request']:
                        path = entry['Request'].split(' ')[1].split(' ')[0]
                        if entry['VHost'].endswith(":80"):
                            new_url = "http://%s%s" % (entry['VHost'][:-3], path)
                        elif entry['VHost'].endswith(":443"):
                            new_url = "https://%s%s" % (entry['VHost'][:-4], path)
                        else:
                            new_url = "http://%s%s" % (entry['VHost'], path)
                        if new_url not in urls:
                            urls.append(new_url)
                            if options.logfile is not None:
                                f = open(options.logfile, "a")
                                f.write(new_url+"\n")
                                f.close()
                            print(new_url)

            except KeyboardInterrupt as e:
                running = False
    else:
        print("[!] Could not detect 'Apache Server Status' in page.")
