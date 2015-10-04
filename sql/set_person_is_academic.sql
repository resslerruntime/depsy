select * from person limit 100

select count(*) from person
-- 64k

select count(*) from person where name is not null
-- 56k

select count(*) from person where github_about ? 'id'
-- 45k

select * from person where github_about->>'bio' != 'null'
-- only 704, seems like mostly orgs

select * from person where github_about->>'company' != 'null'
-- 15k

select * from person where github_login = 'kennethreitz'

-- tried and discarded because of few results or poor precision: 
-- lab, school, professor, student, phd, doctoral	






-- setting academics, using same finding algorithm as above:
update person set is_academic = false

update person set is_academic = true
	where false  -- just makes it easier to comment stuff in and out
	
	-- 1278
	or github_about->>'company' ilike '%universi%' 
	or github_about->>'bio' ilike '%universi%' 
	or name ilike '%universi%'
	
	-- 209
	or github_about->>'company' ilike '%scien%' 
	or github_about->>'bio' ilike '%scien%' 
	or name ilike '%scien%'
	
	-- 174
	or github_about->>'bio' ilike '%research%' 
	or github_about->>'company' ilike '%research%' 
	or name ilike '%research%'
	
	-- 1277
	or email like '%.ac.%%' 
	or email like '%.edu%'

	or name in ('Hadley Wickham', 'Scott Chamberlain', 'Karthik Ram', 'Carl Boettiger')




