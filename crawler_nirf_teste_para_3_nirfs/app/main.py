# importar o selenium e suas utilidades, intertools e sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from itertools import cycle
import sqlite3

# para ler os nirfs do .txt

txt_dos_nirfs = open("nirfs.txt", "r") ## ler nirfs.txt
lista_de_nirfs_com_aspas = (txt_dos_nirfs.read()).split(", ") ## como o texto vem como string, o .split(", ") vai transformar em lista de novo, mas numa lista com os nirfs envoltos por aspas

lista_de_nirfs = [] ## a esta lista serão adicionados os nirfs do .txt (sem aspas)

for nirf_com_aspas in lista_de_nirfs_com_aspas:
    nirf_sem_aspas = (nirf_com_aspas.split('"')[1]) ## separa quando vir aspas e pega o segundo elemento (index=1), que é o número do nirf
    lista_de_nirfs.append(nirf_sem_aspas) ## adiciona o número do nirf à lista de nirfs

print("10 primeiros nirfs:",lista_de_nirfs[0:10])
print(len(lista_de_nirfs),"nirfs no total")

#-----------------------------------------------------------------------------------------------#

# vamos criar uma tabela para salvar os nirfs já crawleados
# mas, antes, vamos garantir que não há outra tabela conflitante:
deletar1 = 'DROP TABLE IF EXISTS tab_nirfs'
con1 = sqlite3.connect("./db_nirfs.db", check_same_thread=False) ## conecta ao banco de dados "db_nirfs" ou cria se ele não existir
cursor1 = con1.cursor() ## criar cursor pra executar ações como deletar a tabela
cursor1.execute(deletar1) ## deletar a tabela se existir
con1.commit() ## salva pra garantir que deletou

# definindo as colunas da tabela
propriedades_tabela_nirfs = "CREATE TABLE tab_nirfs (nirf_c TEXT, resultado_c TEXT)"
cursor1.execute(propriedades_tabela_nirfs) ## cria a tabela
con1.commit() ## salva pra garantir que criou a tabela

#-----------------------------------------------------------------------------------------------#


# apagar as listas que podem ter sido criadas anteriormente
lista_de_certidoes_baixadas = [] ## a essa lista serão adicionados os links acessados (que resultam em certidões baixadas)
lista_de_downloads_falhados = [] # a essa lista serão adicionados os links que o selenium não conseguir entrar

def crawlear(nirf:str):

    try:

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito') ## abre o chrome em modo anônimo, pois o próprio site sugere isso pra evitar bloqueios
        chrome = webdriver.Chrome(chrome_options=chrome_options)

        # entrar nessa página
        chrome.get("https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/ITR/EmitirPgfn") ## abrir o link   
        time.sleep(5) ## espera 4 segundos só pra garantir que ele vai esperar carregar
        
        # digitar o nirf
        chrome.find_element(By.XPATH, './/*[@id="NI"]').click()
        time.sleep(1)
        chrome.find_element(By.XPATH, './/*[@id="NI"]').send_keys(nirf)
        time.sleep(1)
        chrome.find_element(By.XPATH, './/*[@id="NI"]').send_keys(Keys.ENTER)
        time.sleep(1)
        #chrome.find_element(By.XPATH, './/*[@id="validar"]').click ## clica em "consultar" ao invés de dar ENTER
        time.sleep(10) ## espera um bom tempo pra garantir que vai carregar

        # clicar em "Emissão de nova certidão"
        chrome.find_element(By.XPATH, './/*[@id="FrmSelecao"]/a[2]').click()
        time.sleep(1)
        print("certidão baixada")
        resultado = "Sucesso"

        lista_de_certidoes_baixadas.append(nirf) # adicionar os nirfs a uma lista para contar quantos nirfs foram baixados
    
    except: ## se não conseguir baixar
        lista_de_downloads_falhados.append(nirf) ## para somar 1 ao número de falhas
        print("falha: ",nirf," - nirf adicionado à lista de falhas")
        resultado = "Falha"

    # ao final das iterações, isto será mostrado:
    print("+----------------------------------------------------------------------------------+") ## separar resultados para melhor visualização
    print(len(lista_de_certidoes_baixadas), "certidões foram baixadas")
    print('Número de falhas: ',len(lista_de_downloads_falhados))
    cursor1.execute("INSERT INTO tab_nirfs VALUES (?,?)",(nirf, resultado)) ## adiciona o nirf e seu resultado (se deu certo ou errado) à tabela
    con1.commit() ## salva a tabela

#-----------------------------------------------------------------------------------------------#

# função principal, que executa a função "crawlear" n vezes para baixar as certidões 
def main():
    for cada_nirf in lista_de_nirfs[0:3]: ## essa linha é pra testar com poucos nirfs, só pra não tentar até o final se tiver falhando tudo (comentar/apagar se estiver dando certo)
    #for cada_nirf in lista_de_nirfs: #descomentar se quiser crawlear todos os nirfs
        crawlear(cada_nirf)

# para executar a função principal
if __name__ == '__main__':
    main()

## após a execução, veja os resultados no banco de dados "db_nirfs"
## recomendo baixar o programa "DB Browser for SQLite" e usá-lo para visualizar a tabela com os resultados