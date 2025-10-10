from argparse import ArgumentParser
from flask import Flask
from random import randint

app = Flask(__name__)

@app.route('/')
def dado():
    return f'dato tirato e numero: {randint(0, 6)+1} estratto!'

if __name__ == '__main__':
    aparse = ArgumentParser()
    aparse.add_argument('-p', '--port')
    args = aparse.parse_args()

    app.run(host='0.0.0.0', port=int(args.port))