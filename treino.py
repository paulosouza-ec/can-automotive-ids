import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)
from sklearn.preprocessing import label_binarize
from itertools import cycle
import joblib
from sklearn.model_selection import cross_validate

#Carregar o dataset de janelas
try:
    print("Carregando o dataset 'processed_window_data.csv'...")
    df = pd.read_csv('processed_window_data.csv')
    print("Dataset carregado com sucesso.")
except FileNotFoundError:
    print("ERRO: Arquivo 'processed_window_data.csv' não encontrado.")
    print("Por favor, execute o script de pré-processamento primeiro.")
    exit()

#Definir features (X) e alvo (y)
X = df.drop('Label', axis=1)
y = df['Label']
classes = sorted(y.unique())
n_classes = len(classes)

#Dicionário para mapear labels numéricos para nomes legíveis
label_to_name_map = {
    0: 'Benign', 1: 'DoS_Attack', 2: 'Fuzzing_Attack',
    3: 'Replay_Attack', 4: 'Injection_attack'
}
target_names = [label_to_name_map[i] for i in classes]

'''  - Treinamento dos dados '''

#Dividir os dados em conjuntos de treino e teste
#'stratify=y' garante que os conjuntos de treino e teste tenham a mesma proporção de classes
print("Dividindo dados em treino e teste...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


#Inicializar o classificador RandomForest
model = RandomForestClassifier(n_estimators=150, class_weight='balanced', random_state=42)

print("\nTreinando o modelo RandomForest...")
model.fit(X_train, y_train)
print("Treinamento concluído.")


''' Avaliação do modelo '''

#Fazer predições no conjunto de teste
print("Realizando predições no conjunto de teste...")
y_pred = model.predict(X_test)
#Obter as probabilidades para as curvas ROC e P-R
y_pred_proba = model.predict_proba(X_test)

#Calcular e imprimir o relatório de classificação principal
print("\n--- Relatório de Classificação Principal ---")
acuracia = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=target_names)
print(f"Acurácia Geral: {acuracia:.4f}")
print("\nRelatório Detalhado por Classe:")
print(report)

''' Geração das métricas visuais '''

#Matriz de Confusão
print("\nGerando Matriz de Confusão...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(12, 9))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
plt.title('Matriz de Confusão', fontsize=16)
plt.ylabel('Classe Verdadeira', fontsize=12)
plt.xlabel('Classe Prevista', fontsize=12)
plt.savefig('confusion_matrix.png', bbox_inches='tight', dpi=300)
print("Figura da Matriz de Confusão salva como 'confusion_matrix.png'")
plt.close() #Fecha a figura para liberar memória

#Binarizar o output para as curvas ROC e P-R (necessário para abordagem One-vs-Rest)
y_test_binarized = label_binarize(y_test, classes=classes)

#Curva ROC e AUC (Multiclass - One-vs-Rest)
print("\nGerando Curva ROC (One-vs-Rest)...")
fpr = dict()
tpr = dict()
roc_auc = dict()

for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_binarized[:, i], y_pred_proba[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

#Plotar todas as curvas ROC em um único gráfico
plt.figure(figsize=(12, 9))
colors = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label=f'Curva ROC da classe {target_names[i]} (AUC = {roc_auc[i]:0.3f})')

plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Classificador Aleatório')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taxa de Falsos Positivos', fontsize=12)
plt.ylabel('Taxa de Verdadeiros Positivos', fontsize=12)
plt.title('Curva ROC - Multiclasse (One-vs-Rest)', fontsize=16)
plt.legend(loc="lower right")
plt.grid(True)
plt.savefig('roc_curve_multiclass.png', bbox_inches='tight', dpi=300)
print("Figura da Curva ROC salva como 'roc_curve_multiclass.png'")
plt.close()

#Curva de Precisão-Recall (Multiclass - One-vs-Rest)
print("\nGerando Curva de Precisão-Recall...")
precision = dict()
recall = dict()
average_precision = dict()

for i in range(n_classes):
    precision[i], recall[i], _ = precision_recall_curve(y_test_binarized[:, i], y_pred_proba[:, i])
    average_precision[i] = average_precision_score(y_test_binarized[:, i], y_pred_proba[:, i])

#Plotar todas as curvas de Precisão-Recall
plt.figure(figsize=(12, 9))
colors = cycle(['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
for i, color in zip(range(n_classes), colors):
    plt.plot(recall[i], precision[i], color=color, lw=2,
             label=f'Curva P-R da classe {target_names[i]} (AP = {average_precision[i]:0.3f})')

plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precisão', fontsize=12)
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title('Curva de Precisão-Recall - Multiclasse', fontsize=16)
plt.legend(loc="best")
plt.grid(True)
plt.savefig('precision_recall_curve_multiclass.png', bbox_inches='tight', dpi=300)
print("Figura da Curva de Precisão-Recall salva como 'precision_recall_curve_multiclass.png'")
plt.close()

''' Salvamento do modelo treinado para usar na classificação real.'''

nome_arquivo_modelo = 'trained_model.joblib'
print(f"\nSalvando o modelo treinado em '{nome_arquivo_modelo}'...")
joblib.dump(model, nome_arquivo_modelo)
print("Modelo salvo com sucesso!")
print("\nProcesso concluído.")


''' Validação Cruzada '''

print("\nExecutando validação cruzada com 5 folds...")

#Avaliar acurácia, precisão macro, recall macro e F1 macro
scoring = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
cv_results = cross_validate(
    model, X, y, cv=5, scoring=scoring, return_train_score=True, n_jobs=-1
)

#Mostrar resultados médios e desvios
print("\n--- Resultados da Validação Cruzada ---")
for metric in scoring:
    train_mean = cv_results[f'train_{metric}'].mean()
    test_mean = cv_results[f'test_{metric}'].mean()
    test_std = cv_results[f'test_{metric}'].std()
    print(f"{metric.capitalize():<20} | Treino: {train_mean:.4f} | Validação: {test_mean:.4f} ± {test_std:.4f}")
