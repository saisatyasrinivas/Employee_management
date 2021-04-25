MATCH (e:Employee)-[:manages]->(de) 
WITH e 
MATCH (e)-[:dependent]->(d) 
WITH e,count(*) as dep_count 
WHERE dep_count>=1 
RETURN e.Fname+" "+e.Minit+" "+e.Lname as NAME