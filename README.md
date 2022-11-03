# pim-xmlconverter

## Folder Structure

- input (holds the study programm descriptions of the THL, sorted into subdirectories based on their study department)
- output (holds the resulting xml files that python script convert.py produces)
- convert.py (Python Script that converts module descriptions of the THL into pim_edci xml-files)

## Availability THL module descriptions for study programmes

### AN

- [ ] Angewandte Chemie Bachelor
- [ ] Biomedical Engineering Master
- [x] Biomedizintechnik Bachelor
- [ ] Chemie- und Umwelttechnik (auslaufend) Bachelor
- [ ] Hörakustik Bachelor
- [ ] Hörakustik und Audiologische Technik Master
- [ ] Medical Microtechnology Master
- [x] Physikalische Technik Bachelor
- [ ] Regulatory Affairs Master
- [ ] Technische Biochemie Master
- [ ] Umweltingenieurwesen und -management Bachelor

### Bau

- [x] Architektur Bachelor
- [x] Architektur Master
- [ ] Bauingenieurwesen Bachelor
- [ ] Bauingenieurwesen Master
- [x] Nachhaltige Gebäudetechnik Bachelor
- [x] Stadtplanung Bachelor
- [x] Stadtplanung Master
- [ ] Water Engineering Master

### EI

- [x] Allgemeine Elektrotechnik Bachelor
- [x] Angewandte Informationstechnik Master
- [x] Elektrotechnik - Energiesysteme und Automation Bachelor
- [x] Elektrotechnik - Kommunikationssysteme Bachelor
- [x] Informatik/ Softwaretechnik Bachelor
- [x] Informatik/Softwaretechnik für verteilte Systeme Master
- [x] Informationstechnologie und Design Bachelor
- [ ] IT-Sicherheit Online Bachelor
- [ ] Medieninformatik Online Bachelor
- [ ] Medieninformatik Online Master
- [ ] Regenerative Energien Online Bachelor

### MW

- [ ] Betriebswirtschaftslehre Bachelor
- [x] Betriebswirtschaftslehre Master
- [x] Maschinenbau Bachelor
- [x] Mechanical Engineering Master
- [x] Wirtschaftsingenieurwesen Bachelor
- [x] Wirtschaftsingenieurwesen Master
- [ ] Wirtschaftsingenieurwesen Lebensmittelindustrie (vormals Food Processing) Bachelor
- [ ] Wirtschaftsingenieurwesen Online Bachelor

## Usage

1. Put the thl modul descriptions into the folder named input
2. Run the script with "python convert.py" from inside this directory

## Prerequisites

Python Version 3.8.2 with installed libraries: itertools, lxml and xmltodict

## Validation with XMLLint

$ xmllint --schema edci/XSD/PIM/pim_edci_credential.xsd pim-xmlconverter/output/AIT_Modulbeschreibungen_pim_edciv010.xml --noout
