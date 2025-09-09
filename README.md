# Sobre o Projeto
Este projeto apresenta um pipeline completo para um Sistema de Detecção de Intrusão (IDS) para redes CAN (Controller Area Network), comumente utilizadas em veículos automotivos. A solução é baseada em Machine Learning e foi projetada para ser executada em hardware de baixo custo, como uma Raspberry Pi.

O objetivo principal é demonstrar a viabilidade de monitorar o tráfego do barramento CAN em tempo real para identificar e classificar diferentes tipos de ciberataques, aumentando a segurança intraveicular. Este trabalho foi desenvolvido no contexto da disciplina IF747 - Redes Automotivas.

Autores: psgs, dabn.


Com certeza! Baseado nos arquivos do seu projeto, preparei uma documentação completa e organizada no formato README para o seu repositório no GitHub.

Este README explica o propósito do projeto, a metodologia utilizada, as tecnologias, e fornece um guia passo a passo para que outros usuários possam executá-lo.

Rede CAN e Segurança: Da Implementação à Detecção de Intrusão com Machine Learning
Sobre o Projeto
Este projeto apresenta um pipeline completo para um Sistema de Detecção de Intrusão (IDS) para redes CAN (Controller Area Network), comumente utilizadas em veículos automotivos. A solução é baseada em Machine Learning e foi projetada para ser executada em hardware de baixo custo, como uma Raspberry Pi.

O objetivo principal é demonstrar a viabilidade de monitorar o tráfego do barramento CAN em tempo real para identificar e classificar diferentes tipos de ciberataques, aumentando a segurança intraveicular. Este trabalho foi desenvolvido no contexto da disciplina IF747 - Redes Automotivas.

Autores: Danilo A. Barbosa Nogueira, Paulo S. Galdino de Souza

#Metodologia

A abordagem do projeto pode ser dividida em quatro etapas principais:

1. Geração de Datasets
Para treinar um modelo de Machine Learning, é crucial ter dados de alta qualidade. Nesta etapa, foram gerados cinco conjuntos de dados distintos:

Tráfego Benigno: Captura do tráfego normal e esperado em uma rede CAN simulada.

Tráfego de Ataque: Simulação e captura de quatro tipos comuns de ataques em redes veiculares:

Negação de Serviço (DoS): Inunda o barramento com mensagens de alta prioridade (dos.py), impedindo a comunicação legítima.

Fuzzing: Envia mensagens com IDs e dados aleatórios para identificar vulnerabilidades (fuzzing_attack.py).

Injeção (Spoofing): Insere mensagens falsas com IDs válidos para manipular o comportamento do veículo (injection.py).

Replay: Grava uma sequência de mensagens legítimas e as retransmite posteriormente para executar uma ação maliciosa (replay.py).

O script logger.py foi utilizado para capturar todo o tráfego (benigno e de ataques) e salvá-lo em formato .csv.

2. Engenharia de Features
   
O modelo não analisa pacotes CAN individualmente. Em vez disso, ele utiliza uma abordagem baseada em janelas de tempo para extrair características estatísticas do tráfego. O script main.py realiza este pré-processamento:

Janelamento: O fluxo de dados é segmentado em janelas de 100ms, com um passo de 50ms (ou seja, há uma sobreposição de 50%).

Extração de Features: Para cada janela de tempo, as seguintes quatro features são calculadas:

Message_Count: Número total de mensagens na janela.

Unique_IDs: Número de IDs de arbitração únicos na janela.

Mean_Delta_T: O tempo médio entre mensagens consecutivas para um mesmo ID.

Std_Delta_T: O desvio padrão do tempo entre mensagens consecutivas para um mesmo ID.

Este processo transforma os dados brutos em um formato vetorial estruturado, que é salvo em processed_window_data.csv.
