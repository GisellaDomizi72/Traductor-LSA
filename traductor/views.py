from django.shortcuts import render
import spacy

nlp = spacy.load("es_core_news_sm")

def transformar_a_lsa(oracion):
    doc = nlp(oracion.lower())
    sujeto = ""
    objeto = ""
    verbo = ""
    tiempo = ""
    pertenencia = ""
    negacion = ""
    pregunta = ""
    adjetivos = []
    verbos_aux = []
    otros = []

    for token in doc:
        if token.dep_ == "nsubj":
            sujeto = token.text
        elif token.dep_ == "obj":
            objeto = token.text
        elif token.pos_ == "VERB":
            if token.dep_ == "ROOT":
                verbo = token.lemma_
            else:
                verbos_aux.append(token.lemma_)
        elif token.text in ["antes", "ahora", "después"]:
            tiempo = token.text
        elif token.text in ["no", "nunca", "tampoco"]:
            negacion = token.text
        elif token.dep_ == "poss":
            pertenencia = token.text
        elif token.pos_ == "ADJ":
            adjetivos.append(token.text)
        elif token.text in ["quién", "qué", "cuándo", "dónde", "cómo", "por qué"]:
            pregunta = token.text
        else:
            otros.append(token.text)

    resultado = []

    if tiempo:
        resultado.append(tiempo)

    if sujeto:
        resultado.append(sujeto)
        if pertenencia:
            resultado.append(pertenencia)

    if objeto:
        resultado.append(objeto)
        if pertenencia and not sujeto:
            resultado.append(pertenencia)

    if adjetivos:
        resultado.extend(adjetivos)

    if verbos_aux:
        resultado.extend(verbos_aux)

    if verbo:
        resultado.append(verbo)

    if negacion:
        resultado.append(negacion)

    if pregunta:
        resultado.append(pregunta)

    return " ".join(resultado).capitalize()


def index(request):
    resultado = ""
    if request.method == "POST":
        oracion = request.POST.get("oracion", "")
        resultado = transformar_a_lsa(oracion)

    return render(request, "traductor/index.html", {"resultado": resultado})
