from client import Client
valid_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2RhdGFtZXJtYWlkLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMzQxOTkwNDcwMDU3MjAyMzQxMiIsImF1ZCI6WyJodHRwczovL2Rldi1hcGkuZGF0YW1lcm1haWQub3JnIl0sImlhdCI6MTYyNDQ4NjEwOSwiZXhwIjoxNjI0NDkzMzA5LCJhenAiOiI0QUhjVkZjd3hIYjdwMVZGQjlzRldHNTJXTDdwZE5tNSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.FbOKWgqC-fwYAJy1xqLg4M3tp5eZBAdfdkbJVZFrtT0'


c = Client(token=valid_token)
valid_name = 'Bronx River'
valid_id = '2c56b92b-ba1c-491f-8b62-23b1dc728890'
test_id = '8c213ce8-7973-47a5-9359-3a0ef12ed201'
project_data =['sites', 'managements', 'project_profiles', 'observers', 'collectrecords',
                                         'obstransectbeltfishs', 'obsbenthiclits','obsbenthicpits',
                                         'obshabitatcomplexities', 'obscoloniesbleached', 'obsquadratbenthicpercent']


#print(type(c.get_info(info='version')))
#print(c.get_projects())
#print(c.get_my_project(name=valid_name))
#print(c.get_project_data(data='obsbenthicpits', id=valid_id))
print(c.get_obs_data(obs='obstransectbeltfishs', filter='size_min', filter_val=15, id=valid_id))

# https://dev-api.datamermaid.org/v1/projects/2c56b92b-ba1c-491f-8b62-23b1dc728890/obstransectbeltfishs/