# Naredba za instalaciju u terminalu:
# pip install -r requirements.txt

import random
import uuid
import hashlib
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db

app = Flask(__name__)

db.create_all()

@app.route("/", methods=["GET"])
def index():

    session_token = request.cookies.get("session_token")

    if session_token:
        # uzmi usera iz baze prema session tokenu
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    secret_number = random.randint(1,30)

    # provjeri postoji li već user
    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)
        user.save()

    # provjeri password
    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:

        # kreiramo session token
        session_token = str(uuid.uuid4())

        user.session_token = session_token
        user.save()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")

        return response


@app.route("/result", methods=["POST"])
def result():

    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()


    if guess == user.secret_number:

        msg = "Correct! Secret number was {0}".format(str(guess))

        # kreiraj novi secret number
        new_secret = random.randint(1,30)

        user.secret_number = new_secret
        user.save()

    elif guess > user.secret_number:
        msg = "Not correct, try something smaller."

    elif guess < user.secret_number:

        msg = "Not correct, try something bigger."

    return render_template("result.html", msg=msg)


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        # 1. uzeti podatke iz forme
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        # 2. update user objekta
        user.name = name
        user.email = email

        # 3. pospremi save()
        user.save()

        # 4. redirect na profile stranicu
        return redirect(url_for("profile"))

@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        user.delete()

        return redirect(url_for("index"))

@app.route("/users", methods=["GET"])
def all_users():

    users = db.query(User).all()

    return render_template("users.html", users=users)


@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):

    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('index')))  # redirect na index
    response.set_cookie("session_token", expires=0)  # obriši cookie za logout

    return response



if __name__ == "__main__":
    app.run()