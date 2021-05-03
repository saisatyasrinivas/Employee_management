MATCH (p:Project)-[:controlled_by]->(d:Department{Number:5})
WITH collect(p.Number) as projects
MATCH (e:Employee)-[:works_on]->(q:Project)
WITH collect(q.Number) as projects_2, projects, e
WHERE ALL(projectv_1 in projects WHERE ANY(projectv_2 in projects_2 WHERE projectv_1 = projectv_2))
RETURN e.Ssn as Employee_Ssn, e.Fname+ " "+e.Minit+" "+e.Lname as Name;