# setting up connection to nexus server with pypi

1. request account in nexus repo server with update privilege to pypi repo.

result: **url + username + password**

2. create/update `~/.pypirc` with proper nexus **url + username + password**
```bash
[distutils]
index-servers =
    pypi
    nexus

[pypi]
username:
password:

[nexus]
repository:https://YOUR_NEXUS_PYPI_SERVER/
username:<username>
password:<password>
```

3. run `./dev_run.sh register` command to register your python package into nexus pypi repo

4. run `./dev_run.sh upload` command to upload your python package into nexus pypi repo