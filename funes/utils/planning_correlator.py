
tags_time_tagged  = ["Mission", "PlanValidityTimeWindow", "Satellite", "Operation"]
tags_task_plan_acq = ["satellite_id", "station_id", "task_name", "macro_activity_id", "priority", "acquisition_id"]
import xml.etree.ElementTree as ET
import pandas as pd
import json


def extract_op_id(path_time_tagged):
    op_id = []
    for event, elem in ET.iterparse(path_time_tagged, events=('end',)):
        if elem.tag == "OperationId":
                op_id.append(elem.text)
    return op_id
     
def correlate_planning_data(task_plan_Acq, time_tagged_data, cmp_data):
    """
    Correlate task_plan_Acq with time tagged and cmp data to have a merge between acquisition data and planning data, in order to have a complete picture of the situation and be able to make more informed reasoning.
    
    Args:
        task_plan_Acq: The acquisition task plan data.
        time_tagged_data: The time tagged data.
        cmp_data: The cmp data.

    Returns:
        A merged dataset that combines information from task_plan_Acq, time_tagged_data, and cmp_data, providing a comprehensive view of the planning and acquisition context.
    """


    plan_complete = ET.Element("plan_complete")

    task_plan_acq = pd.read_csv(task_plan_Acq)
    op_ids = extract_op_id(time_tagged_data)
    task_plan_acq = task_plan_acq[tags_task_plan_acq]
    task_plan_acq['macro_activity_id'] = task_plan_acq['macro_activity_id'].astype(str)
    task_plan_acq = task_plan_acq[task_plan_acq['macro_activity_id'].isin(op_ids)]
    
    xml = XMLPlanningCleaner()
    time_tagged_plan = xml.xml_plan_filter(time_tagged_data, tags_time_tagged)
    print("TIME TAGGED DATA: \n", xml.get_text_from_xml(time_tagged_plan), "\n\n")

class XMLPlanningCleaner:
    def xml_plan_filter(self, path, tags, day=None, limit=9999999999):
        plan_cleaned = ET.Element("plan_cleaned")
        cont = 0

        for event, elem in ET.iterparse(path, events=('end',)):
            if elem.tag in tags:

                if elem.tag == "Operation":
                    op_el = ET.Element("Operation")
                    op_el.append(ET.Element("OperationSerialNumber", value=elem.findtext("OperationSerialNumber").split(".")[0]))
                    actions = elem.findall("Action")
                    if len(actions) >= 1:
                        # salva prime due e ultime due
                       
                        first_action = actions[0].findtext("TelecommandTime/Value").split(".")[0]
                        last_action = actions[-1].findtext("TelecommandTime/Value").split(".")[0]

                        if day and (first_action[:10] != day ):
                            continue  # Skip this operation if it doesn't match the specified day

                        # riaggiungi solo start e end
                        op_el.append(ET.Element("OpStart", value=first_action))
                        op_el.append(ET.Element("OpEnd", value=last_action))
                    plan_cleaned.append(op_el)

                # aggiungi l’elemento filtrato
                else: plan_cleaned.append(elem)
                cont += 1


            if cont >= limit:
                break
        
        self.indent(plan_cleaned)
        return plan_cleaned
    
    def indent(self, elem, level=0):
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            for child in elem:
                self.indent(child, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if not elem.tail or not elem.tail.strip():
                elem.tail = i

    def get_text_from_xml(self, plan):
        return ET.tostring(plan, encoding='unicode')




cols_task_plan_acq = ["is_emergency_task", "id", "start_time", "stop_time", 'passage_id', 'satellite_id', 'station_id', 'task_status', 'task_type', 'task_name',  'priority']

def get_csv_task_plan(path, date_start=None, date_end=None, satellite_id=None, station_id=None, acquisition_filter = False):
    df = pd.read_csv(path)
    df = df[cols_task_plan_acq]
    df["start_time"] = pd.to_datetime(df["start_time"], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce').dt.floor("s")
    df["stop_time"] = pd.to_datetime(df["stop_time"], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce').dt.floor("s")
    if date_start:
        df = df[df['start_time'] >= date_start]
    if date_end:
        df = df[df['stop_time'] <= date_end]
    if satellite_id:
        df = df[df['satellite_id'] == satellite_id]
    if station_id:
        df = df[df['station_id'] == station_id]
    if acquisition_filter:
        df = df[df['task_type'] == "ACQ"]
    df = json.dumps(df.to_dict(orient="records"), default=str, separators=(",", ":")) 
    return df
          

if __name__ == '__main__':
    # Example usage of the correlate_planning_data function
    task_plan_Acq = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_ACQ_20260317.csv"
    time_tagged_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\IME01_24032026095915680_TIME_TAGGED.xml"
    cmp_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_PL_PPF_CMP_20260311T133622_20260318T000000_20260320T000000_DEV_001.xml"
    task_path = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_NOMINAL_20260318.csv"
    
    df = get_csv_task_plan(task_path, acquisition_filter=True)
    df = json.dumps(df.to_dict(orient="records"), default=str, separators=(",", ":"))  # Convert DataFrame to JSON string, handling datetime serialization
    print(df)