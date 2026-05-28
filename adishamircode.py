"""
=============================================================================
ESQUEMA DE COMPARTILHAMENTO DE SEGREDO DE SHAMIR
Aplicação prática das Diferenças Divididas de Newton
=============================================================================

Conceito:
    Um segredo S é codificado como o termo independente de um polinômio
    aleatório de grau (t-1), onde t é o número mínimo de partes necessárias
    para reconstruir o segredo (threshold).

    f(x) = S + a1*x + a2*x² + ... + a(t-1)*x^(t-1)

    Cada participante recebe um ponto (xi, f(xi)).
    Com t ou mais pontos, usamos o Método de Newton (Diferenças Divididas)
    para reconstruir o polinômio e encontrar f(0) = S.

    Nota: O método de Lagrange está comentado neste arquivo para referência
    e comparação entre os dois métodos de interpolação.

Nenhuma biblioteca externa de interpolação é utilizada.
Toda a lógica matemática é construída passo a passo.
=============================================================================
"""

import random  # Biblioteca para gerar números aleatórios (coeficientes do polinômio)
from typing import List, Tuple  # Tipagem para listas e tuplas


# =============================================================================
# ETAPA 1: Construção do Polinômio Aleatório
# =============================================================================

def gerar_polinomio(segredo: int, grau: int) -> List[int]:
    """
    Gera os coeficientes de um polinômio aleatório onde:
    - coeficientes[0] = segredo (termo independente)
    - coeficientes[1..grau] = valores aleatórios

    Polinômio resultante: f(x) = segredo + c1*x + c2*x² + ... + c(grau)*x^grau
    """
    # O primeiro coeficiente (termo independente) é o próprio segredo
    coeficientes = [segredo]

    # Gera coeficientes aleatórios para os termos de grau 1 até 'grau'
    for i in range(grau):
        # Cada coeficiente é um inteiro aleatório entre 1 e 256
        coeficientes.append(random.randint(1, 256))

    # Monta a representação visual do polinômio gerado
    termos_str = [f"{coeficientes[0]}"]  # Começa com o termo independente
    for i in range(1, len(coeficientes)):
        if i == 1:
            termos_str.append(f"{coeficientes[i]}*x")  # Termo de grau 1
        else:
            termos_str.append(f"{coeficientes[i]}*x^{i}")  # Termos de grau >= 2
    polinomio_str = " + ".join(termos_str)  # Junta todos os termos com "+"

    # Imprime o polinômio aleatório gerado
    print(f"\n  >>> Polinômio aleatório gerado: f(x) = {polinomio_str}")
    print(f"      (O segredo {segredo} está escondido no termo independente)\n")

    return coeficientes  # Retorna a lista de coeficientes


def avaliar_polinomio(coeficientes: List[int], x: int) -> int:
    """
    Avalia o polinômio no ponto x usando o método direto:
    f(x) = c0 + c1*x + c2*x² + ... + cn*x^n

    Cada termo é calculado individualmente para clareza didática.
    """
    resultado = 0  # Acumulador para a soma dos termos

    # Percorre cada coeficiente com seu respectivo expoente
    for expoente, coeficiente in enumerate(coeficientes):
        # Calcula o termo: coeficiente * x^expoente
        termo = coeficiente * (x ** expoente)
        # Soma o termo ao resultado acumulado
        resultado += termo

    return resultado  # Retorna f(x) = valor do polinômio no ponto x


# =============================================================================
# ETAPA 2: Geração dos Shares (Partes do Segredo)
# =============================================================================

def gerar_shares(segredo: int, total_shares: int, threshold: int) -> List[Tuple[int, int]]:
    """
    Gera as partes do segredo avaliando o polinômio em pontos x = 1, 2, ..., n.

    Parâmetros:
        segredo: o valor secreto a ser compartilhado
        total_shares: número total de partes geradas
        threshold: número mínimo de partes para reconstruir (grau + 1)
    """
    # O grau do polinômio é threshold - 1
    grau = threshold - 1
    # Gera o polinômio aleatório com o segredo embutido (já imprime o polinômio)
    coeficientes = gerar_polinomio(segredo, grau)

    # Exibe informações da construção do polinômio
    print("=" * 60)
    print("ETAPA 1: CONSTRUÇÃO DO POLINÔMIO")
    print("=" * 60)
    print(f"\n  Segredo (S) = {segredo}")  # Mostra o segredo original
    print(f"  Threshold (t) = {threshold}")  # Mostra o mínimo de shares necessários
    print(f"  Grau do polinômio = t - 1 = {grau}")  # Grau = threshold - 1
    print(f"\n  Coeficientes gerados:")
    print(f"    c0 (segredo) = {coeficientes[0]}")  # c0 = segredo
    # Exibe cada coeficiente aleatório gerado
    for i in range(1, len(coeficientes)):
        print(f"    c{i} (aleatório) = {coeficientes[i]}")

    # Reconstrói a string do polinômio para exibição
    termos_str = [f"{coeficientes[0]}"]  # Termo independente
    for i in range(1, len(coeficientes)):
        if i == 1:
            termos_str.append(f"{coeficientes[i]}*x")  # Coeficiente * x
        else:
            termos_str.append(f"{coeficientes[i]}*x^{i}")  # Coeficiente * x^i
    polinomio_str = " + ".join(termos_str)  # Concatena com " + "
    print(f"\n  Polinômio completo: f(x) = {polinomio_str}")

    # Início da geração dos shares
    print("\n" + "=" * 60)
    print("ETAPA 2: GERAÇÃO DOS SHARES")
    print("=" * 60)
    print(f"\n  Avaliando f(x) para x = 1, 2, ..., {total_shares}:\n")

    shares = []  # Lista que armazenará os shares (pares de pontos)

    # Para cada participante (x = 1, 2, ..., total_shares)
    for x in range(1, total_shares + 1):
        # Avalia o polinômio no ponto x para obter y = f(x)
        y = avaliar_polinomio(coeficientes, x)
        # Armazena o par (x, y) como share
        shares.append((x, y))

        # Mostra o cálculo detalhado de f(x) para fins didáticos
        termos_calc = []  # Lista dos termos do cálculo
        for exp, coef in enumerate(coeficientes):
            # Monta cada termo: coeficiente * x^expoente
            termos_calc.append(f"{coef}*{x}^{exp}")
        calculo = " + ".join(termos_calc)  # Junta os termos
        print(f"    f({x}) = {calculo} = {y}")  # Mostra a expressão e resultado
        print(f"    → Share {x}: ({x}, {y})")  # Mostra o share gerado
        print()

    return shares  # Retorna lista de todos os shares


# =============================================================================
# ETAPA 3 (COMENTADA): Interpolação de Lagrange (Reconstrução do Segredo)
# =============================================================================
# O método de Lagrange foi substituído pelo método de Newton (Diferenças
# Divididas) abaixo. O código de Lagrange está comentado para referência.
# =============================================================================

# def calcular_base_lagrange(j: int, x_alvo: int, pontos_x: List[int]) -> float:
#     """
#     Calcula o j-ésimo polinômio base de Lagrange L_j(x_alvo).
#
#     Fórmula:
#                  ∏ (x_alvo - x_m)
#         L_j = ─────────────────────   para m ≠ j
#                  ∏ (x_j - x_m)
#
#     Retorna o valor numérico de L_j avaliado em x_alvo.
#     """
#     numerador = 1  # Inicializa o produto do numerador
#     denominador = 1  # Inicializa o produto do denominador
#
#     # Percorre todos os pontos, exceto o j-ésimo
#     for m in range(len(pontos_x)):
#         if m != j:  # Pula quando m == j (condição da fórmula)
#             # Multiplica (x_alvo - x_m) ao numerador
#             numerador *= (x_alvo - pontos_x[m])
#             # Multiplica (x_j - x_m) ao denominador
#             denominador *= (pontos_x[j] - pontos_x[m])
#
#     # Retorna L_j(x_alvo) = numerador / denominador
#     return numerador / denominador


# def interpolar_lagrange(shares: List[Tuple[int, int]], verbose: bool = True) -> float:
#     """
#     Reconstrói f(0) usando Interpolação de Lagrange.
#
#     Fórmula geral:
#         f(x) = Σ y_j * L_j(x)
#
#     Para encontrar o segredo, avaliamos em x = 0:
#         f(0) = Σ y_j * L_j(0)
#
#     Onde L_j(0) = ∏(m≠j) (0 - x_m) / (x_j - x_m)
#     """
#     # Extrai as coordenadas x de cada share
#     pontos_x = [share[0] for share in shares]
#     # Extrai as coordenadas y de cada share
#     pontos_y = [share[1] for share in shares]
#     # Número total de pontos disponíveis
#     n = len(shares)
#
#     if verbose:
#         print("=" * 60)
#         print("ETAPA 3: INTERPOLAÇÃO DE LAGRANGE")
#         print("=" * 60)
#         print(f"\n  Objetivo: encontrar f(0) = segredo")
#         print(f"  Shares utilizados: {shares}")
#         print(f"  Número de pontos: {n}")
#         print(f"\n  Fórmula: f(0) = Σ y_j * L_j(0)")
#         print(f"  Onde L_j(0) = ∏(m≠j) (0 - x_m) / (x_j - x_m)")
#         print()
#
#     # Acumulador para a soma: f(0) = Σ y_j * L_j(0)
#     segredo_reconstruido = 0.0
#
#     # Para cada ponto j, calcula sua contribuição na interpolação
#     for j in range(n):
#         # Inicializa numerador e denominador do polinômio base L_j(0)
#         numerador = 1
#         denominador = 1
#         # Listas para armazenar os termos (para exibição)
#         termos_num = []
#         termos_den = []
#
#         # Percorre todos os pontos m ≠ j
#         for m in range(n):
#             if m != j:  # Exclui o próprio ponto j
#                 # Fator do numerador: (0 - x_m), pois queremos f(0)
#                 fator_num = (0 - pontos_x[m])
#                 # Fator do denominador: (x_j - x_m)
#                 fator_den = (pontos_x[j] - pontos_x[m])
#                 # Acumula o produto no numerador
#                 numerador *= fator_num
#                 # Acumula o produto no denominador
#                 denominador *= fator_den
#                 # Guarda representação textual para exibição
#                 termos_num.append(f"(0 - {pontos_x[m]})")
#                 termos_den.append(f"({pontos_x[j]} - {pontos_x[m]})")
#
#         # Calcula L_j(0) = numerador / denominador
#         base_lagrange = numerador / denominador
#         # Contribuição deste ponto: y_j * L_j(0)
#         contribuicao = pontos_y[j] * base_lagrange
#
#         if verbose:
#             # Exibe o cálculo detalhado de cada base de Lagrange
#             print(f"  ─── Cálculo de L_{j}(0) para o ponto ({pontos_x[j]}, {pontos_y[j]}) ───")
#             print(f"      Numerador:   {' * '.join(termos_num)} = {numerador}")
#             print(f"      Denominador: {' * '.join(termos_den)} = {denominador}")
#             print(f"      L_{j}(0) = {numerador} / {denominador} = {base_lagrange:.6f}")
#             print(f"      Contribuição: y_{j} * L_{j}(0) = {pontos_y[j]} * {base_lagrange:.6f} = {contribuicao:.6f}")
#             print()
#
#         # Soma a contribuição ao resultado total
#         segredo_reconstruido += contribuicao
#
#     if verbose:
#         # Exibe o resultado final da interpolação
#         print("  ─── RESULTADO FINAL ───")
#         print(f"      f(0) = soma das contribuições = {segredo_reconstruido:.6f}")
#         print(f"      Segredo reconstruído = {round(segredo_reconstruido)}")
#         print()
#
#     # Retorna o segredo arredondado (deve ser inteiro)
#     return round(segredo_reconstruido)


# =============================================================================
# ETAPA 3: Diferenças Divididas de Newton (Reconstrução do Segredo)
# =============================================================================

def construir_tabela_diferencas_divididas(
    pontos_x: List[int], pontos_y: List[int], verbose: bool = True
) -> List[List[float]]:
    """
    Constrói a tabela de diferenças divididas passo a passo.

    A tabela é uma matriz triangular inferior onde:
    - Coluna 0: valores f[xi] = yi (diferenças de ordem 0)
    - Coluna 1: f[xi, xi+1] = (f[xi+1] - f[xi]) / (xi+1 - xi) (ordem 1)
    - Coluna 2: f[xi, xi+1, xi+2] = (f[xi+1,xi+2] - f[xi,xi+1]) / (xi+2 - xi) (ordem 2)
    - ...e assim por diante

    Fórmula geral:
        f[xi, ..., xi+k] = (f[xi+1,...,xi+k] - f[xi,...,xi+k-1]) / (xi+k - xi)
    """
    # Número de pontos
    n = len(pontos_x)

    # Cria a tabela como matriz n x n inicializada com zeros
    # tabela[i][j] armazenará a diferença dividida de ordem j começando no ponto i
    tabela = [[0.0 for _ in range(n)] for _ in range(n)]

    # Preenche a coluna 0 com os valores y (diferenças de ordem 0)
    for i in range(n):
        tabela[i][0] = float(pontos_y[i])  # f[xi] = yi

    if verbose:
        print("  ─── Construção da Tabela de Diferenças Divididas ───\n")
        print("  Ordem 0 (valores de f(xi)):")
        for i in range(n):
            # Mostra cada valor inicial: f[xi] = yi
            print(f"    f[{pontos_x[i]}] = {pontos_y[i]}")
        print()

    # Preenche as colunas de ordem 1, 2, ..., n-1
    for ordem in range(1, n):
        if verbose:
            print(f"  Ordem {ordem} (diferenças divididas de ordem {ordem}):")

        # Para cada linha i que possui diferença de ordem 'ordem'
        for i in range(n - ordem):
            # Numerador: diferença entre dois valores da coluna anterior
            valor_superior = tabela[i + 1][ordem - 1]  # f[xi+1, ..., xi+ordem]
            valor_inferior = tabela[i][ordem - 1]       # f[xi, ..., xi+ordem-1]
            numerador = valor_superior - valor_inferior

            # Denominador: diferença entre os pontos x extremos
            denominador = pontos_x[i + ordem] - pontos_x[i]

            # Calcula a diferença dividida
            tabela[i][ordem] = numerador / denominador

            if verbose:
                # Monta a notação dos pontos envolvidos
                pontos_envolvidos = [str(pontos_x[k]) for k in range(i, i + ordem + 1)]
                notacao = ",".join(pontos_envolvidos)
                print(f"    f[{notacao}] = ({valor_superior} - {valor_inferior}) / ({pontos_x[i + ordem]} - {pontos_x[i]})")
                print(f"             = {numerador} / {denominador}")
                print(f"             = {tabela[i][ordem]:.6f}")
                print()

    return tabela  # Retorna a tabela completa de diferenças divididas


def avaliar_newton(
    pontos_x: List[int], tabela: List[List[float]], x_alvo: int, verbose: bool = True
) -> float:
    """
    Avalia o polinômio interpolador de Newton no ponto x_alvo.

    Forma de Newton:
        P(x) = f[x0] + f[x0,x1]*(x-x0) + f[x0,x1,x2]*(x-x0)*(x-x1) + ...

    Para encontrar o segredo, avaliamos em x_alvo = 0:
        P(0) = f[x0] + f[x0,x1]*(0-x0) + f[x0,x1,x2]*(0-x0)*(0-x1) + ...

    Os coeficientes f[x0], f[x0,x1], f[x0,x1,x2], ... são a diagonal
    principal da tabela (tabela[0][0], tabela[0][1], tabela[0][2], ...).
    """
    # Número de pontos/termos
    n = len(pontos_x)
    # Resultado acumulado
    resultado = 0.0

    if verbose:
        print(f"\n  ─── Avaliação do Polinômio de Newton em x = {x_alvo} ───\n")
        print(f"  P({x_alvo}) = f[x0] + f[x0,x1]*({x_alvo}-x0) + f[x0,x1,x2]*({x_alvo}-x0)*({x_alvo}-x1) + ...")
        print()

    # Para cada termo k do polinômio de Newton
    for k in range(n):
        # O coeficiente é a diferença dividida de ordem k: tabela[0][k]
        coeficiente = tabela[0][k]

        # Calcula o produto (x_alvo - x0)*(x_alvo - x1)*...*(x_alvo - x_{k-1})
        produto = 1.0  # Inicializa o produto acumulado
        fatores_str = []  # Lista para exibição dos fatores

        for j in range(k):
            # Cada fator é (x_alvo - xj)
            fator = (x_alvo - pontos_x[j])
            produto *= fator  # Acumula o produto
            fatores_str.append(f"({x_alvo} - {pontos_x[j]})")  # Guarda para exibição

        # Contribuição deste termo: coeficiente * produto dos fatores
        contribuicao = coeficiente * produto
        # Soma ao resultado total
        resultado += contribuicao

        if verbose:
            # Monta a notação dos pontos do coeficiente
            pontos_coef = [str(pontos_x[i]) for i in range(k + 1)]
            notacao_coef = ",".join(pontos_coef)

            if k == 0:
                # Primeiro termo: apenas f[x0]
                print(f"    Termo {k}: f[{notacao_coef}] = {coeficiente:.6f}")
                print(f"      Produto dos fatores: 1 (nenhum fator)")
                print(f"      Contribuição: {coeficiente:.6f} * 1 = {contribuicao:.6f}")
            else:
                # Termos subsequentes: coeficiente * produto dos fatores
                fatores_expr = " * ".join(fatores_str)
                print(f"    Termo {k}: f[{notacao_coef}] = {coeficiente:.6f}")
                print(f"      Produto dos fatores: {fatores_expr} = {produto:.6f}")
                print(f"      Contribuição: {coeficiente:.6f} * {produto:.6f} = {contribuicao:.6f}")
            print(f"      Soma acumulada: {resultado:.6f}")
            print()

    return resultado  # Retorna P(x_alvo)


def reconstruir_segredo_newton(shares: List[Tuple[int, int]], verbose: bool = True) -> int:
    """
    Reconstrói o segredo f(0) usando o Método de Newton com Diferenças Divididas.

    Passos:
        1. Extrai os pontos (x, y) dos shares
        2. Constrói a tabela de diferenças divididas
        3. Avalia o polinômio de Newton em x = 0 para obter o segredo
    """
    # Extrai as coordenadas x de cada share
    pontos_x = [share[0] for share in shares]
    # Extrai as coordenadas y de cada share
    pontos_y = [share[1] for share in shares]
    # Número total de pontos disponíveis
    n = len(shares)

    if verbose:
        print("=" * 60)
        print("ETAPA 3: DIFERENÇAS DIVIDIDAS DE NEWTON")
        print("=" * 60)
        print(f"\n  Objetivo: encontrar f(0) = segredo")
        print(f"  Shares utilizados: {shares}")  # Mostra os pontos usados
        print(f"  Número de pontos: {n}")
        print()
        print("  Método de Newton - Forma do polinômio interpolador:")
        print("  P(x) = f[x0] + f[x0,x1]*(x-x0) + f[x0,x1,x2]*(x-x0)*(x-x1) + ...")
        print()

    # Passo 1: Construir a tabela de diferenças divididas
    tabela = construir_tabela_diferencas_divididas(pontos_x, pontos_y, verbose)

    if verbose:
        # Exibe os coeficientes do polinômio de Newton (primeira linha da tabela)
        print("  ─── Coeficientes do Polinômio de Newton ───\n")
        print("  (São os valores da primeira linha da tabela: tabela[0][k])\n")
        for k in range(n):
            pontos_coef = [str(pontos_x[i]) for i in range(k + 1)]
            notacao = ",".join(pontos_coef)
            print(f"    c{k} = f[{notacao}] = {tabela[0][k]:.6f}")
        print()

    # Passo 2: Avaliar o polinômio de Newton em x = 0
    segredo_reconstruido = avaliar_newton(pontos_x, tabela, 0, verbose)

    if verbose:
        # Exibe o resultado final
        print("  ─── RESULTADO FINAL ───")
        print(f"      P(0) = {segredo_reconstruido:.6f}")
        print(f"      Segredo reconstruído = {round(segredo_reconstruido)}")
        print()

    # Retorna o segredo arredondado (deve ser inteiro)
    return round(segredo_reconstruido)


# =============================================================================
# DEMONSTRAÇÃO COMPLETA
# =============================================================================

if __name__ == "__main__":
    # Cabeçalho visual do programa
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   ESQUEMA DE COMPARTILHAMENTO DE SEGREDO DE SHAMIR       ║")
    print("║   Reconstrução via Diferenças Divididas de Newton        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # --- Definição dos parâmetros do esquema ---
    segredo = 1234        # O segredo que queremos compartilhar
    total_shares = 5      # Quantidade total de partes a gerar
    threshold = 3         # Mínimo de partes necessárias para reconstruir

    # Exibe a configuração escolhida
    print(f"  Configuração:")
    print(f"    • Segredo original: {segredo}")
    print(f"    • Total de partes geradas: {total_shares}")
    print(f"    • Mínimo para reconstruir: {threshold}")
    print()

    # --- Fase 1 e 2: Gera o polinômio e os shares ---
    shares = gerar_shares(segredo, total_shares, threshold)

    # --- Fase 3: Seleciona shares e reconstrói o segredo ---
    # Pega apenas 'threshold' shares (o mínimo necessário)
    shares_selecionados = shares[:threshold]
    print(f"  Shares selecionados para reconstrução ({threshold} de {total_shares}):")
    for s in shares_selecionados:
        print(f"    • Ponto: ({s[0]}, {s[1]})")  # Exibe cada share selecionado
    print()

    # Aplica o Método de Newton (Diferenças Divididas) para encontrar f(0) = segredo
    segredo_recuperado = reconstruir_segredo_newton(shares_selecionados, verbose=True)

    # --- Verificação: compara o segredo original com o recuperado ---
    print("=" * 60)
    print("VERIFICAÇÃO")
    print("=" * 60)
    if segredo_recuperado == segredo:
        # Segredo recuperado com sucesso!
        print(f"\n  ✓ SUCESSO! Segredo recuperado corretamente: {segredo_recuperado}")
    else:
        # Algo deu errado na reconstrução
        print(f"\n  ✗ ERRO! Esperado {segredo}, obteve {segredo_recuperado}")

    # --- Teste de segurança: tenta reconstruir com shares insuficientes ---
    print()
    print("=" * 60)
    print("TESTE: SHARES INSUFICIENTES")
    print("=" * 60)
    # Seleciona menos shares que o threshold (não deve funcionar)
    shares_insuficientes = shares[:threshold - 1]
    print(f"\n  Tentando com apenas {threshold - 1} shares (mínimo é {threshold}):")
    for s in shares_insuficientes:
        print(f"    • Ponto: ({s[0]}, {s[1]})")  # Exibe os shares insuficientes
    print()
    # Tenta interpolar com pontos insuficientes
    resultado_errado = reconstruir_segredo_newton(shares_insuficientes, verbose=False)
    print(f"  Resultado obtido: {resultado_errado}")  # Mostra o resultado incorreto
    if resultado_errado != segredo:
        # Confirma que o segredo NÃO foi recuperado
        print(f"  ✗ Segredo NÃO recuperado (esperado {segredo})")
        print(f"  → Isso demonstra que {threshold - 1} shares são insuficientes!")
    print()