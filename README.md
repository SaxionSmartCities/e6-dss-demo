# E6 Decision Support Demo

The E6 project is a European project aiming to increase the reuse and repair of Electronic and Electrical Equipment. 
The full acronym is:

Ecosystems for Extended-lifetime of End-of-Use Electrical and Electronic Equipment

In E6 several tools are developed and integrated into a Service Hub. The Service Hub will be a one-stop-shop for all 
tools required to run the ecosystem.   

This project demonstrates the Decision Support (DSS) tool using Streamlit and the Bayes Network model. The DSS is 
intended to help citizens and collection agents to decide whether a device is eligible for selling it in the thrift shop 
or that it is better to send it to the recycler.

The DSS is developed with a modeling tool developed by [Bayesfusion](https://www.bayesfusion.com/). The tools are 
free for Academic users. See their [website](https://www.bayesfusion.com/downloads/) to apply for a license.

## Installation
After cloning from GitHub, creates a virtual environment with Python 3.12. Install the required libraries with:
```bash
pip install -r requirements.txt
```
For the pySMILE Python wrapper you need a special command:
```bash
python -m pip install --no-cache-dir --index-url https://support.bayesfusion.com/pysmile-A/ pysmile
```

## Model
The model file is <code>e6-dss.xdsl</code>. This file can be modified with the GeNie tool. This tool is also free for 
Academic use.

## Running and Debugging with JetBrains
To run the app in JetBrains you need the following configuration:
```
module streamlit.cli.web
script parameters: run e6-dss.py
```
Other settings are default. If you get errors when running the debugger you might have to change a registry setting 
in JetBrains: <code>python.debug.asyncio.repl</code>

Do in PyCharm: Help -> Find Action: Registry
Lookup <code>python.debug.asyncio.repl</code> and uncheck the box.

## Example
See [here](doc/examples.md) for an example when running the app with streamlit.

In the current version, tje model evaluates the inputs and calculates the probability for:
* Commercial viability: Could the device still be sold in the thrift shop?
* Quality of spare parts: Could the device be used to harvest spare parts
* Risk of warranty return: If the thrift shop gives a warranty period, what would be the risk it fails in that period.

When switching on the expert user interface toggle, the probabilities will be visible. The easy interface
uses traffic lights. The cutoff values are hardcoded now.




