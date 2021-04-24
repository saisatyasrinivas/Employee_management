from py2neo import Graph
import sys
import os

# class HelloWorldExample:

#     def __init__(self, uri, user, password):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self.driver.close()

#     def print_greeting(self, message):
#         with self.driver.session() as session:
#             greeting = session.write_transaction(self._create_and_return_greeting, message)
#             print(greeting)

#     @staticmethod
#     def _create_and_return_greeting(tx, message):
#         result = tx.run("CREATE (a:Greeting) "
#                         "SET a.message = $message "
#                         "RETURN a.message + ', from node ' + id(a)", message=message)
#         return result.single()[0]

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
    # 3 step try to import one file into neo4j using https://stackoverflow.com/questions/59795828/insert-pandas-dataframe-into-neo4j
    # 4 reserach on how to establish relationships?
    # 5 establish relation ships between nodes



if __name__ == "__main__":
    main()
    # greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "2426")
    # greeter.print_greeting("hello, world")
    # greeter.close()