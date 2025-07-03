from django.shortcuts import render
import spacy

nlp = spacy.load("es_core_news_md")

# Defino palabras relevantes
PALABRAS_TIEMPO = {
    "antes", "ahora", "después", "ayer", "hoy", "mañana", "actualmente",
    "luego", "pronto", "recién", "todavía", "ya", "más", "tarde", "siempre",
    "nunca", "anoche", "previamente", "en", "el", "futuro"
}
PALABRAS_NEGACION = {"no", "nunca", "tampoco"}
PALABRAS_PREGUNTA = {
    "quién", "qué", "cuándo", "dónde", "cómo", "por", "qué", "cuál",
    "quiénes", "cuales", "cuánto", "cuánta", "cuántos", "cuantas"
}
POSESIVOS = {"mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra", "nuestros", "nuestras"}
DEP_POSESIVOS = {"det", "det:poss", "nmod:poss", "poss"}
ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas"}
VERBOS_DESCARTAR = {"ser", "estar"}

def transformar_a_lsa(oracion):
    doc = nlp(oracion.lower())
    
    sujeto = ""
    objeto = ""
    verbo = ""
    tiempo = ""
    negacion = ""
    pregunta = ""
    adjetivos = []
    verbos_aux = []
    usados = set()
    pertenencias = {} #sustantivo -> posesivo

    # Buscar posesivos
    for token in doc:
        if token.dep_ in DEP_POSESIVOS and token.text in POSESIVOS:
            sust = token.head.text
            pose = token.text
            compuesto = f"{sust} {pose}"
            
            if not sujeto:
                sujeto = compuesto
                usados.update([sust, pose])
            elif not objeto:
                objeto = compuesto
                usados.update([sust, pose])

    # Recorrido principal de tokens
    for token in doc:
        #Ignoro los artículos
        if token.text in ARTICULOS:
            continue 
        # Palabras de tiempo
        if token.text in PALABRAS_TIEMPO and token.text not in usados:
            tiempo = token.text
            usados.add(token.text)

        # Negaciones
        if token.text in PALABRAS_NEGACION and token.text not in usados:
            negacion = token.text
            usados.add(token.text)

        # Preguntas
        if token.text in PALABRAS_PREGUNTA and token.text not in usados:
            pregunta = token.text
            usados.add(token.text)

        # Adjetivos
        if token.pos_ == "ADJ" and token.text not in usados:
            adjetivos.append(token.text)
            usados.add(token.text)

        # Verbos principales y auxiliares
        if token.pos_ == "VERB" and token.lemma_ not in VERBOS_DESCARTAR and token.text not in usados:
            if token.dep_ == "ROOT":
                verbo = token.lemma_
            else:
                verbos_aux.append(token.lemma_)
            usados.add(token.text)

        # Sujeto si no se detectó antes
        if token.dep_ == "nsubj" and not sujeto and token.text not in usados:
            sujeto = token.text
            usados.add(token.text)

        # Objeto 
        if token.dep_ in {"obj", "dobj", "obl"} and not objeto and token.text not in usados:
            objeto = token.text
            usados.add(token.text)

    # Si no se detectó verbo principal, buscar otro
    if not verbo:
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in VERBOS_DESCARTAR and token.text not in usados:
                verbo = token.lemma_
                usados.add(token.text)
                break

    # Reorganización de la oración 
    resultado = []

    if tiempo:
        resultado.append(tiempo)
    if sujeto:
        resultado.append(sujeto)
        if sujeto in pertenencias:
            resultado.append(pertenencias[sujeto])
    if objeto:
        resultado.append(objeto)
        if objeto in pertenencias:
            resultado.append(pertenencias[objeto])
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
