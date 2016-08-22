from flask import Flask, redirect, render_template

# from flask_bootstrap import Bootstrap

app = Flask(__name__)

#

# bootstrap = Bootstrap(app)

@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def market():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
