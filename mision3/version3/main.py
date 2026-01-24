from flask import Flask, render_template, request, jsonify
from chatbot.data import training_data
from chatbot.model import build_and_train_model,predict_answer,load_model
app =Flask(__name__)

model,vectorizer,unique_answers=load_model()
if model is None:
        model,vectorizer,unique_answers=build_and_train_model(training_data)
@app.route8("/")
def home():
        return render_template("index.html")
@app.route("/chat",methods=["POST"])
def chat():
        user_text = request.form.get("message","")
        if not user_text.strip():
            return jsonify({"response":"por favor escribe algo 🥵"})
        reponse = predict_answer( model,vectorizer,unique_answers,user_text)
        return jsonify({"reponse":reponse})
            
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
    
    