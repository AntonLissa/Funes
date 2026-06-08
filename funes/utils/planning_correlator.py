
tags_time_tagged  = ["Mission", "PlanValidityTimeWindow", "Satellite", "Operation"]
tags_task_plan_acq = ["satellite_id", "station_id", "task_name", "macro_activity_id", "priority", "acquisition_id"]
import xml.etree.ElementTree as ET
import numpy as np
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

def get_csv_task_plan(path, date_start=None, date_end=None, satellite_id=None, station_id=None, acquisition_filter = False, station_filter = False):
    df = pd.read_csv(path)
    df = df[cols_task_plan_acq]
    df["start_time"] = pd.to_datetime(df["start_time"], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce').dt.floor("s")
    df["stop_time"] = pd.to_datetime(df["stop_time"], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce').dt.floor("s")
    date_end = pd.to_datetime(date_end) + pd.Timedelta(days=1)

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
    if station_filter:
        df = df[df['station_id'].notna()]
    df = json.dumps(df.to_dict(orient="records"), default=str, separators=(",", ":")) 
    return df

def get_passages_from_xml(
    path,
    date_start=None,
    date_end=None,
    satellite_id=None,
    station_id=None
):
    df = pd.read_csv(path)

    # tieni solo colonne utili
    df = df[cols_task_plan_acq].copy()

    # datetime seri
    df["start_time"] = pd.to_datetime(
        df["start_time"],
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce"
    ).dt.floor("s")

    df["stop_time"] = pd.to_datetime(
        df["stop_time"],
        format="%Y-%m-%d %H:%M:%S.%f",
        errors="coerce"
    ).dt.floor("s")

    # --- FILTRI ---
    if date_start is not None:
        date_start = pd.to_datetime(date_start)
        df = df[df["stop_time"] >= date_start]  # overlap intelligente

    if date_end is not None:
        date_end = pd.to_datetime(date_end) + pd.Timedelta(days=1)
        df = df[df["start_time"] <= date_end]

    if satellite_id is not None:
        df = df[df["satellite_id"] == satellite_id]

    if station_id is not None:
        df = df[df["station_id"] == station_id]

    # ordina
    df = df.sort_values(
        ["satellite_id", "station_id", "passage_id", "start_time"]
    )

    # --- STEP 1: segmentazione temporale ---
    df["gap"] = (
        df.groupby(["satellite_id", "station_id", "passage_id"])["start_time"]
        .diff()
        .gt(pd.Timedelta(seconds=600))
    )

    df["block_id"] = (
        df.groupby(["satellite_id", "station_id", "passage_id"])["gap"]
        .cumsum()
    )

    # --- STEP 2: blocchi ---
    blocks = (
        df.groupby(
            ["satellite_id", "station_id", "passage_id", "block_id"]
        )
        .agg(
            block_start=("start_time", "min"),
            block_end=("stop_time", "max"),
            tasks=("task_name", list),
        )
        .reset_index()
    )

    # --- STEP 3: passaggi ---
    passages = (
        blocks.groupby(["satellite_id", "station_id", "passage_id"])
        .agg(
            start_time=("block_start", "min"),
            end_time=("block_end", "max"),
            operations=("tasks", list),
        )
        .reset_index()
    )

    return passages_df_to_llm_json(passages)

def passages_df_to_llm_json(passages_df):
    passages = []

    for _, row in passages_df.iterrows():

        # costruzione fasi
        phases = []
        for i, block in enumerate(row["operations"]):
            phases.append({
                "phase_id": i,
                "tasks": block
            })

        passage = {
            "passage_id": row["passage_id"],
            "satellite": row["satellite_id"],
            "station": row["station_id"],
            "start": row["start_time"].isoformat(),
            "end": row["end_time"].isoformat(),
            "phases": phases
        }

        passages.append(passage)

    return json.dumps({"passages": passages}, indent=2)


def get_soe_from_xml(path, date_start=None, date_end=None):
    tree = ET.parse(path)
    root = tree.getroot()
    soe_data = []
    for event, elem in ET.iterparse(path, events=('end',)):
        if elem.tag == "data":
            for child in elem:
                #print(f"Tag: {child.tag}")
                for subchild in child:
                    #  print(f"  Subtag: {subchild.tag}, Value: {subchild.text}")
                    if subchild.tag == "EPOCH":
                        subchild_date = pd.to_datetime(subchild.text)
                        if date_start and subchild_date < pd.to_datetime(date_start):
                            continue
                        if date_end and subchild_date > pd.to_datetime(date_end):
                            continue
                        soe_data.append({
                            "event": child.tag,
                            "time": subchild.text 
                        })
    return json.dumps(soe_data, indent=2)






if __name__ == '__main__':
    # Example usage of the correlate_planning_data function
    task_plan_Acq = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_ACQ_20260317.csv"
    time_tagged_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\IME01_24032026095915680_TIME_TAGGED.xml"
    cmp_data = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data examples\planning example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\INPUT\IME01_PL_PPF_CMP_20260311T133622_20260318T000000_20260320T000000_DEV_001.xml"
    task_path = r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\planning_example\REGRESSION-TEST-20260324\REGRESSION-TEST-20260324\PLANNING\OUTPUT\TASK_PLAN_NOMINAL_20260318.csv"
        
    #df = get_csv_task_plan(task_path, date_start="2026-03-15 16:50:00", date_end="2026-03-30 18:00:00", acquisition_filter=False, station_filter=True)
    
    passages = get_passages_from_xml(task_path,  date_start="2026-03-15 11:00:00", date_end="2026-03-18 12:00:00")
    print(passages)

    soe = get_soe_from_xml(r"C:\Users\anton\Documents\python projects\FUNES\Funes\data_examples\planning_example\INPUT\IME01_SOE_20260309T131820_020.xml", date_start="2026-01-07 11:00:00", date_end="2026-01-07 12:00:00")
    print(soe)

    tickets = get_tickets()
    print(tickets)