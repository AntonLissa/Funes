from flask import Flask

'''
App Factory Pattern.
Serve per creare più versioni dell'app, ad esempio per testing o produzione, con configurazioni diverse.
'''

def create_app():

    app = Flask(__name__)
    app.secret_key = "super_secret_key_change_me"

    from DSI.api.chat_routes import chat_bp
    app.register_blueprint(chat_bp) # Registra il blueprint per le rotte della chat, un blueprint è un modo per organizzare le rotte in moduli separati.

    return app
