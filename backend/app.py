from quart import Quart

app = Quart(__name__)

@app.route('/solve', methods=['POST'])
def post_solve():...

def run() -> None:
    app.run()