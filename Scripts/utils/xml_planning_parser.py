import xml.etree.ElementTree as ET
import os

'''
DATI UTILI:
- mission
- satellite schedule: 
    - satellite
    - operation :[]
'''


class XMLPlanningCleaner:
    def xml_plan_filter(self, path, tags, limit = 9999999999):
        plan_cleaned = ET.Element("plan_cleaned")
        cont = 0
        for event, elem in ET.iterparse(path, events=('end',)):
            if elem.tag in tags:
                plan_cleaned.append(elem)
                cont += 1
            
            if cont >= limit:
                break

        return plan_cleaned

    def get_text_from_xml(self, plan):
        return ET.tostring(plan, encoding='unicode')


if __name__ == '__main__':
    xml_cleaner = XMLPlanningCleaner()
    path = "C:\\Users\\anton\\Documents\\python projects\\FUNES\\Funes\\data examples\\planning example\\IME01_10022026152801829_TIME_TAGGED.xml"

    plan = xml_cleaner.xml_plan_filter(path, ['Mission', 'PlanValidityTimeWindow', 'Satellite', 'Action'], 5)
    print(xml_cleaner.get_text_from_xml(plan))




