MATCH (p:Project {Location:"Stafford"})-[:controlled_by]->(d)-[:managed_by]->(m) 
RETURN p.Number as PROJECT_NUMBER
        ,d.Number as DEPT_NUMBER
        ,m.Lname as MANAGER_LNAME
        ,m.Address as MANAGER_ADDRESS
        ,m.DOB as MANAGER_DOB