#!/usr/bin/python
"""
2018 Tony Skidmore, <tony@skidmore.co.uk>
Generate Ansible playbook and vars file from vRealize Orchestrator workflow

Allows a vRO workflow to be executed from Ansible using vmware_vro_workflow.py
Ansible module.
"""

from __future__ import print_function

try:
    import json
    import yaml
    import os
    import sys
    from jinja2 import Environment, FileSystemLoader
    import argparse
    import getpass
    import urllib3
    from urllib3.exceptions import HTTPError, SSLError
    HAS_MODULES = True
except ImportError:
    HAS_MODULES = False

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False,
    variable_start_string='"[%',
    variable_end_string='%]"'
    )


class VROClient(object):
    """ VROClient Class """

    BASE_URL = "https://{}:{}/vco/api/workflows/{}/executions/{}/"

    def __init__(self, server, listeningport, username, password,
                 workflowid, executionid, insecure):
        self.user = username
        self.pwd = password
        self.server = server
        self.port = listeningport
        self.workflowid = workflowid
        self.executionid = executionid
        self.validate_certs = insecure

    def _api_url(self):
        execution_path = self.BASE_URL.format(self.server, self.port,
                                              self.workflowid,
                                              self.executionid)
        return execution_path

    def print_url(self):
        """ output REST API URL """
        print(self._api_url())

    def _do_get(self, path):
        """ perform REST API GET method """

        if not self.validate_certs:
            urllib3.disable_warnings()

        http = urllib3.PoolManager()
        headers = urllib3.util.make_headers(basic_auth=self.user +
                                            ':' + self.pwd)

        try:
            resp = http.request('GET', path, headers=headers)
        except (HTTPError, SSLError):
            raise

        return resp.status, resp.data

    def get_workflow_execution(self):
        """ return data from vRO workflow execution """

        path = self._api_url()

        status_code, data = self._do_get(path)

        if status_code != 200:
            fail_msg = "Failed to get state workflow: {} " \
                       "execution id: {}".format(self.workflowid,
                                                 self.executionid)
            raise ValueError(fail_msg)

        return data


def render_template(template_filename, context):
    """ render Jinja2 template """
    return TEMPLATE_ENVIRONMENT.get_template(
        template_filename).render(args_dict=context)


def create_ansible_playbook(context):
    """ create playbook file """
    fname = "vro-playbook.yml"

    with open(fname, 'w') as yaml_file:
        yaml_render = render_template('playbook.j2', context)
        yaml_file.write(yaml_render)


def create_ansible_vars_file(vars_data):
    """ create vars file """
    fname = "vro-vars.yml"

    with open(fname, 'wt') as yaml_file:
        yaml.safe_dump(vars_data, yaml_file, default_flow_style=False)


def main():
    """ main function """

    if not HAS_MODULES:
        print("The required modules could not be loaded")
        sys.exit(1)

    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, required=True)
    parser.add_argument('-l', '--listeningport', type=str, default='8281')
    parser.add_argument('-e', '--executionid', type=str, required=True)
    parser.add_argument('-w', '--workflowid', type=str, required=True)
    parser.add_argument('-u', '--username', type=str, required=True)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-i', '--insecure', action='store_false')

    args = parser.parse_args()
    args_dict = vars(args)

    if not args.password:
        args_dict['password'] = getpass.getpass(prompt='Enter vRO password: ')

    vro = VROClient(**args_dict)

    vro.print_url()

    data = vro.get_workflow_execution()

    json_data = json.loads(data)
    input_params = json_data['input-parameters']
    workflow_parameters = {"workflow_parameters": {"parameters": input_params}}

    create_ansible_vars_file(workflow_parameters)

    create_ansible_playbook(args_dict)


if __name__ == '__main__':
    main()