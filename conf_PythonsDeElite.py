
#  ____        _   _                       ____         _____ _ _ _       
# |  _ \ _   _| |_| |__   ___  _ __  ___  |  _ \  ___  | ____| (_) |_ ___ 
# | |_) | | | | __| '_ \ / _ \| '_ \/ __| | | | |/ _ \ |  _| | | | __/ _ \
# |  __/| |_| | |_| | | | (_) | | | \__ \ | |_| |  __/ | |___| | | ||  __/
# |_|    \__, |\__|_| |_|\___/|_| |_|___/ |____/ \___| |_____|_|_|\__\___|
#        |___/                                                            

# Autor: João Pedro 
# Versão 0.0.1v 09-2025

#CAMINHO DA PASTA
DB_PATH = "C:/Users/noturno/Desktop/Python - João/"
NOMEBANCO = "bancodeElite,db"
TABELA_A = 'drinks.csv'
TABELA_B = 'avengers.csv'

#definições servidor
FLASK_DEBUG = True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

#ROTAS(CAMINHO DE CADA PÁGINA)
ROTAS = [
    '/',                # rota 00
    '/grafico1',        # rota 01
    '/grafico2',        # rota 02
    '/grafico3',        # rota 03
    '/grafico4',        # rota 04
    '/comparar',        # rota 05
    '/upload',          # rota 06
    '/apagar',          # rota 07
    '/ver',             # rota 08
    '/final'            # rota 09
]
#-------------------------
#       Consultas SQL
#-------------------------

