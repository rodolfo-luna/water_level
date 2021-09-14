import pandas as pd 
import streamlit as st 
import math
import datetime
import matplotlib.pyplot as plt 
import seaborn as sns

relatorio = ""

altura_do_sensor = 91  #Se o sensor estiver acima dessa altura, essa variável precisa ser ajustada.
raioPrimeiraBase = 58  
alturaPrimeiraBase = 19.5
raioSegundaBase = 61.5  
alturaSegundaBase = 19 
raioTerceiraBase = 66  
alturaTerceiraBase = 29 
raioQuartaBase = 67 
alturaQuartaBase = 10.5

def menu_lateral():
    global relatorio
    rel_opcoes = ["Escolha o relatório", "Caixa d'água", "Clima", "Debug"]
    relatorio = st.sidebar.selectbox("Escolha qual relatório quer visualizar", rel_opcoes)

def relatorio_clima():
    st.title("RELATÓRIO DO CLIMA")
    st.write("Em breve")

def relatorio_debug():
    hora_agora = datetime.datetime.now()
    data_hoje = datetime.date.today()
    st.title("DEBUG DO VOLUME DE ÁGUA")
    dados_ultrasonico = pd.read_csv('/home/pi/Documents/webservice_caixa_dagua/ultrasonico.csv')
    ultimas_leituras = dados_ultrasonico.tail(15)
    ultima_leitura = ultimas_leituras.distancia.mode()[0]
    altura = altura_do_sensor - ultima_leitura
    st.write("Altura = ", altura)
    st.write("Hora do registro: ", ultimas_leituras.tail(1)['hora'])
    st.write("Últimas leituras: ")
    st.table(ultimas_leituras)

    dados_ultrasonico['faixa'] = dados_ultrasonico['hora'].str.slice(0,13)
    dados_ultrasonico['faixa'] = pd.to_datetime(dados_ultrasonico['faixa'], dayfirst=True)
    dados_agrupados = dados_ultrasonico.groupby(['faixa']).agg(lambda x:x.value_counts().index[0]).reset_index()
    dados_agrupados['altura'] = 91 - dados_agrupados['distancia']
    
    mask = (dados_agrupados['faixa'] >= str(data_hoje)) & (dados_agrupados['faixa'] <= str(hora_agora))
    dados_selecionados = dados_agrupados.loc[mask]
    st.write("Dados selecionados por data")
    st.write(dados_selecionados)

def calculaVolumeDoCilindo(raioDaBase, altura):
    pi = math.pi
    volume = (pi * altura * raioDaBase ** 2)/1000 #já convertendo ml para l
    return volume

def calcula_volume_com_altura(altura):
    if (altura == alturaPrimeiraBase + alturaSegundaBase + alturaTerceiraBase + alturaQuartaBase):
        volume = calculaVolumeDoCilindo(raioPrimeiraBase, alturaPrimeiraBase) + calculaVolumeDoCilindo(raioSegundaBase, alturaSegundaBase) + calculaVolumeDoCilindo(raioTerceiraBase, alturaTerceiraBase) + calculaVolumeDoCilindo(raioQuartaBase, alturaQuartaBase)
        return int(volume)

    elif (altura >= alturaPrimeiraBase + alturaSegundaBase + alturaTerceiraBase):
        alturaRestante = altura - (alturaPrimeiraBase + alturaSegundaBase + alturaTerceiraBase)
        volume = calculaVolumeDoCilindo(raioPrimeiraBase, alturaPrimeiraBase) + calculaVolumeDoCilindo(raioSegundaBase, alturaSegundaBase) + calculaVolumeDoCilindo(raioTerceiraBase, alturaTerceiraBase) + calculaVolumeDoCilindo(raioQuartaBase, alturaRestante)
        return int(volume)

    elif (altura >= alturaPrimeiraBase + alturaSegundaBase):
        alturaRestante = altura - (alturaPrimeiraBase + alturaSegundaBase)
        volume = calculaVolumeDoCilindo(raioPrimeiraBase, alturaPrimeiraBase) + calculaVolumeDoCilindo(raioSegundaBase, alturaSegundaBase) + calculaVolumeDoCilindo(raioTerceiraBase, alturaRestante)
        return int(volume)

    elif (altura >= alturaPrimeiraBase):
        alturaRestante = altura - alturaPrimeiraBase
        volume = calculaVolumeDoCilindo(raioPrimeiraBase, alturaPrimeiraBase) + calculaVolumeDoCilindo(raioSegundaBase, alturaRestante)
        return int(volume)

    elif (altura < alturaPrimeiraBase):
        volume = calculaVolumeDoCilindo(raioPrimeiraBase, altura)
        return int(volume)

def imagem_volume(altura):
    if altura == 68:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_68.jpg'
    elif altura < 68 and altura >=60:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_60.jpg'
    elif altura < 60 and altura >=50:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_50.jpg'
    elif altura < 50 and altura >=40:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_40.jpg'
    elif altura < 40 and altura >=30:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_30.jpg'
    elif altura < 30 and altura >=20:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_20.jpg'
    elif altura < 20:
        imagem = '/home/pi/Documents/streamlit_smarthome/caixa_imagens/caixa_10.jpg'
    return imagem

def plota_grafico(dados):
     st.area_chart(data=dados, width=0, height=0, use_container_width=True)


def menu_de_consumo(dados):
    dados = dados.reset_index()
    volume_anterior = 0
    volume = 0
    for index, row in dados.iterrows():
        if index == 0:        
            volume_anterior = row['volume']
        else:
            if row['volume'] < volume_anterior:
                volume = volume_anterior  - row['volume'] + volume
            volume_anterior = row['volume']

    st.warning('Consumo no período: '+str(volume)+' litros')


def menu_data(dados_agrupados):
    inicial = st.text_input("Data inicial: ", datetime.date.today())
    final = st.text_input("Data final: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    submit = st.button('ENVIAR')
    if submit:
        mask = (dados_agrupados['faixa'] >= str(inicial)) & (dados_agrupados['faixa'] <= str(final))
        dados_selecionados = dados_agrupados.loc[mask]
        dados_selecionados['volume'] = dados_selecionados['altura'].apply(lambda x: calcula_volume_com_altura(x))
        dados_selecionados = dados_selecionados[['faixa', 'volume']]
        dados_selecionados = dados_selecionados.set_index('faixa')
        
        plota_grafico(dados_selecionados)
        menu_de_consumo(dados_selecionados)

def relatorio_caixa_agua():
    st.title("RELATÓRIO DO VOLUME DE ÁGUA")
    dados_ultrasonico = pd.read_csv('/home/pi/Documents/webservice_caixa_dagua/ultrasonico.csv')
    ultimas_leituras = dados_ultrasonico.tail(15)
    ultima_leitura = ultimas_leituras.distancia.mode()[0]
    altura = altura_do_sensor - ultima_leitura
    volume = calcula_volume_com_altura(altura)
    if altura <= 20:
        st.error("A caixa está com "+str(volume)+" litros")
        st.error("Hora da leitura: "+str(ultimas_leituras.tail(1)['hora'].to_string()[5:]))
    elif altura <= 36:
        st.warning("A caixa está com "+str(volume)+" litros")
        st.warning("Hora da leitura: "+str(ultimas_leituras.tail(1)['hora'].to_string()[5:]))
    else:
        st.success("A caixa está com "+str(volume)+" litros")
        st.success("Hora da leitura: "+str(ultimas_leituras.tail(1)['hora'].to_string()[5:]))

    st.image(imagem_volume(altura), width=300)
    dados_ultrasonico['faixa'] = dados_ultrasonico['hora'].str.slice(0,13)
    dados_ultrasonico['faixa'] = pd.to_datetime(dados_ultrasonico['faixa'], dayfirst=True)
    dados_agrupados = dados_ultrasonico.groupby(['faixa']).agg(lambda x:x.value_counts().index[0]).reset_index()
    dados_agrupados['altura'] = 91 - dados_agrupados['distancia']
    menu_data(dados_agrupados)
    

menu_lateral()

if relatorio == "Escolha o relatório":
    st.header("Escolha um relatório no menu ao lado.")

if relatorio == "Caixa d'água":
    relatorio_caixa_agua()

if relatorio == "Clima":
    relatorio_clima()

if relatorio == "Debug":
    relatorio_debug()


#Remover o menu da lateral direita no topo da página
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)