#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Inspired by: https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-16-04

This should be run after key generation. Assumptions about directory names are
documented below.

NOTE: This should be run as a priveleged user since it modifies stuff in /etc.

This will populate conf_output_dir with a number of key and certfiles and an
server.conf which should be suitable for Liquid Investigations use. The entire
contents of this directory can be copied to /etc/openvpn

note: this expects that ./generate-server-keys.py has been run.
note: this expects that the output of ./generate-server-keys.py is in
      openvpn-ca/keys/.
note: this expects that conf_output_dir doesn't exist.
'''

from jinja2 import Template
import os
import shutil

default_config_dict = {
    'port': '1192',
    'protocol': 'udp'
}

# set up some paths
keys_dir = os.path.join(os.getcwd(), 'openvpn-ca/keys')
config_files = list(map(lambda x: os.path.join(keys_dir, x),
               ['ca.crt', 'ca.key', 'server.crt', 'server.key', 'ta.key', 'dh2048.pem']))

conf_template_dir = os.path.join(os.getcwd(),'templates')
conf_template_file = 'server.conf.j2'
conf_output_dir = os.path.join(os.getcwd(),'openvpn-conf')
conf_output_file = 'server.conf'
ca_dir = os.path.join(os.getcwd(),'openvpn-ca')
dest_ca_dir = '/etc/openvpn/openvpn-ca'


def create_openvpn_conf(input_template_file, output_file, config_dict):
    '''
    Creates an server.conf file from the supplied template and
    dictionary. Output file is specified as output_file.
    '''
    with open(input_template_file) as vars_template, \
            open(output_file, 'w') as vars_output:

        vars_template = Template(vars_template.read())
        vars_output.write(vars_template.render(config_dict))

if __name__ == '__main__':
    os.mkdir(conf_output_dir)
    template_file = os.path.join(conf_template_dir, conf_template_file)
    output_file = os.path.join(conf_output_dir, conf_output_file)

    print('creating server.conf...')
    create_openvpn_conf(template_file, output_file, default_config_dict)
    config_files.append(output_file)

    print('copying keys and server.conf to /etc/openvpn')
    for config_file in config_files:
        shutil.copy2(config_file, '/etc/openvpn')

    print('copying CA to /etc/openvpn')
    shutil.copytree(ca_dir, dest_ca_dir)

    print('starting openvpn')
    subprocess.call(['systemctl', 'start', 'openvpn@server'])
