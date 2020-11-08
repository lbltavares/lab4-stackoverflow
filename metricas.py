# Mineração do StackOverflow (consulta dos posts no StackOverflow + valores das metricas do estudo)

import os
import json
import time
import requests as req
from csv import DictReader, DictWriter

ISSUES_FILE = "issues.csv"
RESULTADO_FILE = "resultado.csv"

fieldnames = ["url", "title", "state", "locked", "id", "number", "title", "labels", "assignee", "comments",
              "created_at", "updated_at", "closed_at", "author_association", "active_lock_reason", "performed_via_github_app"]


erros = 0
key = os.environ["key"]


# Obtem as perguntas relacionadas de uma issue
def get_perguntas_relacionadas(issue):
    global erros
    body = issue["url"]
    body = "/".join(body.split("/")[4:]).split("/")[0]
    URL = f'https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&q={body}&site=stackoverflow&key={key}'
    tentativas = 0
    while True:
        try:
            time.sleep(1)
            res = req.get(URL)
            resJson = json.loads(res.text)["items"]
            return resJson
        except Exception as e:
            print(e)
            tentativas += 1
            if tentativas >= 3:
                erros += 1
                return []
            time.sleep(2)


# Percorre o arquivo .csv e retorna cada issue
def issues():
    with open(ISSUES_FILE, "r", encoding="utf-8") as file:
        for issue in DictReader(file, fieldnames):
            if issue[fieldnames[0]] == fieldnames[0]:
                continue
            yield issue


# Percorre o arquivo .csv e retorna cada resultado
def resultados():
    with open(RESULTADO_FILE, "r", encoding="utf-8") as file:
        for result in DictReader(file, fieldnames + ["perguntas_relacionadas", "numero_respostas"]):
            if result[fieldnames[0]] == fieldnames[0]:
                continue
            yield result


# Anexa uma issue no csv de resultados
def append_resultado(issue):
    existe = os.path.isfile(RESULTADO_FILE)
    try:
        with open(RESULTADO_FILE, 'a+', encoding="utf-8") as f:
            w = DictWriter(f, issue.keys())
            if not existe:
                w.writeheader()
            w.writerow(issue)
    except Exception as e:
        print(e)


# RQ 01: total de perguntas relacionadas (PostType: Question)
def RQ1():
    pass


# RQ 02: total de respostas / total de perguntas relacionadas (PostTypes: Answer / Question)
def RQ2():
    pass


# RQ 03: numero de estrelas vs total de pergutnas relacionadas
def RQ3():
    pass


def coletar():
    contador = 0
    total = 40176
    com_resultado = 0
    for issue in issues():
        perguntas_relacionadas = get_perguntas_relacionadas(issue)
        issue["perguntas_relacionadas"] = len(perguntas_relacionadas)
        issue["numero_respostas"] = sum(
            [i["answer_count"] for i in perguntas_relacionadas])
        append_resultado(issue)
        if len(perguntas_relacionadas) > 0:
            com_resultado += 1
        print("%d/%d (%f%%) com_resultado: %d" %
              (contador, total, (contador/total)*100, com_resultado))


if __name__ == "__main__":
    coletar()
    RQ1()
    RQ2()
    RQ3()
