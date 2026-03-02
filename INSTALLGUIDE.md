# POST.Project 

Setting up reflex: 

**Installing uv: (if you haven't already)

``Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "$env:TEMP\install_uv.ps1" powershell.exe -ExecutionPolicy Bypass -File "$env:TEMP\install_uv.ps1"``

**Sync the project: (i.e., import all dependencies through pyproject.toml)

``uv sync``

**Run the app: 

``uv run reflex run``
*if this doesn't work, try: 
``uvx reflex run``

