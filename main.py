#encoding: utf-8

import os
import json
import time
import requests as req
from csv import DictReader, DictWriter

REPOS_FILE = "repos.csv"
ISSUES_FILE = "issues.csv"
TOKEN = os.environ["TOKEN"]

fieldnames = ["url", "title", "state", "locked", "id", "number", "title", "labels", "assignee", "comments",
              "created_at", "updated_at", "closed_at", "author_association", "active_lock_reason", "performed_via_github_app"]


# 1 - Percorrer repos.csv
def repos():
    with open(REPOS_FILE, "r") as file:
        for repo in DictReader(file):
            yield repo


# 2 - Para cada repo, coletar até 50 issues
def issues(repo):
    URL = "https://api.github.com/repos/%s/issues?per_page=50" % (
        repo["nameWithOwner"])
    try:
        res = req.get(URL, headers={"Authorization": "token %s" % TOKEN})
        return json.loads(res.text)
    except Exception as e:
        print(e)


def initfile():
    with open(ISSUES_FILE, "w", encoding="utf-8") as file:
        w = DictWriter(file, fieldnames)
        w.writeheader()


def addissue(issue):
    with open(ISSUES_FILE, "a", encoding="utf-8") as file:
        w = DictWriter(file, fieldnames)
        w.writerow(issue)


# 3 - Salvar o resultado em issues.csv
if __name__ == "__main__":
    initfile()
    n = 0
    for r in repos():
        time.sleep(1)
        n += 1
        print("%d %s" % (n, r["nameWithOwner"]))
        try:
            iss = issues(r)
            for i in iss:
                try:
                    addissue({
                        "url": i.get("url", ""),
                        "title": i.get("url", ""),
                        "state": i.get("state", ""),
                        "locked": i.get("locked", ""),
                        "id": i.get("id", ""),
                        "number": i.get("number", ""),
                        "title": i.get("title", ""),
                        "labels": i.get("labels", ""),
                        "assignee": i.get("assignee", ""),
                        "comments": i.get("comments", ""),
                        "created_at": i.get("created_at", ""),
                        "updated_at": i.get("updated_at", ""),
                        "closed_at": i.get("closed_at", ""),
                        "author_association": i.get("author_association", ""),
                        "active_lock_reason": i.get("active_lock_reason", ""),
                        "performed_via_github_app": i.get("performed_via_github_app", "")
                    })
                except Exception as e:
                    print(e)
        except Exception as e2:
            print(e2)
