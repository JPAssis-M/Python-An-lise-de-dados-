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

def getDbConnect():
    conn = sqlite3.connect(f'{caminhoBanco}{nomeBanco}')
    conn.row_factory = sqlite3.Row
    return conn


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
@app.route('/apagar_tabela/<nome_tabela>', methods=['GET'])
def apagarTabela(nome_tabela): 
    conn = getDbConnect()
    cursor = conn.cursor()

#usaremoso try except para controlar possíveis erros
#confirmar se a tabela existe
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name={nome_tabela}")
    existe = cursor.fetchone()[0]
    if not existe: 
        conn.close()
        return "Tabela não encontrada"
    try: 
        cursor.execute(f'DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f'Tabela{nome_tabela}apagada com sucesso'
    except Exception as erro:
        conn.close()
        return f"Não foi possível apagar a tabela erro: {erro}"

@app.route(rotas[8], methods=["POST","GET"])
def ver_tabela():     
    if request.method =="POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas', 'vingadores']:
            return f"<h3> Tabela {nome_tabela} não encontrada</h3> <br><a href{rotas[8]}>Voltar</a>"
        
        conn =getDbConnect()
        df = pd.read_sql_query(f"SELECT * from {nome_tabela}", conn)
        conn.close()
        tabela_html = df.to_html(classes='table table-striped')
        return f'''
            <h3>Conteudo da tabela {nome_tabela}:</h3>                
            {tabela_html}
            <br><a href={rotas[8]}>Voltar</a>

'''
    return render_template_string ('''
        <marquee>Selecione a tabela a ser visualizada: </marquee>
        <form method="POST">
            <label for="tabela">Escolha a tabela abaixo: </label>      
            <select name="tabela">
                <option value="bebidas">Bebidas</option>
                <option value="vingadores">Vingadores</option>
            </select>
            <hr>
            <input type="submit" value="Consultar Tabela">
         </form>
        <br><a href={{rotas[0]}}>Voltar </a>
    ''', rotas=rotas)

'''
@app.route(rotas[7], methods=['GET'])
def apagarV2(nome_tabela):
    conn = getDbConnect()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM sqlite_master WHERE type='table' AND name='{nome_tabela}'")
    existe = cursor.fetchone()[0]
    if not existe:
        conn.close()
        return "Tabela não encontrada"
    
    try: 
        cursor.execute(f'DROP TABLE "{nome_tabela}"')
        conn.commit()
        conn.close()
        return f'Tabela {nome_tabela} apagada com sucesso'
    except Exception as erro:
        conn.close()
        return f"Não foi possível apagar a tabela. Erro: {erro}"       
'''
@app.route(rotas[7],methods=['Post','GET'])
def apagarV2():
    if request.method =="POST":
        nome_tabela = request.form.get('tabela')
        if nome_tabela not in ['bebidas','vingadores']:
         return f"<h3> Tabela {nome_tabela} não encontrada</h3> <br><a href{rotas[7]}>Voltar</a>"
        
        confirmacao = request.form.get('confirmacao')
        conn = getDbConnect()
        if confirmacao == "sim":
            try: 
                cursor = conn.cursor()
                cursor.execute('SELECIONAR name_FROM sqlite_master WHERE type= tabela AND name=?', (nome_tabela,))
                if cursor.fetchone() is None:
                    return f"<h3>Tabela {nome_tabela} não encontrada no banco de dados! </h3><br><a href={rotas[7]}>Voltar</a>"
                cursor.execute(f'DROP TABLE IF EXISTS "{nome_tabela}"')
                conn.commit()
                conn.close()
                return f"<h3>Tabela {nome_tabela} não encontrada no banco de dados! </h3><br><a href={rotas[7]}>Voltar</a>"

            except Exception as erro:
                conn.close()
                return f"<h3>Erro ao apagar a tabela {nome_tabela} Erro:{erro} </h3><br><a href={rotas[7]}>Voltar</a>"
    
    return f'''
        <html>
            <head>
                <title><marquee> CUIDADO!-Apagar Tabela </marquee></title>
            </head>
            <>body        
            <h2> Selecionar a tabela para apagar </h1>
            <form method="POST" id="formApagar">
                <label for="tabela"> Escolha na tabela abaixo: </label>
                <select name="tabela" id="tabela">
                    <option value="">Selecione...</option>
                    <option value="bebidas">Bebidas</option>
                    <option value="vingadores">Vingadores </option>
                    <option value="vingadores">Usuarios</option>
                </select>
                <input type="hidden" name="confirmacao" value="" 
                id="confirmacao">
                <input type="submit" value = "--Apagar!--" onclick="return confirmarExclusao();"
            </form>    
            <br><a href={{rotas[0]}}>Voltar</a>            
            <script type="text/javascript">
                function confirmarExclusao(){{
                var ok = confirm ('tem certeza de que deseja apagar a tabela selecionada'); 
                if(ok) {{
                    document.getElementById
                    ('confirmacao').value = 'sim';
                    return true
                }}
                else{{        
                   document.getElementById
                    ('confirmacao').value = 'não';
                    return false
                }}
            </script>   
            <body>            
        </html>
 '''     
##### ROTA 9 AVENGERS ALCOOLICOS ANONIMEESSS
@app.route(rotas[9], methods= ['GET','POST'])
def vaa_mortes_consumo():
    
   #cada dose corresponde a 14g de alcool puro!
    metricas_beb = {
        "Total (L de Alcool)":"total_litres_of_pure_alcohol",
        "Cerveja (doses)":"beer_servings",
        "Destilados (doses)":"spirit_servings",
        "Vinho (doses)":"wine_servings"
    }

    if request.method == "POST":
        met_beb_key = request.form.get("metrica_beb") or "Total (L de Alcool)"
        met_beb = metricas_beb.get(met_beb_key, "total_litres_of_pure_alcohol") #met_beb = request.get(met_beb_key, "total_litres_of_pure_alcohol")
        #semente opcional para reproduzir a mesma distribuição de paises nos vingadores

        try:
            semente = int(request.form.get("semente"))
        except: 
            semente = 42
        sementeAleatoria = random.Random(semente) #gera o valor aleatório baseado na semente escolhida

        # le os dados do SQL
        with getDbConnect () as conn:
            dfA = pd.read_sql_query ('SELECT *FROM vingadores', conn)
            dfB = pd.read_sql_query ('SELECT country, beer_servings, spirit_servings, wine_servings,total_litres_of_pure_alcohol *FROM bebidas', conn)

        #_______Morte dos Vingadores
        #estrategia é somar as colunas que contenha o death como true(case-insensitive
        #contaremos não-nulos como 1,ou seja, death1 tem true: vale 1, não tem nada; vale 0
        death_cols = [c for c in dfA.columns if"death" in c.lower()] 
        if death_cols:
            dfA["Mortes"] = dfA [death_cols].notna().astype(int).sum(axis=1)
        elif "Deaths" in dfA.columns:
            dfA["Mortes"] = pd.to_numeric(dfA["Deaths"], errors="coerce").fillna().astype(int)
        else:
            dfA ["Mortes"] = 0
        if "Name/Alias" in dfA.columns:
            col_name = "Name/Alias"
        elif "Name" in dfA.columns:
            col_name = "Name"
        elif "" in dfA.columns:
            col_name = ""
        elif "Alias" in dfA.columns:
            col_name = "Alias"
        else:
            possivel_texto = [c for c in dfA.columns if dfA[c].dtype == "object"]
            col_name = possivel_texto [0] if possivel_texto else dfA.columns[0]
        dfA.rename(columns={col_name:"Personagem"}, inplace=True)

        #----------Sortear um país para cada vingador
        paises = dfB["country"].dropna().astype(str).to_list()
        if not paises:
            return f"<h3> Não há países na tela de bebidas!</h3><a href={rotas[9]}>Voltar</a>"

        dfA["Pais"] = [sementeAleatoria.choice(paises) for _ in range(len(dfA))]
        dfB_cons = dfB[["country","met_beb"]].rename(columns={"country":"Pais", met_beb : "consumo"})

        base = dfA[["Personagem","Mortes", "Pais"]].merge(dfB_cons, on="Pais", how="left")

        #filtrar apenas linhas validas
        base = base.dropna(subset=['Consumo'])
        base["Mortes"] = pd.to_numeric(base["Mortes"], errors="coerce").fillna(0).astype(int)
        base = base[base["Mortes"]>= 0]
        corr_txt = ""
        if base ["Consumo"].notna().sum() >3 and base ["Mortes"].notna().sum >=3:
            try:
                corr = base ["consumo"].corr(base["Mortes"])
                corr_txt = f" • r = {corr:.3f}"
            except Exception:
                pass 

    #---------------------------------GRAFICO SCATTER 2D: CONSUMO X MORTES
            fig2d = px.scatter(
               base,
               x = "Consumo", 
               y = "Mortes",
               color = "Pais",
               hover_name = " Personagem",
               hover_data = {
                   "Pais": True,
                   "Consumo": True,
                   "Mortes": True
               },
               title = f"Vingadores - Mortes vs consumo de alcool do pais "
               ({met_beb_key}){corr_txt}"
            )
            fig2d.update_layout(
                xaxis_title = f"{met_beb_key}",
                yaxis_title = "Mortes (contagem)",
                margin = dict (l=40, r=20, t=70, b=40)
            )
            return (
                "<h3>---Grafico 2D ---</h3>"
                + fig2d.to_html(full_html=False)
                +"<hr>"
                +"<h3>---Grafico 3D ---</h3>"
                + "<p> Em breve </p>"
                +"<h3>---Preview dos dados ---</h3>"
                +"<p> Em breve </p>"
                +"<hr>"
                +f"<a href={rotas[9]}>Voltar</a>"
                +"<br>"
                +f"<a href={rotas[9]}>Menu Inicial</a>"
            )        

    return render_template_string("""
    <style>
           body, html {
    margin: 0;
    padding: 0;
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9f9f9;
    color: #333;
    line-height: 1.6;
}

/* CONTAINER CENTRALIZADO */
form {
    max-width: 500px;
    margin: 40px auto;
    padding: 30px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* TÍTULOS */
h2 {
    text-align: center;
    color: #2c3e50;
}

/* LABELS */
label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    color: #555;
}

/* SELECT & INPUT */
select, input[type="number"] {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 8px;
    margin-bottom: 20px;
    transition: border-color 0.3s ease;
}

select:focus, input:focus {
    border-color: #3498db;
    outline: none;
}

/* BOTÃO */
input[type="submit"] {
    background-color: #3498db;
    color: white;
    padding: 12px;
    border: none;
    width: 100%;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

input[type="submit"]:hover {
    background-color: #2980b9;
}

/* PARÁGRAFOS DE EXPLICAÇÃO */
p {
    max-width: 700px;
    margin: 20px auto;
    padding: 0 20px;
    text-align: justify;
    color: #666;
}

/* LINK VOLTAR */
a {
    display: block;
    text-align: center;
    margin: 30px auto;
    font-weight: bold;
    color: #2c3e50;
    text-decoration: none;
    transition: color 0.3s ease;
}

a:hover {
    color: #2980b9;
}

/* MOBILE RESPONSIVO */
@media (max-width: 600px) {
    form {
        margin: 20px;
        padding: 20px;
    }
}                       
</style>        
                                  
            <h2> V.A.A - Pais x Consumo X Mortes </h2>
                <form method="POST">
                    <label for="metrica_beb"> <b> Metrica do consumo:</b> </label>
                    <select name="metrica_beb" id="metrica_beb">
                        {% for metrica in metrica_beb.keys() %}
                              <option value="{{metrica}}">{{metrica}} </option>
                        {% endfor %}          
                    </select>
                    <br><br>
                    <label> <b>Semente:</b> (<i>opcional, p/reprodutibilidade</i>) </label>
                    <input type="number" name="semente" id="semente" value="42">

                    <br><br>
                    <input type="submit" value="--Gerar Graficos>--""                                            
                </form>
                <p>
                  Esta visão sorteia um pais para cada vingador, soma as mortes dos personagens(usando todas as colunas que contenham death) e anexo o consumo de alcool do pais, ao fim plota um
scatter 2d (Consumo X Mortes) e um gráfico 3d=D (Pais x Mortes)                
                </p>
                <br>
                <a href={{rotas[0]}}>Voltar</a>
""", metricas_beb = metricas_beb, rotas=rotas)


#inicia o servidor
if __name__ == '__main__':
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )