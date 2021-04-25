MATCH (e:Employee)-[:dependent]->(de) 
WITH e,count(*) as dep_count 
WHERE dep_count>=2 
RETURN e.Fname+" "+e.Minit+" "+e.Lname as NAME