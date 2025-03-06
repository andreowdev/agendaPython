import tkinter as tk
from tkinter import ttk
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import threading
import time
from plyer import notification
from datetime import datetime, timedelta

# Lista de atividades
atividades = [
    ("07:00 - 08:00", "Afazeres (café da manhã, banho, etc.)"),
    ("08:00 - 12:00", "Programação Micro SaaS (Next.js)"),
    ("12:00 - 13:00", "Almoço"),
    ("13:00 - 16:00", "Estudo de PHP"),
    ("16:00 - 17:30", "Tarefas da faculdade"),
    ("17:30 - 19:00", "Se arrumar para a faculdade"),
    ("19:00 - 22:30", "Faculdade")
]

# Criando a interface principal
root = tk.Tk()
root.title("Gerenciador de Rotina")
root.geometry("500x350")

# Criando a Treeview
colunas = ("Horário", "Atividade", "Status")
lista_atividades = ttk.Treeview(root, columns=colunas, show="headings")

# Definindo cabeçalhos
for col in colunas:
    lista_atividades.heading(col, text=col)
    lista_atividades.column(col, width=150)

# Adicionando os dados
for horario, atividade in atividades:
    lista_atividades.insert("", tk.END, values=(horario, atividade, "Não Concluído"))

lista_atividades.pack(pady=10)

# Exibindo o tempo restante
tempo_restante_label = tk.Label(root, text="Tempo até próxima atividade: 00:00")
tempo_restante_label.pack(pady=10)

# Botão para marcar como concluído
def marcar_concluido():
    selecionado = lista_atividades.selection()
    if selecionado:
        for item in selecionado:
            lista_atividades.item(item, values=(lista_atividades.item(item)['values'][0], lista_atividades.item(item)['values'][1], "Concluído"))

botao_concluir = tk.Button(root, text="Marcar como Concluído", command=marcar_concluido)
botao_concluir.pack()

# Botão para marcar como "Não Concluído"
def marcar_nao_concluido():
    selecionado = lista_atividades.selection()
    if selecionado:
        for item in selecionado:
            lista_atividades.item(item, values=(lista_atividades.item(item)['values'][0], lista_atividades.item(item)['values'][1], "Não Concluído"))

botao_nao_concluido=tk.Button(root, text="Marcar como não concluído", command=marcar_nao_concluido)
botao_nao_concluido.pack()

# Oculta a janela no início
root.withdraw()

# Função para calcular o tempo restante
# Função para calcular o tempo restante
# Função para calcular o tempo restante
def calcular_tempo_restante():
    while True:
        agora = datetime.now()
        proxima_atividade = None
        
        # Encontrar a próxima atividade
        for horario, _ in atividades:
            inicio_horario = horario.split(" - ")[0]
            inicio_dt = datetime.strptime(inicio_horario, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day)

            # Se a atividade ainda não aconteceu, define ela como próxima
            if agora < inicio_dt:
                proxima_atividade = inicio_dt
                break

        # Se houver uma próxima atividade
        if proxima_atividade:
            # Calcular o tempo restante
            tempo_restante = proxima_atividade - agora
            horas_restantes, segundos_restantes = divmod(tempo_restante.seconds, 3600)
            minutos_restantes, _ = divmod(segundos_restantes, 60)

            # Exibir o tempo restante de forma legível
            tempo_restante_label.config(text=f"Tempo até próxima atividade: {horas_restantes:02}:{minutos_restantes:02}")
        
        else:
            # Se não houver mais atividades para o dia, calcula o tempo até a primeira atividade do próximo dia
            primeiro_horario = atividades[0][0].split(" - ")[0]
            primeiro_dt = datetime.strptime(primeiro_horario, "%H:%M").replace(year=agora.year, month=agora.month, day=agora.day) + timedelta(days=1)
            
            # Calcular o tempo restante até o primeiro horário do próximo dia
            tempo_restante = primeiro_dt - agora
            horas_restantes, segundos_restantes = divmod(tempo_restante.seconds, 3600)
            minutos_restantes, _ = divmod(segundos_restantes, 60)

            tempo_restante_label.config(text=f"Tempo até próxima atividade: {horas_restantes:02}:{minutos_restantes:02}")
        
        time.sleep(60)

# Rodar a função de cálculo de tempo em segundo plano
thread_tempo_restante = threading.Thread(target=calcular_tempo_restante, daemon=True)
thread_tempo_restante.start()

# Criando o ícone para a bandeja do sistema
def criar_icone():
    image = Image.new("RGB", (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill=(0, 0, 255))

    menu = Menu(MenuItem("Abrir", mostrar_janela), MenuItem("Sair", sair_app))
    return Icon("notificador", image, "Gerenciador de Rotina", menu)

# Função para exibir a janela
def mostrar_janela(icon, item):
    root.deiconify()  # Exibe a janela novamente
    root.lift()  # Coloca a janela em primeiro plano

# Função para sair do aplicativo
def sair_app(icon, item):
    icon.stop()
    root.quit()

# Criar função para notificações
def verificar_notificacoes():
    while True:
        agora = datetime.now().strftime("%H:%M")
        for horario, atividade in atividades:
            fim_horario = horario.split(" - ")[1]
            fim_dt = datetime.strptime(fim_horario, "%H:%M") - timedelta(minutes=5)
            if agora == fim_dt.strftime("%H:%M"):
                notification.notify(
                    title="Lembrete de Atividade",
                    message=f"Está quase na hora de finalizar: {atividade}",
                    timeout=10
                )
        time.sleep(60)

# Rodar notificações em segundo plano
thread_notificacao = threading.Thread(target=verificar_notificacoes, daemon=True)
thread_notificacao.start()

# Criar e rodar o ícone da bandeja do sistema
icone = criar_icone()
thread_icone = threading.Thread(target=icone.run, daemon=True)
thread_icone.start()

# Iniciar o loop principal do Tkinter
root.mainloop()
