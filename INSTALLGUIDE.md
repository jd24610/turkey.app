# POST.Project 

Setting up reflex: 

**Installing uv: (if you haven't already)

``Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "$env:TEMP\install_uv.ps1" powershell.exe -ExecutionPolicy Bypass -File "$env:TEMP\install_uv.ps1"``

**Sync the project: 

``uv sync``

**Run the app: 

``uv run reflex run``
*if this doesn't work, try: 
``uvx reflex run``


**INSTALL DOCKER. (needed for interfacing with lightning.ai.)
Ensures compatability with the cloud service's platform 

https://docs.docker.com/desktop/setup/install/windows-install/