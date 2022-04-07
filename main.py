import math
import pandas as pd
import requests
from datetime import datetime
from datetime import date

token = input("Entre com seu token: ")

headers = {"Authorization": f"Bearer {token}"}

def run_query(cursor):
  f_cursor = "null" if cursor is None else "\"" + cursor + "\""
  query = """{
  search(query: "stars:>100 is:pr is:public", type: ISSUE, first: 20) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on PullRequest {
        repository {
          url  
          pullRequests {
            totalCount
          }
        }
        createdAt
        mergedAt
        additions
        deletions
        body
        reviews {
          totalCount
        }
        files {
          totalCount
        }
        participants {
          totalCount
        }
        comments {
          totalCount
        }
      }
    }
  }
}
"""
  request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
  if request.status_code == 200:
      return request.json()
  else:
      raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

data = []

def save_file(result):
  results = result["data"]["search"]["nodes"]
  for r in results:
    total_pull_requests = r["repository"]["pullRequests"]["totalCount"]
    if total_pull_requests >= 100:
        url = r["repository"]["url"]
        created_at = (r["createdAt"][11:19])
        age = 0
        if r["mergedAt"]:
            merged_at = (r["mergedAt"][11:19])
            format = '%H:%M:%S'
            age = (datetime.strptime(merged_at, format) - datetime.strptime(created_at, format)).seconds
        additions = r["additions"]
        deletions = r["deletions"]
        body = len(r["body"])
        reviews = r["reviews"]["totalCount"]
        files = r["files"]["totalCount"]
        participants = r["participants"]["totalCount"]
        comments = r["comments"]["totalCount"]
        if age / 3600 >= 1: # Check if review took at least 1 hour
            data.append([url, total_pull_requests, age, additions, deletions, body, reviews, files, participants, comments])


  columns = ["URL", "Total Pull Requests", "Age", "Additions", "Deletions", "Body", "Reviews", "Files", "Participants", "Comments"]
  df = pd.DataFrame(data, columns=columns) 
  df.to_csv("repositorios_populares.csv")

pages = 50
endCursor = None

for page in range(pages):
  result = run_query(endCursor)
  save_file(result)
  has_next = result["data"]["search"]["pageInfo"]["hasNextPage"]
  if not has_next:
      break
  endCursor = result["data"]["search"]["pageInfo"]["endCursor"]

