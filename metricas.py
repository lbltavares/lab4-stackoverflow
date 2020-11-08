# Mineração do StackOverflow (consulta dos posts no StackOverflow + valores das metricas do estudo)

import os
import json
import time
import requests as req
import statistics as stat
from datetime import datetime as dt
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
# Métrica: Total de perguntas relacionadas (PostType: Question)
def RQ1():
    total_perguntas = 0
    for r in resultados():
        total_perguntas += int(r["perguntas_relacionadas"])
    return total_perguntas


# RQ 02: total de respostas / total de perguntas relacionadas (PostTypes: Answer / Question)
# Métrica: Total de respostas / total de perguntas relacionadas (PostTypes: Answer/ Question)
def RQ2():
    total_perguntas = RQ1()
    total_respostas = 0
    for r in resultados():
        if r["numero_respostas"]:
            total_respostas += int(r["numero_respostas"])
    return total_respostas / total_perguntas


# RQ 03: numero de estrelas vs total de pergutnas relacionadas
# Métrica: Número de estrelas vs. total de perguntas relacionadas
def RQ3():
    from main import repos
    arr_estrelas = []
    arr_perguntas = []
    with open("RQ3.csv", 'a+', encoding="utf-8") as f:
        w = DictWriter(f, ["numero_estrelas", "perguntas_relacionadas"])
        w.writeheader()
        for repo in repos():
            issues = [i for i in resultados() if repo["nameWithOwner"]
                      in i["url"]]
            estrelas = json.loads(repo["stargazers"].replace("'", '"'))[
                "totalCount"]
            arr_estrelas.append(estrelas)
            perg_relac = sum([int(i["perguntas_relacionadas"])
                              for i in issues])
            arr_perguntas.append(perg_relac)
            row = {
                "numero_estrelas": estrelas,
                "perguntas_relacionadas": perg_relac,
            }
            w.writerow(row)
    result = [stat.median(arr_estrelas), stat.median(arr_perguntas)]
    return result


# RQ 04: Existe alguma relação entre o número de respostas de uma Issue e o seu tempo de fechamento?
# Métrica: Quantidade de respostas de uma Issue / Tempo até o seu fechamento (em dias)
def RQ4():
    respostas, tempo, metrica, contador = 0, 0, 0, 0
    for issue in resultados():
        contador += 1
        try:
            respostas += (int(issue["perguntas_relacionadas"]))
            tempo += issue["closed_at"] - issue["created_at"]
            metrica += (respostas / tempo)
        except Exception as e:
            print(e)
    result = metrica / contador
    return result


# RQ 05: Quais labels de Issues no GitHub tendem a gerar mais perguntas no Stack Overflow? (Bugs, Features, etc?)
# Métrica: Nº de perguntas geradas para cada label
def RQ5():
    return -1


# RQ 06: Qual é a frequência de repetição de Issues do GitHub no Stack Overflow
# Métrica: Issues mencionadas no Stack Overflow / Total de Issues do Repositório
def RQ6():
    from main import repos
    result = 0
    for repo in repos():
        iss = [i for i in resultados() if repo["nameWithOwner"] in i["url"]]
        mencionadas = len(iss)
        total_issues = repo["total_issues"]
        result += (mencionadas / total_issues)
    return result


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
    # coletar()
    print("RQ1 - Total de perguntas relacionadas: %d" % RQ1())
    print("RQ2 - Total de respostas / total de perguntas relacionadas: %f" % RQ2())
    print(f"RQ3 - Número de estrelas vs. total de perguntas relacionadas: [20101.5, 0.0]")
    print("RQ4 - Quantidade de respostas de uma Issue / Tempo até o seu fechamento (em dias): %f" % RQ4())
    print("RQ5 - Nº de perguntas geradas para cada label: %f" % RQ5())
    print("RQ6 - Issues mencionadas no Stack Overflow / Total de Issues do Repositório: %f" % RQ6())
