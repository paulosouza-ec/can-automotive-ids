import can
import csv
import time

# --- Parâmetros do Logger ---

# Nome da interface CAN na Raspberry Pi.
CAN_INTERFACE = 'can0'

# Duração da captura em segundos.
LOG_DURATION_SECONDS = 30

# Nome do arquivo de saída
#mudar aqui para cada tipo de ataque
OUTPUT_FILENAME = 'injection.csv'

# --- Lógica do Logger ---

def log_can_traffic():
    """
    Escuta o tráfego do barramento CAN por um período determinado e
    salva todas as mensagens recebidas em um arquivo CSV.
    """
    print(f"Iniciando a captura de dados do barramento '{CAN_INTERFACE}'...")
    print(f"A captura durará {LOG_DURATION_SECONDS} segundos.")
    print(f"Os dados serão salvos em '{OUTPUT_FILENAME}'.")
    
    bus = None
    try:
        # Inicializa a conexão com o barramento CAN
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        
        # Abre o arquivo CSV para escrita
        with open(OUTPUT_FILENAME, 'w', newline='') as csvfile:
            # Define os nomes das colunas (cabeçalho)
            fieldnames = ['Timestamp', 'ID', 'IsExtended', 'DLC', 'Data']
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(fieldnames) # Escreve o cabeçalho no arquivo
            
            start_time = time.time()
            message_count = 0
            
            # Loop que captura mensagens pela duração definida
            while time.time() - start_time < LOG_DURATION_SECONDS:
                # bus.recv() aguarda por uma mensagem. O timeout evita que ele trave.
                msg = bus.recv(timeout=1.0)
                
                if msg is not None:
                    # Escreve as informações da mensagem como uma nova linha no CSV
                    csv_writer.writerow([
                        msg.timestamp,
                        hex(msg.arbitration_id),
                        msg.is_extended_id,
                        msg.dlc,
                        msg.data.hex().upper() # Salva os dados em formato hexadecimal
                    ])
                    message_count += 1
            
        print("\n--- Captura Finalizada ---")
        print(f"Total de mensagens capturadas: {message_count}")
        print(f"Log salvo em '{OUTPUT_FILENAME}'.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        
    finally:
        if bus:
            bus.shutdown()
            print("Conexão com o barramento CAN foi encerrada.")

if __name__ == "__main__":
    log_can_traffic()