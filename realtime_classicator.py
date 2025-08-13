import joblib
import can
import time
import pandas as pd
import numpy as np
import warnings

# Ignorar os warnings específicos do sklearn
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


# --- 1. Carrega o modelo treinado com features de janela ---
try:
    MODEL_FILE = 'trained_model.joblib'  # Certifique-se que o nome do arquivo está correto
    model = joblib.load(MODEL_FILE)
    print(f"Modelo '{MODEL_FILE}' carregado com sucesso.")
except FileNotFoundError:
    print(f"ERRO: Modelo '{MODEL_FILE}' não encontrado. Execute o script de treinamento primeiro.")
    exit()

# Parâmetros da janela (DEVEM SER OS MESMOS USADOS NO TREINAMENTO)
WINDOW_SIZE = 0.1  # 100ms
STEP_SIZE = 0.05   # Analisar a cada 50ms

# Dicionário para traduzir previsões
label_to_name_map = {
    0: 'Benigno', 1: 'Ataque de DoS', 2: 'Ataque de Fuzzing',
    3: 'Ataque de Replay', 4: 'Ataque Injection'
}

# --- 2. Inicialização do barramento e do buffer ---
try:
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
    print("Interface CAN 'can0' iniciada.")
except Exception as e:
    print(f"ERRO ao iniciar a interface CAN: {e}. Verifique a configuração.")
    exit()

# O buffer irá armazenar as mensagens recentes em um DataFrame do Pandas
message_buffer = pd.DataFrame(columns=['Timestamp', 'ID', 'DLC'])
print("Monitorando o barramento CAN... Pressione Ctrl+C para parar.")

# --- 3. Loop principal de detecção ---
try:
    while True:
        # Coleta mensagens por um curto período de tempo (o tamanho do nosso passo)
        start_collection_time = time.time()
        temp_messages = []
        while time.time() - start_collection_time < STEP_SIZE:
            msg = bus.recv(timeout=0.01)  # Timeout curto para não bloquear
            if msg:
                temp_messages.append({
                    'Timestamp': msg.timestamp,
                    'ID': msg.arbitration_id,
                    'DLC': msg.dlc
                })

        # Adiciona as novas mensagens ao buffer
        if temp_messages:
            # Ignora colunas vazias para evitar warnings futuros
            df_temp = pd.DataFrame(temp_messages)
            message_buffer = pd.concat([message_buffer, df_temp], ignore_index=True)

        # Remove mensagens antigas do buffer para não consumir memória infinita
        current_time = time.time()
        message_buffer = message_buffer[message_buffer['Timestamp'] >= current_time - WINDOW_SIZE]

        # Se o buffer não estiver vazio, calcula as features e faz a predição
        if not message_buffer.empty:
            # --- Cálculo de Features em Tempo Real ---
            buffer_sorted = message_buffer.sort_values(by='Timestamp')
            buffer_sorted['Delta_T'] = buffer_sorted.groupby('ID')['Timestamp'].diff().fillna(0)

            message_count = len(buffer_sorted)
            unique_ids = buffer_sorted['ID'].nunique()
            mean_delta_t = buffer_sorted['Delta_T'].mean()
            std_delta_t = buffer_sorted['Delta_T'].std(ddof=0)

            # ✅ Correção: agora usando np.nan_to_num() para lidar com NaN ou inf
            features = np.nan_to_num(np.array([
                [message_count, unique_ids, mean_delta_t, std_delta_t]
            ]))

            # --- Predição ---
            prediction = model.predict(features)
            result_label = prediction[0]

            if result_label != 0:
                attack_name = label_to_name_map.get(result_label, "Ataque Desconhecido")
                print(f"[{time.strftime('%H:%M:%S')}] ALERTA: Comportamento de {attack_name} detectado na janela!")

except KeyboardInterrupt:
    print("\nDetecção encerrada pelo usuário.")
finally:
    bus.shutdown()
    print("Interface CAN desligada.")
