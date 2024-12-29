import pyodbc
from test_api_openai import analise
import json

conn_str = ""

while True:
    output_data = []
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            query = """SELECT TOP 10 ID, Damaged, Country_Of_Origin, Description
                        FROM [dbo].[Car_Offers_Sample]
                        WHERE Description IS NOT NULL and flag1 is null
                        ORDER BY NEWID();""" 
                        
            cursor.execute(query)
            query_output = cursor.fetchall()
            output_data = query_output

    data_update = []
    for i in output_data:

        analized_data = analise(i[3])
        response_dict = json.loads(analized_data)
        damaged = i[1]
        country = i[2]
        correctness = 1

        if response_dict["Import_Country"] == "USA":response_dict["Import_Country"] = "Stany Zjednoczone"
        if response_dict["Import_Country"] == "Niemiec":response_dict["Import_Country"] = "Niemcy"
        if response_dict["Import_Country"] == "null":response_dict["Import_Country"] = ''
        if response_dict["Running"] == "null":response_dict["Running"] = ''
        if response_dict["Damaged"] == "null":response_dict["Damaged"] = ''
        if response_dict["Damaged"] == {}:response_dict["Damaged"] = ''
        if response_dict["Running"] == {}:response_dict["Running"] = ''


        #print(f" {i[0]} Stan opisany: {i[1]}, {i[2]} Stan po analizie: {response_dict}")

        if i[1] == None: damaged = response_dict["Damaged"]
        elif i[1] != response_dict["Damaged"] and response_dict["Damaged"] != None: correctness = 0

        if i[2] == None: country = response_dict["Import_Country"]
        elif i[2] != response_dict["Import_Country"] and response_dict["Import_Country"] != None: correctness = 0

        data_update.append([i[0], damaged, response_dict["Running"], country])
        #print(data_update[-1])

        evidence_json = {'id': i[0],
                        'scraped': {'Damaged': i[1], 'Import_Country': i[2]},
                            'ai': {'Damaged': response_dict["Damaged"], 'Import_Country': response_dict["Import_Country"]},
                            'correctness': correctness}
        
        with open('ai_test.json', 'r') as file:
            data = json.load(file)
            data.append(evidence_json)

        with open('ai_test.json', 'w') as file:
            json.dump(data, file, indent=4)
        
    #print(data_update)
    case_kolumna0 = " ".join([f"WHEN {id} THEN 'True'" for id, _, _, _ in data_update])
    case_kolumna1 = " ".join([f"WHEN {id} THEN '{value1}'" for id, value1, _, _ in data_update])
    case_kolumna2 = " ".join([f"WHEN {id} THEN '{value2}'" for id, _, value2, _ in data_update])
    case_kolumna3 = " ".join([f"WHEN {id} THEN '{value3}'" for id, _, _, value3 in data_update])

    ids = ", ".join([str(id) for id, _, _, _ in data_update])

    query = f"""
    UPDATE [dbo].[Car_Offers_Sample]
    SET 
        Damaged = CASE id
            {case_kolumna1}
        END,
        flag1 = CASE id
            {case_kolumna0}
        END,
        Running = CASE id
            {case_kolumna2}
        END,
        Country_Of_origin = CASE id
            {case_kolumna3}
        END
    WHERE id IN ({ids});
    """

    
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:       
            print(query)                 
            cursor.execute(query)

    break