from flask import Flask, request, render_template_string 
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random
import conf_PythonsDeElite as config
import Consultas

caminhoBanco = config.DB_PATH
pio.renderers.default = "browser"
nomeBanco = config.NOMEBANCO
rotas = config.ROTAS    
tabelaA = config.TABELA_A
tabelaB = config.TABELA_B

#Arquivos a serem carregados
dfDrinks = pd.read_csv(f'{caminhoBanco}{tabelaA}') 
dfAvengers = pd.read_csv(f'{caminhoBanco}{tabelaB}', encoding='latin1')

#outros exemplos de encondigs = utg-8, cp1256, iso 8859-1
#criamos o banco de dados em sql caso não exista
conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')

dfDrinks.to_sql("bebidas", conn, if_exists="replace", index=False)
dfAvengers.to_sql("vingadores", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

html_template = f'''
    <h1>Dashboards</h1>
    <h2>Parte 01 </h2>
    <ul>    
        <li> <a href="{rotas[1]}" > Top 10 Paises em consumo de alcool  </a> </li>
        <li> <a href="{rotas[2]}" >por tipo  </a> </li>
        <li> <a href="{rotas[3]}">consumo por região       </a> </li>
        <li> <a href="{rotas[4]}">Comparativo entre tipos </a> </li>
        
    </ul>
     <h2> Parte02</h2>
    <h2>    </h2>
    <ul>    
        <li> <a href="{rotas[5]}">comparar </a> </li>
        <li> <a href="{rotas[6]}"> Upload  </a> </li>
        <li> <a href="{rotas[7]}">Apagar Tabela  </a> </li>
        <li> <a href="{rotas[8]}"> Ver Tabela </a> </li>
        <li> <a href="{rotas[9]}"> V.A.A. </a> </li>
    </ul>
'''

#iniciar o flask
app = Flask(__name__)

@app.route(rotas[0])
def index():
    return render_template_string(html_template)

@app.route(rotas[1])
def grafico1(): 
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn: 
        df = pd.read_sql_query(Consultas.consulta01, conn)
    figuraGrafico01 = px.bar(
        df, 
        x = 'country',
        y = 'total_litres_of_pure_alcohol',
        title = 'Top 10 Paises em consumo de alcool!')    
    return figuraGrafico01.to_html()

@app.route(rotas[2])
def grafico2():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(Consultas.consulta02, conn)
        #transformar as colunas cervejas destilados e vinhos  e linhas criando no fim duas colunas,
        #uma chamada bebidas com os nomes originais das colunas e outra com a média de porções
        #com os seus valor correspondentes
    df_melted = df.melt(var_name='Bebidas', value_name='Média de Porções')
    figuraGrafico02 = px.bar(
        df_melted,
        x = 'Bebidas',
        y = 'Média de Porções',
        title = 'Média de consumo global por tipo'
    )
    return figuraGrafico02.to_html()

@app.route(rotas[3])
def grafico3():
    regioes = {
        "Europa": ['France', 'Germany','Spain','Italy','Portugal'],
        "Asia": ['China', 'Japan','India','Thailand'],
        "Africa": ['Angola', 'Nigeria', 'Egypt','Algeria'],
        "America":['USA','Brazil','Canada','Argentina','Mexico']   
    }
    dados = []
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        for regiao, paises in regioes.items():
            placeholders = ",".join([f"'{p}'" for p in paises])
            query = f''' 
                SELECT SUM (total_litres_of_pure_alcohol) AS total
                FROM  bebidas
                WHERE country IN ({placeholders})
    '''
            total = pd.read_sql_query(query, conn).iloc[0,0]
            dados.append({"região": regiao,
                        "Consumo total": total})

    dfRegioes = pd.DataFrame(dados)
    figuraGrafico03 = px.pie(
        dfRegioes , 
        names = "região" ,
        values = "Consumo total" ,
        title = "Consumo total por região"
    )
    return figuraGrafico03.to_html() + f"<br><a href'{rotas[0]}'>Voltar</a>"

@app.route(rotas[4])
def grafico4():
    with sqlite3.connect(f'{caminhoBanco}{nomeBanco}') as conn:
        df = pd.read_sql_query(Consultas.consulta03, conn)
        medias = df.mean().reset_index()
        medias.columns = ['Tipo', 'Média']
        figuraGrafico04 = px.pie(
            medias,
            names = "Tipo",
            values = "Média",
            title = "Proporção média entre os tipos de bebidas!"
        )
        return figuraGrafico04.to_html() + f"<br><a href'{rotas[0]}'>Voltar</a>"


@app.route(rotas[5], methods = ["POST", "GET"])
def comparar():   
    opcoes = [
        'beer_servings',
        'spirit_servings',
        'wine_servings'
    ]

    if request.method == "POST":
        eixo_x = request.form.get('eixo_x')
        eixo_Y = request.form.get('eixo_y')
        if eixo_x == eixo_Y:
            return f"<h3> Selecionar campos diferentes! <h3> <br><a href='{rotas[0]}'>Voltar</a>"
        conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
        df = pd.read_sql_query("SELECT country, {}, {} FROM bebidas".format(eixo_x,eixo_Y), conn)
        conn.close()

        figuraComparar = px.scatter(
                df,
                x = eixo_x,
                y = eixo_Y,
                title=f"Comparação entre {eixo_x} VS {eixo_Y} "
        )
        figuraComparar.update_traces(textposition = 'top center')
        return figuraComparar.to_html() + f"<br><a href'{rotas[0]}'>Voltar</a>"

    return render_template_string('''
        <h2> comparar campos </h2>
        <form method = "POST">
            <label> Eixo X </label>
            <select name = "eixo_x">
                    {% for opcao in opcoes %}
                        <option value ='{{opcao}}'> {{opcao}} </option>
                    {% endfor %}
            </select>               
            <br> <br>

            <label> Eixo Y </label>
            <select name = "eixo_y">
                    {% for opcao in opcoes %}
                        <option value ='{{opcao}}'> {{opcao}} </option>
                    {% endfor %}
            </select>               
            <br> <br>

            <input type="submit" value= "--comparar--">                                           
        </form>
        <br><a href="{{rotaInterna}}">Voltar</a>                                                           
    ''', opcoes = opcoes, rotaInterna = rotas[0])

@app.route(rotas[6],methods=['GET','POST'])
def upload():
    if request.method=="POST":
        recebido = request.files['c_arquivo']
        if not recebido:
            return f"<h3> Nenhum arquivo enviado </h3><br><a href='{rotas[6]}'>Voltar</a>"
        dfAvengers.to_sql("vingadores",conn, if_exists="replace",
        index=False)   
        conn.commit()
        conn.close()
        return f"<h3> Upload feito com sucesso  </h3><br><a href='{rotas[6]}'>Voltar</a>"

    return'''
        <h2> Upload da tabela Avengers! </h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="c_arquivo" accept=".csv">
            <input type="submit" value="--Carregar--">
        </form>
'''






#inicia o servidor
if __name__ == '__main__':
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )