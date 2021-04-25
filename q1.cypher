MATCH (d:Department {Name:"Research"})-[:employs]->(e) 
RETURN e.Fname+" "+e.Minit+" "+e.Lname as NAME, e.Address as ADDRESS