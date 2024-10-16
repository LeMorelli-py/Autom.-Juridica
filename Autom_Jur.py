import pandas as pd
import requests
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
import sys
import warnings
import concurrent.futures

warnings.filterwarnings("ignore", category=UserWarning, module="IPython.core.interactiveshell")

def carregar_arquivo():
    arquivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if arquivo:
        entrada_arquivo.delete(0, tk.END)
        entrada_arquivo.insert(0, arquivo)

def processar_dados():
    arquivo = entrada_arquivo.get()
    if not arquivo:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo Excel.")
        return

    try:
        processos = pd.read_excel(arquivo)
        processos = processos.rename(columns={"www": "Processo nº"})
        processos['Processo nº'] = processos['Processo nº'].apply(lambda x: x.replace('.', '').replace('-', ''))
        
        lista = processos["Processo nº"].tolist()
        
        url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search"
        api_key = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
        
        resultados = []
        total_processos = len(lista)
        processos_concluidos = 0

        # Usar ThreadPoolExecutor para processar os dados em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submeter todas as tarefas
            futures = [executor.submit(processar_processos, numero_processo, url, api_key) for numero_processo in lista]
            
            # Processar os resultados à medida que são concluídos
            for future in concurrent.futures.as_completed(futures):
                resultado = future.result()
                if resultado:
                    resultados.append(resultado)
                
                processos_concluidos += 1
                progresso['value'] = (processos_concluidos / total_processos) * 100
                janela.update_idletasks()

        df_resultados = pd.DataFrame(resultados)
        arquivo_saida = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if arquivo_saida:
            df_resultados.to_excel(arquivo_saida, index=False)
            messagebox.showinfo("Sucesso", f"Os resultados foram salvos em '{arquivo_saida}'")
            janela.quit()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def fechar_programa():
    janela.quit()

def alternar_tema():
    global tema_atual
    if tema_atual == "escuro":
        janela.set_theme("arc")
        tema_atual = "claro"
        bg_color = "white"  # Cor de fundo para o tema claro
        style.configure("TLabel", foreground="black")
        style.configure("TButton", foreground="black")
        style.configure("TEntry", foreground="black")
        botao_tema.config(text="☀️", bg="white", fg="black")
        titulo_label.config(fg="#0000FF", bg=bg_color)  # Azul para tema claro, fundo branco
    else:
        janela.set_theme("equilux")
        tema_atual = "escuro"
        bg_color = "#464646"  # Cor de fundo para o tema escuro
        style.configure("TLabel", foreground="white")
        style.configure("TButton", foreground="white")
        style.configure("TEntry", foreground="white")
        botao_tema.config(text="🌙", bg="#464646", fg="white")
        titulo_label.config(fg="#00BFFF", bg=bg_color)  # Azul claro para tema escuro, fundo escuro
    style.configure("Horizontal.TProgressbar")
    janela.configure(bg=bg_color)  # Atualiza a cor de fundo da janela principal

def processar_processos(numero_processo, url, api_key):
    payload = json.dumps({
        "query": {
            "match": {
                "numeroProcesso": numero_processo,     
            }
        }
    })

    headers = {
        'Authorization': f"APIKey {api_key}",
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        dados = response.json()
        if dados['hits']['total']['value'] > 0:
            movimentacoes = dados['hits']['hits'][0]['_source']['movimentos']
            ultimo = movimentacoes[-1]
            return {
                'Processo nº': numero_processo,
                'Código': ultimo.get('codigo'),
                'Nome': ultimo.get('nome'),
                'Data/Hora': ultimo.get('dataHora'),
                'Complementos': json.dumps(ultimo.get('complementosTabelados', []), ensure_ascii=False)
            }
    return None

# Criar a janela principal com tema
janela = ThemedTk(theme="equilux")  # Tema escuro inicial
janela.title("AutoJur")
janela.geometry("400x350")  # Aumentado a altura para acomodar o título

tema_atual = "escuro"


# Configurar cores para o tema escuro
bg_color = "#464646"
fg_color = "#FFFFFF"  # Branco puro para maior contraste
janela.configure(bg=bg_color)

# Criar e posicionar os widgets
frame = ttk.Frame(janela, padding="20")
frame.pack(expand=True, fill=tk.BOTH)

# Título personalizado com símbolo de balança
titulo_label = tk.Label(janela, text="⚖️ AutoJur", font=("Arial", 20, "bold"), fg="#00BFFF", bg=bg_color)
titulo_label.pack(pady=10)

# Estilo personalizado para widgets
style = ttk.Style()
style.configure("TLabel", foreground=fg_color)
style.configure("TButton", foreground=fg_color)
style.configure("TEntry", foreground=fg_color)
style.configure("Horizontal.TProgressbar")

# Botão para alternar tema
botao_tema = tk.Button(janela, text="🌙", command=alternar_tema, font=("Arial", 10), width=3, height=1, bg=bg_color, fg=fg_color)
botao_tema.place(relx=1.0, x=-5, y=5, anchor="ne")

ttk.Label(frame, text="Arquivo Excel:").pack(pady=5)
entrada_arquivo = ttk.Entry(frame, width=50)
entrada_arquivo.pack(pady=5)

botao_carregar = ttk.Button(frame, text="Carregar Arquivo", command=carregar_arquivo, width=20)
botao_carregar.pack(pady=5)

botao_processar = ttk.Button(frame, text="Processar Dados", command=processar_dados, width=20)
botao_processar.pack(pady=5)

progresso = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate', style="Horizontal.TProgressbar")
progresso.pack(pady=10)

botao_fechar = ttk.Button(frame, text="Fechar Programa", command=fechar_programa, width=20)
botao_fechar.pack(pady=5)

# Iniciar o loop principal
janela.mainloop()
sys.exit()
