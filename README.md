# vmware_vro_workflow
> Ansible module for executing vRealize Orchestrator workflows

## Synopsis
The ```vmware_vro_workflow.py``` Python script in the library directory of this repo is an Ansible module for executing vRealize Orchestrator workflows.  

## Examples
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
