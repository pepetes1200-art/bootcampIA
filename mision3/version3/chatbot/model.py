#scikit-learn
import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

MODEL_DIR= "models"
MODEL_PATH =os.path.join(MODEL_DIR,"model.pkl")
VECTORIZER_PATH=os.path.join(MODEL_DIR,"vectorizer.pkl")
ANSWERS_PATH=os.path.join(MODEL_DIR,"answers.pkl")

#Función de entrenamiento preguntas y respuestas
def build_and_train_model(train_pairs):
    #train_pairs lista de pares(pregunta,respuestas)
    #Ejemplo [("Hola","!Hola¡"),("adiós","¡Hasta luego!")]
    # separamos las preguntas y respuestas en dos listas
    questions =[q for q, _ in train_pairs]# lista de preguntas
    answers =[a for _, a in train_pairs]  # lista de respuestar
    # creamos el vectorizado, que traducirá el texto a números
    vectorizer=CountVectorizer()
    #Entrenamiento
    x = vectorizer.fit_transform(questions)
    # obtenemos una lista de respuestas Únicas
    unique_answers = sorted(set(answers))
    # crear el dicionario con las etiquetas
    answer_to_label={a: i for i, a in enumerate(unique_answers)}
    #creamos una lista
    y=[answer_to_label[a] for a in answers]
    #Modelo clasificación de texto
    model = MultinomialNB()
    #Entrenar el modelo
    model.fit(x,y)
    #crear carpeta para guardar el model si no existe
    os.makedirs(MODEL_DIR,exist_ok=True)
    #Guardar los objetos entrenados
    with open(MODEL_PATH,"wb") as f:
        pickle.dump(model,f)
    with open(VECTORIZER_PATH,"wb") as f:
        pickle.dump(vectorizer, f)
    with open(ANSWERS_PATH,"wb")as f:
        pickle.dump(unique_answers,f)
    print("🆗 Modelo entrebado y guardado correctamente")
    return model,vectorizer,unique_answers

def load_model():
    """
    Carga el modelo, el vectorizado y las respuestas si existe.
    """
    if(
        os.path.exists(MODEL_PATH)
        and os.path.exists(VECTORIZER_PATH)
        and os.path.exists(ANSWERS_PATH)
    ):
        with open(MODEL_PATH,"rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH,"rb") as f:
            vectorizer=pickle.load(f)
        with open (ANSWERS_PATH,"rb") as f:
            unique_answers= pickle.load(f)
        print("📂 Modelo cargado desde disco.")
        return model,vectorizer,unique_answers
    else:
        print("⚠️ No hay modelo guardado, será necesario entrenarlo")
        return None,None,None
                  
def predict_answer(model,vectorizer,unique_answers,user_text):
    # convertimos el texto a números
    x = vectorizer.transform([user_text])
    # el modelo predice la etiqueta de la respuesta correcta
    label = model.predict(x)[0]
    return unique_answers[label]
 