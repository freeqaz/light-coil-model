
## Light Coil 3d Model

### Setup

Install Miniforge
```
curl -L -o miniforge.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
```

Create and activate conda environment
```
source $HOME/miniforge/bin/activate
conda create -y --name build123d python==3.11.9
```

Install deps
```
conda install -c conda-forge -c cadquery ocp

pip install "https://github.com/CadQuery/ocp-build-system/releases/download/7.7.2.0/cadquery_ocp-7.7.2-cp311-cp311-macosx_11_0_arm64.whl"

python3 -m pip install git+https://github.com/gumyr/bd_warehouse
```

Install VS Code extension called "OCP Cad Viewer"

I can't remember exactly how I setup the environment, it was just painful. The VS Code extension did something too and it seemed to work.

### Running

In the VS Code terminal I've been running:
```
$HOME/miniforge/envs/build123d/bin/python ./light_coil.py
```

That pulls up the CAD viewer with the model for me.
