#SCRIPT DE MONTAGEM DO DATASET (VERSÃO CORRIGIDA FINAL)
import pandas as pd
import numpy as np
import os

# --- Bloco para garantir o diretório de trabalho ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Diretório de trabalho alterado para: {os.getcwd()}")
except NameError:
    print(f"Executando no diretório: {os.getcwd()}")


files = {
    'benigno.csv': 0, 'dos_attack.csv': 1, 'fuzzing_attack.csv': 2,
    'replay.csv': 3, 'injection.csv': 4
}

#Lista que vai armazenar as features de TODAS as janelas de TODOS os arquivos
all_window_features = []

print("\n--- Iniciando processamento de janelas por arquivo ---")
#1. Loop através de cada arquivo individualmente
for f, label in files.items():
    try:
        print(f"Processando arquivo: '{f}' com Label: {label}")
        temp_df = pd.read_csv(f)
        
        if temp_df.empty:
            print(f"  -> AVISO: Arquivo '{f}' está vazio, pulando.")
            continue

        # Normaliza o timestamp e calcula o Delta_T para o arquivo atual
        temp_df['Timestamp'] = temp_df['Timestamp'] - temp_df['Timestamp'].min()
        temp_df['ID'] = temp_df['ID'].apply(lambda x: int(str(x), 16))
        temp_df.sort_values(by='Timestamp', inplace=True)
        temp_df['Delta_T'] = temp_df.groupby('ID')['Timestamp'].diff().fillna(0)

        # 2. Processamento de janela DENTRO do loop do arquivo
        start_time = temp_df['Timestamp'].min()
        end_time = temp_df['Timestamp'].max()
        window_size = 0.1
        step_size = 0.05
        current_time = start_time

        while current_time + window_size <= end_time:
            window_df = temp_df[(temp_df['Timestamp'] >= current_time) & (temp_df['Timestamp'] < current_time + window_size)]

            if not window_df.empty:
                message_count = len(window_df)
                unique_ids = window_df['ID'].nunique()
                mean_delta_t = window_df['Delta_T'].mean()
                std_delta_t = window_df['Delta_T'].std(ddof=0)
                
                # O rótulo da janela é simplesmente o rótulo do arquivo atual
                window_label = label 
                
                all_window_features.append([
                    message_count, unique_ids, mean_delta_t, std_delta_t, window_label
                ])
            
            current_time += step_size
        print(f"  -> Finalizado. Gerou {len(all_window_features)} janelas até agora.")

    except FileNotFoundError:
        print(f"  -> ERRO: Arquivo '{f}' NÃO ENCONTRADO.")

# 3. Criar o Novo DataFrame com as Features de todos os arquivos combinados
feature_names = ['Message_Count', 'Unique_IDs', 'Mean_Delta_T', 'Std_Delta_T', 'Label']
window_dataset = pd.DataFrame(all_window_features, columns=feature_names).fillna(0)

print("\n\n--- Amostra do Novo Dataset Baseado em Janelas ---")
print(window_dataset.head())
print("\n--- Distribuição das Classes no Novo Dataset ---")
print(window_dataset['Label'].value_counts())

output_filename = 'processed_window_data.csv'
window_dataset.to_csv(output_filename, index=False)
print(f"\nSUCESSO! O dataset foi montado e o novo arquivo '{output_filename}' foi criado.")