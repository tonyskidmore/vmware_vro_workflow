# vmware_vro_workflow
> Ansible module for executing vRealize Orchestrator workflows

## Synopsis
The ```vmware_vro_workflow.py``` Python script in the library directory of this repo is an Ansible module for executing vRealize Orchestrator workflows.  

## Auto-Generating Ansible Playbooks from previous vRO workflow executions  
If you know the ID of the workflow that you want to execute (look for ID GUID under General tab of workflow) and the ID of an execution of that workflow (look under ID of the General tab of an execution instance of the workflow) you can auto-generate an Ansible playbook and associated vars file to replay that execution using the ```vro_workflow_to_ansible.py`` script.  
  
### Example  
Clone this repo and identify the workflowid and executionid as described above.  You can view the script parameters by using ```--help```:  

```
$ ./vro_workflow_to_ansible.py --help
usage: vro_workflow_to_ansible.py [-h] -s SERVER [-l LISTENINGPORT] -e
                                  EXECUTIONID -w WORKFLOWID -u USERNAME
                                  [-p PASSWORD] [-i]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
  -l LISTENINGPORT, --listeningport LISTENINGPORT
  -e EXECUTIONID, --executionid EXECUTIONID
  -w WORKFLOWID, --workflowid WORKFLOWID
  -u USERNAME, --username USERNAME
  -p PASSWORD, --password PASSWORD
  -i, --insecure
```
So if we had the following workflow and execution IDs:  
Workflow ID: 1b1bc06b-593e-423a-a434-1430888550de  
Execution ID: 2c9325a561f6998a0161faef558200f3  

We could use the following syntax:  
```
./vro_workflow_to_ansible.py -s vro.domain.local -u vcoadmin -w 1b1bc06b-593e-423a-a434-1430888550de -e 2c9325a561f6998a0161faef558200f3 -i
```
When the above is executed you will be prompted for ```Enter vRO password:``` if not provided on the command line (bad idea).  Once executed successfully you should get the URL of the REST API call displayed i.e. :  
https://vro.domain.local:8281/vco/api/workflows/1b1bc06b-593e-423a-a434-1430888550de/executions/2c9325a561f6998a0161faef558200f3/  

This should have created ```vro-playbook.yml``` and ```vro-vars.yml``` files.  You should then be able to just execute the Anisble playbook to replay the previous vRO workflow execution:  
```
ansible-playbook vro-playbook.yml
vRO password:
```
Re-enter you vRO password above to trigger the execution.  Even if for some reason the Ansible Playbook or vRO workflow fails you should still have the basis of creating an Ansible playbook for your requirements that may require some manual adjustment.  
  

## Manually Created Example Playbooks
* Run the workflow *test-workflow* using it's workflow name  
```
- name: run vro workflow by name
  vmware_vro_workflow:
    name: test-workflow
    hostname: vro.domain.local
    username: vcoadmin
    password: vcoadmin
```
  
* Run the workflow *test-workflow* using it's workflow ID
```
- name: run vro workflow by UUID
  vmware_vro_workflow:
    uuid: a7a1d06a-9018-40c4-9199-1ce95932311c
    hostname: vro.domain.local
    username: vcoadmin
    password: vcoadmin
```
  
* Complete playbook to prompt for credentials and run the test workflow supplying values for various inputs  
```
- name: run vRO workflow example playbook
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    validate_certs: False
    workflow_name: "test-workflow"
    vro_server: "vro.domain.local"
    workflow_timeout_seconds: 20
    workflow_wait: yes
    workflow_state: started
    input_sleep_milliseconds: 1000
    workflow_parameters:
      parameters:
        - name: 'attrSleep'
          type: 'number'
          scope: 'local'
          value:
            number:
              value: "{{ input_sleep_milliseconds }}"
        - name: 'inValue'
          type: 'string'
          scope: 'local'
          value:
            string:
              value: 'Executed by Ansible'
        - name: 'inUserPass'
          type: 'SecureString'
          scope: 'local'
          value:
            string:
              value: "a_secret"

  vars_prompt:
    - name: "username"
      prompt: "vRO username"
    - name: "password"
      prompt: "vRO password"
      private: yes

  tasks:
  - name: debug inputs
    debug:
      var: workflow_parameters

  - name: run vro workflow
    vmware_vro_workflow:
      name: "{{ workflow_name | default(omit) }}"
      uuid: "{{ workflow_uuid | default(omit) }}"
      state: "{{ workflow_state | default(omit) }}"
      hostname: "{{ vro_server }}"
      username: "{{ username }}"
      password: "{{ password }}"
      validate_certs: "{{ validate_certs | default(omit)}}"
      inputs: "{{ workflow_parameters | default(omit) }}"
      timeout: "{{ workflow_timeout_seconds | default(omit) }}"
      wait_for_workflow: "{{ workflow_wait | default(omit) }}"
    register: vro_workflow_run

  - name: debug vro_workflow_run
    debug:
      var: vro_workflow_run
```

## Contributing

1. Fork it (<https://github.com/tonyskidmore/vmware_vro_workflow>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
