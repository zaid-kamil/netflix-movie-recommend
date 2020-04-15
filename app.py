from flask import Flask, render_template, request, jsonify, redirect, session
from predict import predict
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = "Resident Evil 4 remake has been announced!!"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True, nullable = False)
    email = db.Column(db.String(20), nullable = True)
    password = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return f'self.username, self.email, self.password'

class Search(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    movie = db.Column(db.String(30), unique = True, nullable = False)
    result = db.Column(db.String(20), nullable = True)
    created = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return f'self.username, self.email, self.password'

db.create_all()

@app.route('/')
@app.route('/home')
def home():
    if not session.get('user'):
        return redirect('/signin')
    return render_template('index.html')

@app.route('/signin', methods = ["POST", "GET"])
def Signin():
    
    if request.method == 'POST':
        data = request.form
        
        user = User.query.filter_by(username = data.get('username')).first()
        if user:
            print(user)
            if user.password == data.get('password'):
                print('login success')
                session['user'] = user.username
                return redirect('/home')
                
            else:
                return redirect('/signin')
        else:
            return redirect('/signin')

    return render_template('signin.html')

@app.route('/signup', methods = ["POST", "GET"])
def Signup():
    if request.method == 'POST':
        data = request.form
        user = User(username = data.get('username'), email = data.get('email'), password = data.get('password'))
        db.session.add(user)
        db.session.commit()
        print('data saved!!')
        return redirect('/signin')

    return render_template('signup.html')

@app.route('/logout')
def Logout():
    session['user'] = None
    return redirect('/signin')

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if not session.get('user'):
        return redirect('/signin')
    if request.method=='POST':
        movie_name=request.form.get('movie')
        if movie_name:
            recommendations=predict(movie_name)
            print('r', recommendations)
            return render_template('recommend.html', names=recommendations, movie = movie_name)
    return render_template('recommend.html')

if __name__ == "__main__":
    app.run(debug=True)