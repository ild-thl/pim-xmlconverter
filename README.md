# pim-xmlconverter

Folder Structure:
* input (holds the study programm descriptions of the THL, sorted into subdirectories based on their study department)
* output (holds the resulting xml files that python script convert.py produces)
* convert.py (Python Script that converts module descriptions of the THL into pim_edci xml-files)
* pim_edci_credential.xsd (XML schema that describes how the output files have to look, used for validation purposes)

## Usage:
1. Put the thl modul descriptions into the folder named input 
2. Run the script with "python convert.py" from inside this directory

### Prerequisites:
Python Version 3.8.2 with installed libraries: itertools, lxml and xmltodict
    
