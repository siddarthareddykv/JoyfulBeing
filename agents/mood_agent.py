@app.route("/mood", methods=["POST"])
def mood():
    user_mood = request.form["mood"]
    suggestion = generate_suggestion(user_mood)
    return render_template("result.html", suggestion=suggestion)

def generate_suggestion(mood):
    prompt = f"""
    User is feeling {mood}.
    Suggest:
    1 short calming message
    1 breathing exercise
    1 small action for today.
    Tone: gentle, peaceful.
    """
    
    response = llm_api_call(prompt)
    return response
