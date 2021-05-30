import random 
import json 
from py2neo import Graph, Node, Relationship, cypher


graph = Graph(
    uri="neo4j+s://3670dede.databases.neo4j.io",
    user="neo4j", 
    password="4Pd1FlT3AOHxIlf6AoUKQYN09ajnrBOD7_l7mzO0tow"
    )

temp = dict()

def return_fulfillment(data): 
    intent = data["queryResult"]["intent"]["displayName"]
    choices = []

    if intent == "EmployeeSkill": 
        # Who knows java? 
        skill_name = data["queryResult"]["parameters"]["skills"][0]
        cypher_query = f"MATCH (emp:Employee)-[:POSSESS]->(skill) WHERE skill.skill = '{skill_name}' RETURN (emp);"
        all_employee = graph.run(cypher_query).data()
        employee = random.choice(all_employee)["emp"]
        choices = [
            f"{employee['EmployeeName']} knows {skill_name}", 
            f"{employee['EmployeeName']} is experienced with {skill_name}"
        ]
    elif intent == "ProjectSkill": 
        # Have we worked with python before?
        skill_name = data["queryResult"]["parameters"]["Skill"][0]
        cypher_query = f"MATCH (proj:Project)-[:REQUIRES]->(sk:Skill) WHERE sk.skill =~ '(?i){skill_name}' return (proj)"
        all_project = graph.run(cypher_query).data()
        project = random.choice(all_project)['proj']
        choices = [
            f"{project['ProjectName']} involved some skill with {skill_name}", 
            f"Yes, {project['ProjectName']} had involved personnel with experience in {skill_name}", 
            f"Yes, {skill_name} was used in {project['ProjectName']}"
        ]
    elif intent == "CompanyPeople.Lead": 
        # who was the tech lead in our last project with singtel
        company_name = data["queryResult"]["parameters"]["company"]
        cypher_query = f"MATCH (comp:Company)-[:ORGANISE]->(proj:Project)-[:LEAD_BY]->(emp:Employee) WHERE comp.CompanyName =~ '(?i){company_name}' RETURN emp, proj"
        all_employee_project = graph.run(cypher_query).data()
        employee_project = random.choice(all_employee_project)
        choices = [
            f"The tech lead of {employee_project['proj']['ProjectName']} is {employee_project['emp']['EmployeeName']}", 
            f"{employee_project['emp']['EmployeeName']} leaded the project {employee_project['proj']['ProjectName']}"
        ]
    elif intent == "Company.Industry": 
        # were we involved in the healthcare industry? 
        industry = data["queryResult"]["parameters"]["industry"]
        cypher_query = f"MATCH (comp:Company) WHERE comp.Industry =~ '(?i){industry}' RETURN (comp) "
        all_comp = graph.run(cypher_query).data()
        comp = random.choice(all_comp)["comp"]
        choices = [
            f"Yes, we were affiliated in the {industry} industry with {comp['CompanyName']}", 
            f"Yup, we had some experience with {comp['CompanyName']} who is in the {industry} industry"
        ]
    elif intent == "Company.Region": 
        # Do we have a client from Singapore 
        region = data["queryResult"]["parameters"]["geo-country"]
        cypher_query = f"MATCH (comp:Company) WHERE comp.Region =~ '(?i){region}' RETURN (comp) "
        all_comp = graph.run(cypher_query).data()
        comp = random.choice(all_comp)["comp"]
        choices = [
            f"Yes, {comp['CompanyName']} is located in {region}", 
            f"Yup, {comp['CompanyName']} is from {region} "
        ]
    elif intent =="ProjectPeople.Lead": 
        # who is the techlead of Muscle Fitness management system
        project_name = data["queryResult"]["parameters"]["system-name"]
        cypher_query = f"match (proj:Project)-[:LEAD_BY]->(e:Employee) where proj.ProjectName =~ '(?i){project_name}' RETURN e"
        all_leader = graph.run(cypher_query).data()
        leader = random.choice(all_leader)["e"]
        choices = [
            f"The tech lead of the project {project_name} is {leader['EmployeeName']}", 
            f"{leader['EmployeeName']} leaded the project {project_name}"
        ]
 
    elif intent == "ProjectSkill.All": 
        # What is used in Berjaya fitness system? 
        project_name = data["queryResult"]["parameters"]["project-name"]
        cypher_query = f"MATCH (proj:Project)-[:REQUIRES]->(sk:Skill) WHERE proj.ProjectName =~ '(?i){project_name}' RETURN (sk)"
        all_skill = graph.run(cypher_query).data()
        all_skill_list = [skill["sk"]['skill'] for skill in all_skill]
        if all_skill_list: 
            choices = [
                f"The skills required in {project_name} is {', '.join(all_skill_list)}"
            ]
        else: 
            return data
    elif intent == "help": 
        # if the user needs help 
        query_examples = [
            "Who knows java?",  # works
            "What projects did we do in the past involved C?", # works  
            "Do you know who is the tech lead of our last project with Singtel?", # works  
            "What is the skills used in Muscle Fitness management system?", # works
            "Did we had any clients from Thailand?" # works
        ]  
        new_data_examples = [
            "Add employee name John Cena", # works 
            "This new project Nestle Grains Management System from Nestle is lead by John Ceasser", 
            "Add new skill Java", # works
            "Make new data for Philip's in Electronics industry in Netherlands" # works
        ]  

        final_output =  f"These are some examples of what you can do : "\
                        f"\n - {query_examples.pop(random.randint(0, len(query_examples)))}"\
                        f"\n - {random.choice(new_data_examples)}"\
                        f"\n - {query_examples.pop(random.randint(0, len(query_examples) - 1))}"\
        
        choices = [final_output]
    elif intent == "NewData.Project": 

        leader_f = data["queryResult"]["parameters"]["leader_fname"]
        leader_l = data["queryResult"]["parameters"]["leader_lname"]
        leader_name = f"{leader_f} {leader_l}"
        company_name = data["queryResult"]["parameters"]["compName"][0]
        project_name = data["queryResult"]["parameters"]["projName"]

        temp["leader_name"] = leader_name
        temp["company_name"] = company_name
        temp["project_name"] = project_name

        return json.dumps(data)

    elif intent == "NewData.Project - contributer - skill": # as of now, doesnt work

        skills: list = data["queryResult"]["parameters"]["skill"]
        names_matrix = [
            data["queryResult"]["outputContexts"][0]["parameters"]["fname"], 
            data["queryResult"]["outputContexts"][0]["parameters"]["lname"]
        ]
        names_tuple = list(zip(*names_matrix))
        names = list(f"{name[0]} {name[1]}" for name in names_tuple)
        
        cypher_query = f"CREATE (p:Project {{ ProjectName: '{temp['project_name']}' }}) "\
                        f"WITH p "\
                        f"MATCH (e:Employee) "\
                        f"WHERE (e.EmployeeName =~ '{temp['leader_name']}') "\
                        f"MERGE (p)-[l:LEADS_BY]->(e) "\
                        f""\
                        f"WITH p MATCH (c:Company) "\
                        f"WHERE (c.CompanyName =~ '{temp['company_name']}') "\
                        f"MERGE (c)-[o:ORGANISE]->(p) "\
                        f""\
                        f"CREATE (n:N {{skill:'{','.join(skills)}'}}) "\
                        f"WITH n "\
                        f"MATCH (p:Project {{ProjectName:'{temp['project_name']}'}}) "\
                        f"UNWIND split(n.skill, ',') AS SKILL "\
                        f"MERGE (s:Skill {{skill: SKILL}}) "\
                        f"MERGE (p)-[r:REQUIRES]->(s) "\
                        f""\
                        f"CREATE (m:M {{emp:'{','.join(names)}'}}) "\
                        f"WITH m "\
                        f"MATCH (p:Project {{ProjectName:'{temp['project_name']}'}}) "\
                        f"UNWIND split(m.emp, ',') AS EMP "\
                        f"MERGE (e:Employee {{EmployeeName: EMP}}) "\
                        f"MERGE (e)-[i:INVOLVE_IN]->(p) "\
                        f"DELETE n, m"
        
        graph.run(cypher_query)

        output = [
            "Success!"
        ]
    elif intent == "NewData.Company": 
        new_company_name = data["queryResult"]["parameters"]["compName"]
        new_company_industry = data["queryResult"]["parameters"]["industry"]
        new_company_region  = data["queryResult"]["parameters"]["region"]["country"]
        cypher_query_check = f"MATCH (c:Company) WHERE c.CompanyName =~ '(?i){new_company_name}' RETURN c"
        exist = len(list(graph.run(cypher_query_check))) > 1
        
        if not exist: 
            cypher_query = f"MERGE (c:Company {{compName: '{new_company_name}', industry: '{new_company_industry}', region: '{new_company_region}'}})"
            graph.run(cypher_query)
            choices = [
                "Created new company entry!", 
                f"Success! {new_company_name} created."
            ]
        else: 
            choices = [
                "This entry already exist."
            ]
    elif intent == "NewData.Skill":
        new_skill = data["queryResult"]["parameters"]["skill"]
        cypher_query_check = f"MATCH (s:Skill) WHERE s.skill =~ '(?i){new_skill}' RETURN s"
        exist = len(list(graph.run(cypher_query_check))) > 0 

        if not exist: 
            cypher_query = f"MERGE (s:Skill {{skill: '{new_skill}'}})"
            graph.run(cypher_query)
            choices = [
                f"{new_skill} have been added!", 
                f"New skill acquired!", 
                f"Mastery level increase!"
            ]
        else: 
            choices = [
                f"Skill already exist!", 
                f"Existing skills cannot be added again. :("
            ] 

    elif intent == "NewData.Employee - skill": 
        first_name = data["queryResult"]["outputContexts"][0]["parameters"]["emp_fame"]
        last_name = data["queryResult"]["outputContexts"][0]["parameters"]["emp_lname"]
        new_employee_name = f"{first_name} {last_name}"
        skills:list = data["queryResult"]["parameters"]["skill"]
        cypher_query_check = f"MATCH (e:Employee) WHERE e.EmployeeName =~ '(?i){new_employee_name}' RETURN e"
        exist = len(list(graph.run(cypher_query_check))) > 0

        if not exist: 
            # cypher_query = f"CREATE (e:Employee {{EmployeeName:'{new_employee_name}'}}) "\
            #                 f"CREATE (n:N {{skill:'{','.join(skills)}'}}) "\
            #                 f"WITH n "\
            #                 f"UNWIND split(n.skill, ',') AS SKILL "\
            #                 f"MERGE (s:Skill {{skill: SKILL}}) "\
            #                 f"MERGE (e)-[:POSSESS]->(s) "\
            #                 f"DELETE n"
            cyphers = []
            cyphers.append(f"merge (e:Employee {{EmployeeName:'{new_employee_name}'}});")
            for skill in skills: 
                cyphers.append(f"match (sk:Skill), (ee:Employee) where sk.skill =~ '(?i){skill}' AND ee.EmployeeName =~ '(?i){new_employee_name}' merge (ee)-[:POSSESS]->(sk);")
            for cy in cyphers: 
                graph.run(cy)
            choices = [
                f"{new_employee_name} has joined your party!", 
                f"You've got a new character! Welcome {new_employee_name} to the party!"
            ]
        else: 
            choices = [
                f"Warning! {new_employee_name} is already in the party!", 
                f"Employee was already in the team..."
            ]
    elif intent == "testCardResponse": # only for testing purposes
        custom_card = {
                        "fulfillmentMessages": [
                            {
                            "card": {
                                "title": "LMAO card",
                                "subtitle": "ayeee",
                                "imageUri": "https://cdn.discordapp.com/attachments/846742521983664128/848250432127893565/unknown.png",
                                "buttons": [
                                {
                                    "text": "button text",
                                    "postback": "https://example.com/path/for/end-user/to/follow"
                                }
                                ]
                            }
                            }
                        ]
                        }
        return json.dumps(custom_card)

    else: 
        return data
    

    if choices: 
        output = {
            'fulfillmentText' : random.choice(choices), 
            'source' : 'webhookdata'
        }
        return json.dumps(output)
