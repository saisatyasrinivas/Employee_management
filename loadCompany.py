from py2neo import Graph
import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Please enter the directory name")
        print("Usage: python loadCompany.py [data]")
        os._exit(-1)
    directoryName = sys.argv[1]
    if not os.path.isdir(directoryName):
        print("Please enter a valid directory name")
        exit()
    list_of_files = ['DEPENDENTS.dat', 'DEPARTMENTS.dat', 'DEPT_LOCATIONS.dat','EMPLOYEES.dat','PROJECTS.dat','WORKS_ON.dat']

    list_of_files_directory = os.listdir(directoryName)
    for i in list_of_files:
        if i not in list_of_files_directory:
            print("The directory you have provided doesn't contain [{}] the required file".format(i))
    graph = Graph("bolt://localhost:7687", user="neo4j", password="2426")
    tx = graph.begin()
    
    # Departments table
    with open('./data/DEPARTMENTS.dat') as f:
        data = f.readlines()
    data = [i.strip().split(':') for i in data]
    for l in data:
        tx.evaluate('''
        MERGE (a:Department {Name:$dept_name, Number:$dept_no})
        MERGE (b:Employee {Ssn:$mssn})
        MERGE (b)-[r:manages {StartDate:$mstart}]->(a)
        MERGE (a)-[r1:managed_by {StartDate:$mstart}]->(b)
        MERGE (a)-[r2:employs]->(b)
        MERGE (b)-[r3:works_for]->(a)
        ''', parameters = {'dept_name': l[0], 'dept_no': int(l[1]), 'mssn': l[2], 'mstart': l[3]})

    with open('./data/PROJECTS.dat') as f:
        data = f.readlines()
    data = [i.strip().split(':') for i in data]
    for l in data:
        tx.evaluate('''
        MATCH (dept:Department {Number:$proj_dno})
        MERGE (a:Project {Name:$proj_name, Number:$proj_no, Location:$proj_location})
        MERGE (dept)-[r:controls]->(a)
        MERGE (a)-[r1:controlled_by]->(dept)
        
                ''', parameters = {'proj_dno': int(l[3]), 'proj_name': l[0], 'proj_no': l[1], 'proj_location': l[2]})


    with open('./data/EMPLOYEES.dat') as f:
        data = f.readlines()
    data = [i.strip().split(':') for i in data]
    for l in data:
        tx.evaluate('''
        MATCH (a:Department {Number:$works_for})
        MATCH (p:Employee)
        MERGE (a)-[r:employs]->(p)
        MERGE (p)-[r1:works_for]->(a)
        SET p += {Fname:$first_name, Minit:$middle_name, Lname:$last_name, Ssn:$ssn, DOB:$dob, Address:$address, Gender:$gender, Salary:$salary}
                ''', parameters = {'first_name': l[0], 'middle_name': l[1], 'last_name': l[2], 'ssn': l[3], 'dob': l[4], 'address': l[5], 'gender': l[6], 'salary': l[7], 'works_for':l[9]})

    
    tx.commit()

    # 3 step try to import one file into neo4j using https://stackoverflow.com/questions/59795828/insert-pandas-dataframe-into-neo4j
    # 4 reserach on how to establish relationships?
    # 5 establish relation ships between nodes



if __name__ == "__main__":
    main()

#MATCH (dept:Department {dept_no:$proj_dno}) MERGE (dept)-[r:controls]->(a)
       # MERGE (a)-[r1:controlled_by]->(dept)