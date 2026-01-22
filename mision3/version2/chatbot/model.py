#scikit-learn
import os 
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

MODEL_DIR="models"
MODEL_PATH =os.path.join(MODEL_DIR,"model.pkl")
VECTORIZER_PATH=os.path.join(MODEL_DIR,"vectorizer.pkl")
ASNWER_PATH=os.path.join(MODEL_DIR,"answer.pkl")

#funcion de entrenamiento  preguntas y respuestas
def build_and_train_model(train_pairs):
    #train_pairs lista de pares (preguntas,respuestas)
    #ejemplo [("hola")!("hola!"),("adios","!hasta luego")]
    #separamos las pareguntas y respuestas en dos listas
    questions =[q for q, _ in train_pairs]# lista de proguntas
    answers =[a for _, a in  train_pairs]  # lista de respuestas
    # creamos el vectorizquierdo,que traducira el texto a numeros 
    Vectorizer=CountVectorizer()
    #entrenamiento
    x = Vectorizer.fit_transform(questions)
    #obtenemos una lista de repuestas unicas 
    unique_answers = sorted(set(answers))
    #creavel dicionario con las etiquetas
    answer_to_label={a: i for i, a in enumerate(unique_answers)}
    y=[answer_to_label[a] for a in answers]
    #modelo  clasificacion de texto 
    model = MultinomialNB()
    #entrenar el modelo
    model.fit(x,y)
    #crear carpeta para guardar el modelo son no existe 
    os.makedirs(MODEL_DIR,exist_ok=True)
    #guardar lso objectos  entrenados
    with open(MODEL_DIR,"wb") as f:
        pickle.dump(model,f)
    return model,Vectorizer,unique_answers
#funcion predict_answer
def predict_answer(model,vetorizer,unique_answer,user_text):
    
# convertimos  el texto  a numeros 
    x = vetorizer.transform([user_text])
    #el modelo  predice la etiqueta de la respuesta  correcta 
    label=model.predict(x)[0]
    return unique_answer[label]
# programa principal 
if __name__ == "__main__":
    training_data =[
    ("hola", "¡Hola! ¿En qué podemos ayudarte hoy?"),
    ("buenos días", "Buenos días, gracias por contactarnos. ¿Cómo podemos asistirte?"),
    ("buenas tardes", "Buenas tardes, es un gusto atenderte. ¿Qué consulta tienes?"),
    ("buenas noches", "Buenas noches, estamos a tu disposición. ¿En qué podemos ayudarte?"),
    ("informacion", "Con gusto te brindamos la información que necesitas. ¿Sobre qué tema?"),
    ("soporte", "Nuestro equipo de soporte está listo para ayudarte. Cuéntanos tu inconveniente."),
    ("precio", "Con gusto te compartimos nuestros precios. ¿Qué servicio te interesa?"),
    ("gracias", "Gracias a ti por comunicarte con nosotros. ¡Que tengas un excelente día!")

    ]
    model ,vectorizer,unique_answer=build_and_train_model(training_data)
    #motrar un mensaje inicial al usuario 
    print("chatbot supervisado listo,escribe salir para terminar.\n")
    while True:
        #pedimos uan frase al usuario 
        user =input("tu:  ").strip()
        if user.lower() in {"salir","exit","quit"}:
            print("bot:  !hasta pronto¡")
            break
        response=predict_answer(model,vectorizer,unique_answer,user)
        print("bot",response)