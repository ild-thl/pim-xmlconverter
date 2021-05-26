import os
import itertools
from lxml import etree as et
import xmltodict

# Following Mappings map the values used in the xml files of the THL
# to the according values of the edci format
veranstaltungsart_mapping = {
    # possible EDCI types: classroom, workShop, lab
    "Vorlesung": "http://data.europa.eu/europass/learningActivityType/classroom",
    "Lecture": "http://data.europa.eu/europass/learningActivityType/classroom",
    "Online-Lehrveranstaltung": "http://data.europa.eu/europass/learningActivityType/classroom",
    "Seminar": "http://data.europa.eu/europass/learningActivityType/workShop",
    "Übung": "http://data.europa.eu/europass/learningActivityType/workShop",
    "Exercise": "http://data.europa.eu/europass/learningActivityType/workShop",
    "Project Work": "http://data.europa.eu/europass/learningActivityType/workShop",
    "Praktikum": "http://data.europa.eu/europass/learningActivityType/lab",
    "Practical Training": "http://data.europa.eu/europass/learningActivityType/lab",
    "Projekt": "http://data.europa.eu/europass/learningActivityType/workShop",
    "Exkursion": "http://data.europa.eu/europass/learningActivityType/workShop"
}
sprachen_mapping = {
    "Deutsch": "http://publications.europa.eu/resource/authority/language/DEU",
    "German": "http://publications.europa.eu/resource/authority/language/DEU",
    "English": "http://publications.europa.eu/resource/authority/language/ENG",
    "Englisch": "http://publications.europa.eu/resource/authority/language/ENG",
    "Deutsch/Englisch": "http://publications.europa.eu/resource/authority/language/ENG",
    "German/English": "http://publications.europa.eu/resource/authority/language/ENG",
    "Taught Foreign Language": "http://publications.europa.eu/resource/authority/language/ENG",
    "Gelehrte Fremdsprache": "http://publications.europa.eu/resource/authority/language/ENG"
}
assessmentType_mapping = {
    # possible EDCI types: writtenExamen, oralExamen, markedAssignment und continuousEvaluation
    "Klausur": "http://data.europa.eu/europass/assessmentType/writtenExamen",
    "Written Exam": "http://data.europa.eu/europass/assessmentType/writtenExamen",
    "Studienarbeit": "http://data.europa.eu/europass/assessmentType/continuousEvaluation",
    "Projektarbeit": "http://data.europa.eu/europass/assessmentType/continuousEvaluation",
    "Project Work": "http://data.europa.eu/europass/assessmentType/continuousEvaluation",
    "Portfolio-Prüfung": "http://data.europa.eu/europass/assessmentType/markedAssignment",
    "Portfolio Exam": "http://data.europa.eu/europass/assessmentType/markedAssignment",
    "Thesis": "http://data.europa.eu/europass/assessmentType/markedAssignment",
    "Abschlussarbeit": "http://data.europa.eu/europass/assessmentType/markedAssignment",
    "Colloquium": "http://data.europa.eu/europass/assessmentType/oralExamen",
    "Kolloquium": "http://data.europa.eu/europass/assessmentType/oralExamen",
    "Oral Exam": "http://data.europa.eu/europass/assessmentType/oralExamen",
    "Mündliche Prüfung": "http://data.europa.eu/europass/assessmentType/oralExamen",
    "Prüfungsvortrag": "http://data.europa.eu/europass/assessmentType/oralExamen"
}
# The Validity is the date of the last reaccreditation
fachbereich_validity_mapping = {
    "Angewandte Naturwissenschaften": "Seit 04.06.2020",
    "Elektrotechnik und Informatik": "Seit 04.06.2020",
    "Electrical Engineering and Computer Science": "Seit 04.06.2020",
    "Maschinenbau und Wirtschaft": "Seit 14.11.2020",
    "Mechanical Engineering and Business Administration": "Seit 14.11.2020",
    "Bauwesen": "Seit 14.11.2020"
}
organization = {
    "id": "urn:epass:thl:organization:927",
    "title": "Technische Hochschule Lübeck",
    "type": "http://data.europa.eu/esco/agent-type#academic-institution",
    "location": "http://publications.europa.eu/resource/authority/country/DEU",
    "registration": "DUMMY-REGISTRATION"
}

# xml namespaces
DEFAULT_NS = 'http://data.europa.eu/europass/model/credentials#'
DEFAULT = '{%s}' % DEFAULT_NS
EUP_NS = 'http://data.europa.eu/europass/model/credentials#'
EUP = '{%s}' % EUP_NS
NS2_NS = 'http://uri.etsi.org/01903/v1.3.2#'
NS2 = '{%s}' % NS2_NS
NS3_NS = 'http://www.w3.org/2000/09/xmldsig#'
NS3 = '{%s}' % NS3_NS
NS4_NS = 'http://uri.etsi.org/01903/v1.4.1#'
NS4 = '{%s}' % NS4_NS
NS5_NS = 'http://data.europa.eu/europass/model/credentials#'
NS5 = '{%s}' % NS5_NS
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
XSI = '{%s}' % XSI_NS

SCHEMALOCATION = "http://data.europa.eu/europass/model/credentials# pim_edci_credential.xsd"

NSMAP = {None: DEFAULT_NS, 'eup': EUP_NS, 'ns2': NS2_NS,
         'ns3': NS3_NS, 'ns4': NS4_NS, 'ns5': NS5_NS, 'xsi': XSI_NS}

# Returns only the text inside a given dictionary, and formats the the text according to the xml tag


def unpackDict(d, key=''):
    result = ''
    if isinstance(d, dict):
        for (k, v) in d.items():
            result += unpackDict(v, k)
            if((k == 'li' or k == 'p') and not result.endswith('\n')):
                result += "\n"
    elif isinstance(d, list):
        for v in d:
            if key == 'li':
                result += '\t- '
            result += unpackDict(v)
            if not result.endswith('\n'):
                result += '\n'
    elif isinstance(d, str):
        result += d
        result = result.strip()

    return result


class LearnSpecRef:
    def __init__(self, xml, root):
        self.modul_descriptions = [
            modul_descriptions for modul_descriptions in xml['Modulbeschreibung']]
        self.modules = [Module(modul_desc)
                        for modul_desc in self.modul_descriptions]

        self.id = generateIdFromFilename(filename)
        self.studyProgramme_id = "urn:thl:learning:spec:studyprogramme:" + self.id
        self.studyProgramme = xml['Modulbeschreibung'][0]['Modul']['M_Studiengang']

        self.degree = 'B. Sc.'
        if xml['Modulbeschreibung'][0]['Modul']['M_Niveau'] == 'Master':
            self.degree = 'M. Sc.'

        self.node = et.SubElement(
            root, NS5+'learningSpecificationReferences')

    # Creates xml data
    def build(self):
        # Create StudyProgramme
        studyProgramme_node = et.SubElement(self.node, NS5+'studyProgramme')
        studyProgramme_node.set(
            'id', self.studyProgramme_id)
        studyProgramme_title_node = et.SubElement(
            studyProgramme_node, NS5+'title')
        studyProgramme_title_node.set('lang', 'de')
        studyProgramme_title_node.text = self.studyProgramme
        education_node = et.SubElement(
            studyProgramme_node, NS5+'hasEducationLevel')
        education_targetName_node = et.SubElement(
            education_node, NS5+'targetName')
        education_targetName_node.set('lang', 'de')
        education_targetName_node.text = self.degree

        # Create Stupo
        stupo_node = et.SubElement(self.node, NS5+'stupo')
        stupo_node.set('id', "urn:thl:learning:spec:stupo:" + self.id)
        stupo_title_node = et.SubElement(stupo_node, NS5+'title')
        stupo_title_node.set('lang', 'de')
        stupo_title_node.text = self.studyProgramme
        stupo_specOf_node = et.SubElement(stupo_node, NS5+'specializationOf')
        stupo_specOf_node.set('idref', self.studyProgramme_id)

        # Create StudySection
        studySection_node = et.SubElement(self.node, NS5+'studySection')
        studySection_node.set(
            'id', "urn:thl:learning:spec:studysection:" + self.id)
        studySection_title_node = et.SubElement(studySection_node, NS5+'title')
        studySection_title_node.set('lang', 'de')
        studySection_title_node.text = self.studyProgramme

        for module in self.modules:
            module.build(self.node, studySection_node)


class Module:
    static_id = itertools.count(start=10100, step=17)

    def __init__(self, xml):
        self.xml = xml
        modul = xml['Modul']
        lehrveranstaltungen = xml['Lehrveranstaltungen']

        # module
        self.module_id = str(next(Module.static_id))
        self.module_full_id = "urn:thl:learning:spec:" + self.module_id
        self.module_type = "http://data.europa.eu/europass/learningOpportunityType/programModule"
        self.module_title = 'Modul ' + self.module_id

        # Module Specialization
        self.mspec_id = self.module_id + '#1'
        self.full_id = "urn:thl:learning:spec:" + self.mspec_id
        alllearningEvents = [LearningEvent(lehrveranstaltungen[key], self.mspec_id, str(index+1)) for (
            index, key) in enumerate(lehrveranstaltungen)]
        self.learningEvents = [
            x for x in alllearningEvents if (x.learnActSpec.type != "" and x.learnActSpec.title != "")]
        self.learningOutcome = LearningOutcome(xml, self.mspec_id)
        self.description = Module.generateDescription(lehrveranstaltungen)
        self.mspec_title = modul['M_Modulname']
        self.mspec_type = "http://data.europa.eu/europass/learningOpportunityType/course"
        self.ects = modul['M_ECTS_Leistungspunkte']
        self.volumeOfLearning = 0
        if modul['M_Arbeitsaufwand_in_Stunden'] is not None:
            if isinstance(modul['M_Arbeitsaufwand_in_Stunden'], str):
                self.volumeOfLearning += int(
                    modul['M_Arbeitsaufwand_in_Stunden'])
            else:
                self.volumeOfLearning += int(unpackDict(
                    modul['M_Arbeitsaufwand_in_Stunden']))
        self.language = sprachen_mapping[modul['M_Lehrsprache']]

        self.mode = Module.generateMode(modul)

        self.duration = int(modul['M_Dauer_in_Semestern']) * 6
        self.targetGroup = "http://data.europa.eu/europass/targetGroup/adults"
        self.entryRequirementsNote = "&lt;![CDATA[Wünschenswerte Voraussetzungen für die Teilnahme an den Lehrveranstaltungen: null;&lt;br/&gt;Verpflichtende Voraussetzungen für die Modulprüfungsanmeldung: Keine Angabe]]&gt;"
        self.literature = unpackDict(
            lehrveranstaltungen['Lehrveranstaltung1']['L1_Literatur'])
        self.enrollment_formalities = "Die Studierenden haben keine besonderen Anmeldeformalitäten zu beachten."
        # !!! Dummy data
        self.validity = fachbereich_validity_mapping[modul['M_Fachbereich']]

    @staticmethod
    def generateMode(modul):
        # mode = "http://data.europa.eu/europass/modeOfLearningAndAssessment/online"
        # if modul['M_Praesenzstunden'] is not None and int(modul['M_Praesenzstunden']) > 0:
        #     if modul['M_Selbststudiumsstunden'] is not None and int(modul['M_Selbststudiumsstunden']) > 0:
        #         mode = "http://data.europa.eu/europass/modeOfLearningAndAssessment/blended"
        #     else:
        #         mode = "http://data.europa.eu/europass/modeOfLearningAndAssessment/presential"

        # return mode

        # blended is the only supported edci value at the moment
        return "http://data.europa.eu/europass/modeOfLearningAndAssessment/blended"

    # returns a string that holds the description of a module based on the "Lehrninhalte"
    # of the corresponding "Lehrveranstaltugen"
    @staticmethod
    def generateDescription(lehrveranstaltungen):
        description = ""
        lehrinhalte = [lehrveranstaltungen['Lehrveranstaltung' + str(index+1)]['L'+str(
            index+1)+'_Lehrinhalte'] for (index, key) in enumerate(lehrveranstaltungen)]
        for i in range(len(lehrinhalte)):
            if len(lehrinhalte) > 1:
                if(lehrveranstaltungen['Lehrveranstaltung' + str(
                        i+1)]['L'+str(i+1)+'_Lehrveranstaltungsname']):
                    description += lehrveranstaltungen['Lehrveranstaltung' + str(
                        i+1)]['L'+str(i+1)+'_Lehrveranstaltungsname'] + ':\n'

            description += unpackDict(lehrinhalte[i])

            if(i < len(lehrinhalte)-1):
                description += '\n'

        return description.strip()

    def generateAwardingOpportunities(self, root):
        awardingOpportunities_node = et.SubElement(
            root, NS5+'awardingOpportunities')
        awardingOpportunity_node = et.SubElement(
            awardingOpportunities_node, NS5+'awardingOpportunity')
        organization_node = et.SubElement(
            awardingOpportunity_node, NS5+'organization')
        organization_node.set('idref', organization['id'])
        location_node = et.SubElement(awardingOpportunity_node, NS5+'location')
        location_node.set("uri", organization['location'])
        startedAtTime_node = et.SubElement(
            awardingOpportunity_node, NS5+'startedAtTime')
        startedAtTime_node.text = "2018-03-31T23:59:59.000Z"

    # Creates xml data
    def build(self, parent, studySection_node):
        # Create Ref in StudySection
        studySection_ref_node = et.SubElement(studySection_node, NS5+'hasPart')
        studySection_ref_node.set('idref', self.full_id)

        # Create modulSpecialization
        root = et.SubElement(parent,
                             NS5+'modulSpecialization')
        root.set('id', self.full_id)

        # Create identifier
        id_node = et.SubElement(root, NS5+'identifier')
        id_node.text = self.mspec_id

        # Create Type-Tag
        type_node = et.SubElement(root, NS5+'type')
        type_node.set(
            'uri', self.mspec_type)

        # Create Title
        title_node = et.SubElement(root, NS5+'title')
        title_node.set('lang', 'de')
        title_node.text = self.mspec_title

        # Create Definition
        definition_node = et.SubElement(root, NS5+'definition')
        definition_text_node = et.SubElement(definition_node, NS5+'text')
        definition_text_node.set('content-type', 'text/plain')
        definition_text_node.set('lang', 'de')
        definition_text_node.text = self.description

        # Create additional note, Literatur
        literature_node = et.SubElement(
            root, NS5+'additionalNote')
        literature_text_node = et.SubElement(literature_node, NS5+'text')
        literature_text_node.set('content-type', "text/plain")
        literature_text_node.set('lang', "de")
        literature_text_node.text = 'Literaturangaben: ' + self.literature

        # Create additional note, enrolement formalities
        formalities_node = et.SubElement(
            root, NS5+'additionalNote')
        formalities_text_node = et.SubElement(formalities_node, NS5+'text')
        formalities_text_node.set('content-type', "text/plain")
        formalities_text_node.set('lang', "de")
        formalities_text_node.text = 'Anmeldeformalitäten: ' + self.enrollment_formalities

        # Create additional note, period of validity
        validity_node = et.SubElement(
            root, NS5+'additionalNote')
        validity_text_node = et.SubElement(validity_node, NS5+'text')
        validity_text_node.set('content-type', "text/plain")
        validity_text_node.set('lang', "de")
        validity_text_node.text = 'Gültigkeit: ' + self.validity

        # Create supplementaryDoc
        supplementaryDoc_node = et.SubElement(root, NS5+'supplementaryDoc')
        supplementaryDoc_node.set(
            'uri', "https://pim.moses.tu-berlin.de/moses/modultransfersystem/bolognamodule/beschreibung/anzeigen.html?number=" + self.module_id + "&amp;version=1")
        subject_node = et.SubElement(supplementaryDoc_node, NS5+'subject')
        subject_node.set(
            'uri', "http://data.europa.eu/esco/qualification-topics#entry-requirements")

        # Create volumeOfLearning tag
        volumeOfLearning_node = et.SubElement(root, NS5+'volumeOfLearning')
        volumeOfLearning_node.text = 'P0Y0M0DT' + \
            str(self.volumeOfLearning) + 'H0M0S'

        # Create hasECTS tag
        ects_node = et.SubElement(root, NS5+'hasECTSCreditPoints')
        ects_node.set(
            'schemeID', "http://data.europa.eu/europass/educationalCreditPointSystem/ects")
        ects_node.text = self.ects

        # Create language tag
        language_node = et.SubElement(root, NS5+'language')
        language_node.set('uri', self.language)

        # Create mode tag
        mode_node = et.SubElement(root, NS5+'mode')
        mode_node.set('uri', self.mode)

        # Create duration tag
        duration_node = et.SubElement(root, NS5+'duration')
        duration_node.text = 'P0Y' + \
            str(self.duration) + 'M0DT0H0M0S'

        # Create targetGroup tag
        target_node = et.SubElement(root, NS5+'targetGroup')
        target_node.set('uri', self.targetGroup)

        # Create entryRequirementsNote
        entry_node = et.SubElement(root, NS5+'entryRequirementsNote')
        entry_text_node = et.SubElement(entry_node, NS5+'text')
        entry_text_node.set('content-type', "text/html")
        entry_text_node.set('lang', "de")
        entry_text_node.text = self.entryRequirementsNote

        # Create reference to LearningOutcome
        learningOutcomes_node = et.SubElement(root, NS5+'learningOutcomes')
        learningOutcome_node = et.SubElement(
            learningOutcomes_node, NS5+'learningOutcome')
        learningOutcome_node.set('idref', self.learningOutcome.full_id)

        # Create assessmentSpecification Reference
        assessmentSpecificationRef_node = et.SubElement(
            root, NS5+'assessmentSpecification')
        assessmentSpecificationRef_node.set(
            'idref', self.learningOutcome.assessmentSpecification.full_id)

        #  Create AwardingOppurtunities
        self.generateAwardingOpportunities(root)

        # Create LearningEvents
        for learningEvent in self.learningEvents:
            ref = et.SubElement(root, NS5+'hasPart')
            ref.set('idref', learningEvent.full_id)
            learningEvent.build(parent)

        # Create LearningOutcome
        self.learningOutcome.build(parent)

        # Create ref to Module
        moduleref_node = et.SubElement(root, NS5+'specializationOf')
        moduleref_node.set('idref', self.module_full_id)

        # Create module tag
        module_root = et.SubElement(parent, NS5+'modul')
        module_root.set('id', self.module_full_id)

        # Create Module-identifier
        module_id_node = et.SubElement(module_root, NS5+'identifier')
        module_id_node.text = self.module_id

        # Create Module-Type-Tag
        module_type_node = et.SubElement(module_root, NS5+'type')
        module_type_node.set(
            'uri', self.module_type)

        # Create Module-Title
        module_title_node = et.SubElement(module_root, NS5+'title')
        module_title_node.set('lang', 'de')
        module_title_node.text = self.module_title


class AssessmentSpecification:
    root = None

    # Creates assessmentSpecificationReferences Tag in root only if it dosnt already exist
    @staticmethod
    def getRoot():
        if AssessmentSpecification.root is None:
            AssessmentSpecification.root = et.SubElement(
                root, NS5+'assessmentSpecificationReferences')

        return AssessmentSpecification.root

    @staticmethod
    def generateType(prüfungsleistung):
        type = assessmentType_mapping[prüfungsleistung]
        if type == None:
            type = ''
            print("Value Error (Püfungsleistung): '" + prüfungsleistung + "'")
        return type

    # collects data of assessments of the given modul data
    @staticmethod
    def generateAssessments(xml, id):
        assessments = []
        if xml['Modul']['M_Pruefungsleistung'] == None:
            lehrveranstaltungen = xml['Lehrveranstaltungen']
            for (index, key) in enumerate(lehrveranstaltungen):
                if lehrveranstaltungen[key]['L'+str(index+1)+'_Pruefungsleistung'] != None:
                    assessments.append(
                        {"id": id+'.'+str(index+1), "title": lehrveranstaltungen[key]['L'+str(index+1)+'_Lehrveranstaltungsname'], "type": AssessmentSpecification.generateType(lehrveranstaltungen[key]['L'+str(index+1)+'_Pruefungsleistung']), "language": lehrveranstaltungen[key]['L'+str(index+1)+'_Pruefsprache']})
        else:
            assessments.append(
                {"id": id+'.1', "title": xml['Modul']['M_Modulname'], "type": AssessmentSpecification.generateType(xml['Modul']['M_Pruefungsleistung']), "language": xml['Modul']['M_Pruefsprache']})

        return assessments

    def __init__(self, xml, mspec_id, proveId):
        self.id = mspec_id
        self.full_id = "urn:thl:assessment:spec:" + self.id
        self.proveId = proveId
        self.title = xml['Modul']['M_Modulname']
        self.assessments = AssessmentSpecification.generateAssessments(
            xml, self.full_id)
        if len(self.assessments) == 1:
            self.type = self.assessments[0]['type']
            if self.assessments[0]['language'] is None:
                self.language = "http://publications.europa.eu/resource/authority/language/DEU"
            else:
                self.language = sprachen_mapping[self.assessments[0]['language']]
        else:
            self.type = "http://data.europa.eu/europass/assessmentType/continuousEvaluation"
            self.language = "http://publications.europa.eu/resource/authority/language/DEU"
            for assessment in self.assessments:
                if not assessment['language'] == "Deutsch":
                    self.language = "http://publications.europa.eu/resource/authority/language/ENG"
                    break

    # Creates XML
    def build(self):
        root = et.SubElement(AssessmentSpecification.getRoot(),
                             NS5+'assessmentSpecification')
        root.set('id', self.full_id)
        title_node = et.SubElement(root, NS5+'title')
        title_node.set('lang', 'de')
        title_node.text = self.title
        type_node = et.SubElement(root, NS5+'type')
        type_node.set('uri',  self.type)
        language_node = et.SubElement(root, NS5+'language')
        language_node.set('uri', self.language)
        proves_node = et.SubElement(root, NS5+'proves')
        proves_node.set('idref', self.proveId)

        if len(self.assessments) > 1:
            for assessment in self.assessments:
                hasPart_node = et.SubElement(root, NS5+'hasPart')
                hasPart_node.set('idref', assessment['id'])
                assessment_node = et.SubElement(
                    AssessmentSpecification.getRoot(), NS5+'assessmentSpecification')
                assessment_node.set('id', assessment['id'])
                assessment_title_node = et.SubElement(
                    assessment_node, NS5+'title')
                assessment_title_node.set('lang', 'de')
                assessment_title_node.text = assessment['title']
                assessment_type_node = et.SubElement(
                    assessment_node, NS5+'type')
                assessment_type_node.set(
                    'uri',  assessment['type'])


class LearningOutcome:

    # returns a string that holds the description of a learningOutcome based on the "Lehrnergebnisse"
    # of the corresponding "Lehrveranstaltugen"
    @staticmethod
    def generateDescription(xml):
        description = unpackDict(xml['Modul']['M_Lernergebnisse'])
        if description == "":
            lehrveranstaltungen = xml['Lehrveranstaltungen']
            lernergebnisse = [lehrveranstaltungen['Lehrveranstaltung' + str(index+1)]['L'+str(
                index+1)+'_Lernergebnisse'] for (index, key) in enumerate(lehrveranstaltungen)]
            for i in range(len(lernergebnisse)):
                if len(lernergebnisse) > 1:
                    description += lehrveranstaltungen['Lehrveranstaltung' + str(i+1)]['L'+str(
                        i+1)+'_Lehrveranstaltungsname'] + ':\n'

                description += unpackDict(lernergebnisse[i])

                if(i < len(lernergebnisse)-1):
                    description += '\n'

        return description.strip()

    def __init__(self, xml, mspec_id):
        self.xml = xml
        self.id = mspec_id
        self.full_id = "urn:thl:learningoutcome:" + self.id
        self.prefLabel = xml['Modul']['M_Modulname']
        self.description = LearningOutcome.generateDescription(xml)
        self.assessmentSpecification = AssessmentSpecification(
            xml, mspec_id, self.full_id)

    # Creates XML
    def build(self, parent):
        root = et.SubElement(parent, NS5+'learningOutcome')
        root.set('id', self.full_id)

        prefLabel_node = et.SubElement(root, NS5+'prefLabel')
        prefLabel_node.set('lang', 'de')
        prefLabel_node.text = self.prefLabel

        description_node = et.SubElement(root, NS5+'description')
        description_text_node = et.SubElement(description_node, NS5+'text')
        description_text_node.set('content-type', 'text/plain')
        description_text_node.set('lang', 'de')
        description_text_node.text = self.description

        parent.insert(0, parent[-1])

        self.assessmentSpecification.build()


class LearningEvent:

    def __init__(self, xml, parent_id, index):
        self.xml = xml
        self.id = parent_id + '-' + index
        self.full_id = "urn:thl:learning:spec:" + self.id
        self.title = xml['L' + index + '_Lehrveranstaltungsname']
        self.type = 'http://data.europa.eu/europass/learningOpportunityType/class'
        self.learnActSpec = LearnActSpec(xml, self.id, index)

    # Creates XML
    def build(self, parent):
        self.learnActSpec.build()

        # Create LearningEvent Tag
        root = et.SubElement(parent,
                             NS5+'learningEvent')
        root.set('id', self.full_id)

        # Create Type-Tag
        type_node = et.SubElement(root, NS5+'type')
        type_node.set(
            'uri', self.type)

        # Create Title-Tag
        title_node = et.SubElement(root, NS5+'title')
        title_node.set('lang', 'de')
        title_node.text = self.title

        # Create ref to learningActivitySpecification
        learnActSpec_node = et.SubElement(
            root, NS5+'learningActivitySpecification')
        learnActSpec_node.set('idref', self.learnActSpec.full_id)


class LearnActSpec:
    root = None

    # Creates learningActivitySpecificationReferences Tag in root only if it dosnt already exist
    @staticmethod
    def getRoot():
        if LearnActSpec.root is None:
            LearnActSpec.root = et.SubElement(
                root, NS5+'learningActivitySpecificationReferences')

        return LearnActSpec.root

    def __init__(self, xml, parent_id, index):
        self.xml = xml
        self.id = parent_id
        self.full_id = "urn:thl:learningactivity:spec:" + self.id
        self.title = xml['L' + str(index) + '_Lehrveranstaltungsname']
        if xml['L' + str(index) + '_Lehrveranstaltungsart'] is None:
            self.type = ""
        else:
            self.type = veranstaltungsart_mapping[xml['L' +
                                                      str(index) + '_Lehrveranstaltungsart']]

    def build(self):
        # Create LearningEvent Tag
        root = et.SubElement(LearnActSpec.getRoot(),
                             NS5+'learningActivitySpecification')
        root.set('id', self.full_id)

        # Create Title-Tag
        title_node = et.SubElement(root, NS5+'title')
        title_node.set('lang', 'de')
        title_node.text = self.title

        # Create Type-Tag
        type_node = et.SubElement(root, NS5+'type')
        type_node.set(
            'uri', self.type)


def generateOrganization(root):
    agentRefs_node = et.SubElement(root, NS5+'agentReferences')
    organization_node = et.SubElement(agentRefs_node, NS5+'organization')
    organization_node.set('id', organization['id'])
    registration_node = et.SubElement(organization_node, NS5+'registration')
    registration_node.set('spatialID', organization['location'])
    registration_node.text = organization['registration']
    type_node = et.SubElement(organization_node, NS5+'type')
    type_node.set('uri', organization['type'])
    prefLabel_node = et.SubElement(organization_node, NS5+'prefLabel')
    prefLabel_node.set('lang', 'de')
    prefLabel_node.text = organization['title']
    hasLocation_node = et.SubElement(organization_node, NS5+'hasLocation')
    spatialCode_node = et.SubElement(hasLocation_node, NS5+'spatialCode')
    spatialCode_node.set('uri', organization['location'])


def generateCredentialSubject(parent):
    root = et.SubElement(parent, NS5+'credentialSubject')
    root.set('id', "DUMMY-SUBJECT")
    nationalId_node = et.SubElement(root, NS5+'nationalId')
    nationalId_node.set(
        "spatialID", "http://publications.europa.eu/resource/authority/country/DEU")
    nationalId_node.text = "DUMMY-NATIONALID"
    identifier_node = et.SubElement(root, NS5+'identifier')
    identifier_node.set(
        "spatialID", "http://publications.europa.eu/resource/authority/country/DEU")
    identifier_node.text = "DUMMY-IDENTIFIER"
    fullName_node = et.SubElement(root, NS5+'fullName')
    fullName_node.set("lang", "en")
    fullName_node.text = "DUMMY SUBJECT"
    givenNames_node = et.SubElement(root, NS5+'givenNames')
    givenNames_node.set("lang", "en")
    givenNames_node.text = "DUMMY"
    familyName_node = et.SubElement(root, NS5+'familyName')
    familyName_node.set("lang", "en")
    familyName_node.text = "SUBJECT"
    birth_node = et.SubElement(root, NS5+'dateOfBirth')
    birth_node.text = "2000-10-20Z"
    et.SubElement(root, NS5+'achievements')
    et.SubElement(root, NS5+'activities')
    et.SubElement(root, NS5+'assessments')
    et.SubElement(root, NS5+'entitlements')
    et.SubElement(root, NS5+'awardings')


def generateScoringSchemeRefs(root):
    et.SubElement(root, NS5+'scoringSchemeReferences')


def genereateCredential():
    AssessmentSpecification.root = None
    LearnActSpec.root = None

    # set schema location, id and xsdVersion
    root.set(XSI + 'schemaLocation', SCHEMALOCATION)
    root.set("id", "urn:epass:credential:b576d4a4-c669-458b-ba17-23bd3237e177")
    root.set("xsdVersion", "0.4.0")

    # set attributes of europassCredential (root Tag)
    type_node = et.SubElement(root, NS5+'type')
    type_node.set(
        'uri', "http://data.europa.eu/europass/credentialType/learning")
    issuanceDate_node = et.SubElement(root, NS5+'issuanceDate')
    issuanceDate_node.text = "2021-01-21T16:01:34.979+02:00"
    issuer_node = et.SubElement(root, NS5+'issuer')
    issuer_node.set('idref', organization['id'])
    title_node = et.SubElement(root, NS5+'title')
    title_node.set('lang', 'de')
    title_node.text = xml_in['Modulbeschreibungen']['Modulbeschreibung'][0]['Modul']['M_Studiengang']
    description_node = et.SubElement(root, NS5+'description')
    description_text_node = et.SubElement(description_node, NS5+'text')
    description_text_node.set('content-type', "text/plain")
    description_text_node.set("lang", "de")
    description_text_node.text = "Dies ist der Studiengang " + \
        xml_in['Modulbeschreibungen']['Modulbeschreibung'][0]['Modul']['M_Studiengang'] + " aus dem Fachbereich " + \
        xml_in['Modulbeschreibungen']['Modulbeschreibung'][0]['Modul']['M_Fachbereich'] + "."

    generateCredentialSubject(root)

    # Create LearningSpecificationReferneces
    LearnSpecRef(xml_in['Modulbeschreibungen'], root).build()

    et.SubElement(root, NS5+'entitlementSpecificationReferences')
    et.SubElement(root, NS5+'learningOpportunityReferences')

    # Create Organizations
    generateOrganization(root)

    et.SubElement(root, NS5+'accreditationReferences')

    generateScoringSchemeRefs(root)

    et.SubElement(root, NS5+'semanticFrameworkReferences')
    et.SubElement(root, NS5+'attachmentList')
    et.SubElement(root, NS5+'proof')

    return root


# returns a String of numbers, that is supposed to look like a study proframm id
# the abbreviation of the name of a study programm gets converted
# into the Ascii numbers equivalent
def generateIdFromFilename(filename):
    id = ""
    abbreviation = filename.replace(
        '_Modulbeschreibungen.xml', '').replace('_', '')
    for c in abbreviation:
        id += str(ord(c))

    return id


# Open a file
path = r"./input"

# Generate new XML for every file in the subdirectories of the input folder
with os.scandir(path) as dirs:
    for dir in dirs:
        if os.path.isdir(dir):
            with os.scandir(dir) as subdir:
                for file in subdir:
                    if os.path.isfile(file):
                        filename = file.name
                        output_filename = filename.replace('.xml', '_pim.xml')

                        # Read THL Moduldescriptions and convert them to dictionary
                        xml_in = open(
                            file, 'r', encoding='utf-8').read()
                        xml_in = xmltodict.parse(xml_in)

                        # Generate new XML, setting the root Tag
                        root = et.Element(
                            DEFAULT + 'europassCredential', nsmap=NSMAP)
                        genereateCredential()

                        # Write xml to new file in output folder
                        tree = et.ElementTree(root)
                        tree.write('output/' + output_filename, pretty_print=True,
                                   xml_declaration=True, encoding="utf-8")
