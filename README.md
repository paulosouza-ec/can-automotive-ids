# Rede CAN e Segurança: Detecção de Intrusão com Machine Learning 🚗🛡️

Bem-vindo! Este projeto transforma uma simples Raspberry Pi em um **Guardião Inteligente** para a rede CAN do seu veículo, usando o poder do Machine Learning para detectar ciberataques em tempo real.

Cansado da ideia de que as redes automotivas são vulneráveis? 😟 Nós também! Por isso, criamos um Sistema de Detecção de Intrusão (IDS) completo, desde a simulação dos ataques até a detecção ao vivo.

[cite_start]**Autores:** Danilo A. Barbosa Nogueira, Paulo S. Galdino de Souza [cite: 3]

![Matriz de Confusão do Projeto](https://raw.githubusercontent.com/galdinopaulo/CAN-Bus-IDS-using-ML/main/metricas/matriz_confusao.png)

---

## ✨ A Grande Ideia (Como Funciona?)

Em vez de analisar pacotes CAN um por um (o que seria lento e ineficiente!), nosso sistema observa o **comportamento do tráfego** em pequenas janelas de tempo.

[cite_start]A cada 100 milissegundos, extraímos a "personalidade" da rede com base em 4 características-chave[cite: 64, 173]:
1.  [cite_start]**Contagem de Mensagens:** O volume de tráfego está normal ou suspeitosamente alto? [cite: 66]
2.  **Contagem de IDs Únicos:** Estamos vendo os "participantes" de sempre na conversa ou há estranhos na rede?
3.  [cite_start]**Tempo Médio entre Mensagens:** A comunicação está fluindo no ritmo esperado? [cite: 67]
4.  **Desvio Padrão do Tempo:** O ritmo da comunicação está estável ou caótico?

[cite_start]Essas características alimentam nosso cérebro digital — um modelo **Random Forest** treinado — que classifica o tráfego como `Benigno` ou como um dos `Ataques` conhecidos com uma **acurácia de 98.5%**! [cite: 83, 200]

---

## 👾 Inimigos Detectados

[cite_start]Nosso IDS foi treinado para identificar e classificar 4 tipos de ciberataques veiculares[cite: 54]:

-   [cite_start]**🌪️ Ataque de Negação de Serviço (DoS):** Quando o barramento é inundado com lixo para impedir a comunicação. [cite: 55]
-   [cite_start]**💣 Ataque de Fuzzing:** Mensagens aleatórias e malformadas tentando encontrar uma brecha no sistema. [cite: 56]
-   [cite_start]**🎭 Ataque de Injeção (Spoofing):** Um impostor se passando por uma ECU legítima para enviar comandos perigosos. [cite: 57]
-   [cite_start]**🔁 Ataque de Replay:** Uma sequência de comandos legítimos gravada e reenviada em um momento inoportuno. [cite: 58]

---

## 🛠️ O Arsenal (Tecnologias Utilizadas)

-   **🐍 Linguagem:** Python 3
-   [cite_start]**🧠 Machine Learning:** Scikit-Learn, Pandas, NumPy [cite: 52]
-   [cite_start]**🚗 Comunicação CAN:** Biblioteca `python-can` [cite: 51]
-   [cite_start]**💻 Hardware:** Raspberry Pi + Módulo CAN (Ex: MCP2515) [cite: 48]

---

## 📈 Resultados em Destaque

A performance do modelo é excelente. Com a acurácia acima de 98%, A matriz de confusão abaixo mostra que a maioria dos ataques, especialmente **Replay e Injection, são detectados com 100% de precisão**. As curvas ROC e de Precisão-Recall (com pontuações AUC e AP > 0.99) confirmam que o sistema é extremamente confiável, gerando poucos alarmes falsos.

![Matriz de Confusão do Projeto](https://i.imgur.com/fKu3bMI.png)

---

## 🚀 Guia de Início Rápido (Rode em 5 Minutos!)

Quer ver a mágica acontecer? Siga estes passos para rodar o detector com nosso modelo já treinado.

#### 1. Prepare o Ambiente

```bash
# Clone este repositório
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio

# Crie e ative um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instale todas as dependências mágicas
pip install -r 
```

#### 2. Ligue a Interface CAN

O sistema usa a interface `can0` por padrão. Ative-a com o bitrate da sua rede (ex: 500 kbit/s).

```bash
# Lembre-se de usar 'sudo'!
sudo ip link set can0 up type can bitrate 500000
```

#### 3. Inicie o Guardião! 🛡️

Execute o classificador em tempo real. Ele carregará o `trained_model.joblib` e começará a monitorar a rede.

```bash
python realtime_classifier.py
```
Você verá a mensagem: `Monitorando o barramento CAN...`

#### 4. Simule um Ataque! 💥

Com o guardião rodando, abra um **novo terminal**, ative o ambiente virtual (`source venv/bin/activate`) e dispare um dos ataques.

```bash
# Exemplo: Ataque de DoS
python ataques/dos.py
```

Volte para o terminal do guardião e veja os alertas de detecção aparecerem em tempo real!

---

## 🥋 Quer ser um Mestre? (Treine seu Próprio Modelo)

Se você quiser treinar o modelo com seus próprios dados, o caminho é este:

1.  **Capture seus Dados (`logger.py`):**
    -   Use o `logger.py` para gravar o tráfego da sua rede CAN em arquivos `.csv`.
    -   Gere um arquivo para o tráfego benigno e um para cada tipo de ataque que você simular.

2.  **Processe os Dados (`main.py`):**
    -   Coloque seus arquivos `.csv` na pasta `dataset/`.
    -   Rode `python main.py` para aplicar a engenharia de features e gerar o `processed_window_data.csv`.

3.  **Treine o Cérebro (`treino.py`):**
    -   Rode `python treino.py` para treinar o modelo com seus dados.
    -   Ao final, um novo arquivo `trained_model.joblib` será salvo, pronto para ser usado pelo `realtime_classifier.py`.
