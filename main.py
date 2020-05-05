from flask import Flask, url_for, request, render_template, redirect
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
db_session.global_init("db/plan.sqlite")

def main():
    app.run()

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')