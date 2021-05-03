from flask import Flask, request,jsonify
from flask_cors import CORS
from py2neo import Graph


app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
graph = Graph("bolt://localhost:7687", user="neo4j", password="r123")
# tx = graph.begin()

@app.route('/company/departments/', methods=['GET'])
def departments():
    query= graph.run("""MATCH (dept:Department) RETURN dept.Number as departments""").data()
    output = []
    for i in query:
        output.append(int(i["departments"]))
    result = {"departments":output}
    return jsonify(result)
@app.route('/company/employees/', methods=['GET'])
def employees():
    query= graph.run("""MATCH (emp:Employee) RETURN emp.Ssn as employees""").data()
    output = []
    for i in query:
        output.append(i["employees"])
    result = {"employees":output}
    return jsonify(result)
@app.route('/company/projects/', methods=['GET'])
def projects():
    query= graph.run("""MATCH (proj:Project) RETURN proj.Number as projects""").data()
    output = []
    for i in query:
        output.append(int(i["projects"]))
    result = {"projects":output}
    return jsonify(result)
@app.route('/company/cities/', methods=['GET'])
def cities():
    query = graph.run("""MATCH (l:Project) with collect(l.Location) as locationp MATCH (d:Department) return locationp,collect(d.Location)""").data()
    raw_data = query[0]
    dept_locations = raw_data["collect(d.Location)"]
    revised = []
    for i in dept_locations:
        for j in i:
            revised.append(j)
    project_locations = raw_data["locationp"]
    locations = list(set(project_locations+revised))
    final_output = {"cities":locations}
    return final_output
@app.route('/company/supervisees/<string:ssn>/', methods=['GET'])
def supervisees_ssn(ssn):
    query= graph.run("""MATCH (s:Employee {Ssn:$ssn})-[:supervisor*1..3]->(su) return collect(su.Ssn) as employees""", parameters = {"ssn":ssn}).data()
    return jsonify(query[0])
@app.route('/company/department/<int:dno>/', methods=['GET'])
def department_dno(dno):
    query= graph.run("""match (d:Department {Number:$dno}) 
                        with d 
                        optional match (d)-[:controls]->(project) 
                        with d,collect(project) as controlled_project 
                        optional match (d)-[:employs]->(employee) 
                        with d,controlled_project,collect(employee.Ssn) as emp_ssn 
                        optional match (d)-[r:managed_by]->(manager) 
                        return d,controlled_project,emp_ssn,manager,r.StartDate """,parameters={"dno":dno}).data()
    raw_data = query[0]
    controlled_project = []
    for i in raw_data["controlled_project"]:
        project = {
            "pname":i["Name"],
            "pnumber":i["Number"]
        }
        controlled_project.append(project)
    final_output = {
        "controlled_projects":controlled_project,
        "dname":raw_data["d"]["Name"],
        "employees":raw_data["emp_ssn"],
        "locations":raw_data["d"]["Location"],
        "manager":raw_data["manager"]["Fname"]+raw_data["manager"]["Minit"]+raw_data["manager"]["Lname"],
        "manager_start_date":raw_data["r.StartDate"],
        "mgrssn":raw_data["manager"]["Ssn"]
    }
    return final_output
@app.route('/company/employee/<string:ssn>/', methods=['GET'])
def employee_ssn(ssn):
    if ssn == "null":
        return ""
    query= graph.run("""MATCH (e:Employee {Ssn:$ssn})
                        WITH e
                        OPTIONAL MATCH(e)-[:dependent]->(dep)
                        with e,collect(dep) as dependents 
                        OPTIONAL MATCH (e)-[:manages]->(manages) 
                        WITH e,dependents,manages 
                        OPTIONAL MATCH (e)-[r:works_on]->(project) 
                        WITH e,dependents,manages,collect(project) as projects,collect(r.Hours) as working 
                        OPTIONAL MATCH (e)-[:supervisor]->(s) 
                        WITH e,dependents,manages,projects,working,collect(s.Ssn) as supervisees 
                        OPTIONAL MATCH (e)-[:supervisee]->(su:Employee) 
                        WITH e,dependents,manages,projects,supervisees,working,su.Ssn as supervisor 
                        OPTIONAL MATCH (e)-[:works_for]->(department) 
                        return e,dependents,manages,projects,working,supervisees,supervisor,department.Name as department_name, department.Number as department_number""", parameters= {"ssn":ssn}).data()
    raw_data = query[0]
    manage = {
        "dname": "NA",
        "dnumber": "NA"
    }
    if raw_data["manages"]:
        manage = {
            "dname":raw_data["manages"]["Name"],
            "dnumber":raw_data["manages"]["Name"]
        }
    dependent = []
    project = []
    for i in raw_data["dependents"]:
        depend =  {
        "bdate": i["BirthDate"],
        "dname": i["Name"],
        "gender": i["Sex"],
        "relationship": i["Relationship"]
        }
        dependent.append(depend)
    for i,j in zip(raw_data["projects"],raw_data['working']):
        prooo = {
            "pname": i["Name"],
            "pnumber": i["Number"],
            "hours": j
        }
        project.append(prooo)

    final_output = {"address":raw_data["e"]["Address"],
                    "bdate"  :raw_data["e"]["DOB"],
                    "department_name":raw_data["department_name"],
                    "department_number":raw_data["department_number"],
                    "dependents":dependent,
                    "fname":raw_data["e"]["Fname"],
                    "gender":raw_data["e"]["Gender"],
                    "lname":raw_data["e"]["Lname"],
                    "manages": manage,
                    "minit": raw_data["e"]["Minit"],
                    "projects":project,
                    "salary":raw_data["e"]["Salary"],
                    "supervisees":raw_data["supervisees"],
                    "supervisor":raw_data["supervisor"]
                     }
    return final_output
@app.route('/company/project/<int:pno>/', methods=['GET'])
def project_pno(pno):
    query  = graph.run("""MATCH (p:Project {Number:$number}) with p optional match (p)-[:controlled_by]->(depart) with p,depart optional match (p)-[r:worker]->(employee)-[:works_for]-(department) return p,depart,collect(employee) as employees,collect(r.Hours) as hours,collect(department) as department_""",parameters={"number":int(pno)}).data()
    raw_data = query[0]

    output = {
        "controlling_dname": raw_data['depart']['Name'],
        "controlling_dnumber": raw_data['depart']['Number'],
    }

    dep_hours = {}

    a = raw_data["employees"]
    b = raw_data["hours"]
    c = raw_data["department_"]
    for i in range(len(a)):
        dep_name = c[i]['Name']
        if dep_name in dep_hours:
            dep_hours[dep_name] = dep_hours[dep_name] + int(float(b[i]))
        else:
            dep_hours[dep_name] = int(float(b[i]))
    
    output["dept_hours"] = dep_hours
    output["employees"] = [i["Ssn"] for i in a]
    count = 0
    for j in dep_hours:
        count += dep_hours[j]

    output["person_hours"] = count
    output["pname"] = raw_data['p']['Name']
    output["plocation"] = raw_data['p']['Location']
    return jsonify(output)
@app.route('/company/dcities/', methods=['GET'])
def dcities():
    query = graph.run("""MATCH (d:Department) return collect(d.Location) as dept_location""").data()
    raw_data = query[0]
    dept_locations = raw_data["dept_location"]
    revised = []
    for i in dept_locations:
        for j in i:
            revised.append(j)
    final_output = {"cities":revised}
    return final_output
@app.route('/company/pcities/', methods=['GET'])
def pcities():
    query = graph.run("""MATCH (l:Project) with collect(l.Location) as locationp  return locationp""").data()
    raw_data = query[0]
    project_location = raw_data["locationp"]
    final_output = {"cities":project_location}
    return final_output
@app.route('/company/projects/<string:cty>/', methods=['GET'])
def projects_cty(cty):
    query = graph.run("""Match (p:Project {Location:$location}) return collect(p) as proj""",parameters={"location":cty}).data()
    raw_data = query[0]
    projects = []
    for i in raw_data["proj"]:
        project = {
            "pname": i["Name"],
            "pnumber": i["Number"]
        }
        projects.append(project)
    final_output = {"projects":projects}
    return final_output
@app.route('/company/departments/<string:cty>/', methods=['GET'])
def departments_cty(cty):
    query = graph.run("""Match (p:Department) with p where any(p1 in p.Location where p1 = "{}") return collect(p) as departments""".format(cty)).data()
    raw_data = query[0]
    department = []
    for i in raw_data["departments"]:
        depart = {
            "dname": i["Name"],
            "dnumber": i["Number"]
        }
        department.append(depart)
    final_output = {"departments":department}
    return final_output

app.run()