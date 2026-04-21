from typing import List, Tuple, Optional, Dict
import time
import math
import random

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2

# -----------------------------------------------------------------------------
# Utilidades de tabuleiro (PRONTAS)
# -----------------------------------------------------------------------------
def copy_board(board: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in board]

def valid_moves(board: List[List[int]]) -> List[int]:
    """Retorna as colunas ainda jogáveis (topo vazio)."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def make_move(board: List[List[int]], col: int, player: int) -> Optional[List[List[int]]]:
    """Retorna um novo tabuleiro aplicando a gravidade na coluna col; None se inválido."""
    if col < 0 or col >= COLS or board[0][col] != EMPTY:
        return None
    nb = copy_board(board)
    for r in reversed(range(ROWS)):
        if nb[r][col] == EMPTY:
            nb[r][col] = player
            return nb
    return None

def winner(board: List[List[int]]) -> int:
    """0 se ninguém venceu; 1 ou 2 se há 4 em linha."""
    # Horizontais
    for r in range(ROWS):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return x
    # Verticais
    for c in range(COLS):
        for r in range(ROWS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return x
    # Diag ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return x
    # Diag ↗
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return x
    return 0

def is_full(board: List[List[int]]) -> bool:
    return all(board[0][c] != EMPTY for c in range(COLS))

def terminal(board: List[List[int]]) -> Tuple[bool, int]:
    """(é_terminal, vencedor) com vencedor=0 para empate/indefinido."""
    w = winner(board)
    if w != 0:
        return True, w
    if is_full(board):
        return True, 0
    return False, 0

def other(player: int) -> int:
    return P1 if player == P2 else P2

# -----------------------------------------------------------------------------
# ÚNICO PONTO A SER IMPLEMENTADO PELOS ALUNOS
# -----------------------------------------------------------------------------
def choose_move(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    """
    Decide a coluna (0..6) para jogar agora.

    Parâmetros:
      - board: matriz 6x7 com valores {0,1,2}
      - turn: 1 ou 2
      - config: {"max_time_ms": int, "max_depth": int}

    Retorna:
      - col: int (0..6)
    """
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move
    
    move = mini_max(board, legal, turn, max_depth, time_exceeded)

    return move

def mini_max(board, legal, player, max_depth, time_exceeded):

    opponent = other(player)
    
    # --------- heuristica ---------
    def heuristic(board):
        score = 0

        def evaluate_window(window):
            s = 0
            player_count = window.count(player)
            opp_count = window.count(opponent)
            empty_count = window.count(EMPTY)

            if player_count == 4:
                s += 100
            elif player_count == 3 and empty_count == 1:
                s += 5
            elif player_count == 2 and empty_count == 2:
                s += 2

            if opp_count == 3 and empty_count == 1:
                s -= 6

            return s

        #centro
        center_col = COLS // 2
        center = [board[r][center_col] for r in range(ROWS)]
        score += center.count(player) * 3

        #horizontais
        for r in range(ROWS):
            for c in range(COLS - 3):
                window = [board[r][c+i] for i in range(4)]
                score += evaluate_window(window)

        #verticais
        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [board[r+i][c] for i in range(4)]
                score += evaluate_window(window)

        #diagonal direita baixo
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += evaluate_window(window)

        #diagonal direita cima
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [board[r-i][c+i] for i in range(4)]
                score += evaluate_window(window)

        return score

    # --------- minimax ---------
    def minimax(board, depth, maximizing, alpha, beta, count=[0]):

        if time_exceeded():
            return heuristic(board)

        terminou, vencedor = terminal(board)
        count[0] += 1
        # nó folha --> funcao utilidade
        if terminou:
            if vencedor == player:
                return 1000
            elif vencedor == opponent:
                return -1000
            else:
                return 0

        # death limite
        if depth == 0:
            return heuristic(board)

        # moves = valid_moves(board)
        moves = sorted(valid_moves(board), key=lambda c: abs(c - 3))
        
        if maximizing:
            best = -math.inf
            for col in moves:
                nb = make_move(board, col, player)
                val = minimax(nb, depth - 1, False, alpha, beta)

                best = max(best, val)
                alpha = max(alpha, best)

                if alpha >= beta:
                    break

            return best
        else:
            best = math.inf
            for col in moves:
                nb = make_move(board, col, opponent)
                val = minimax(nb, depth - 1, True, alpha, beta)

                best = min(best, val)
                beta = min(beta, best)

                if alpha >= beta:
                    break

            return best

    #escolhe
    best_score = -math.inf
    best_move = legal[0]
    countTotal = 0
    legal = sorted(legal, key=lambda c: abs(c - 3))

    for depth in range(1, max_depth + 1):

        if time_exceeded():
            break
        
        current_best_move = best_move
        current_best_score = -math.inf

        for col in legal:

            if time_exceeded():
                break

            nb = make_move(board, col, player)

            score = minimax(nb, depth - 1, False, -math.inf, math.inf)

            if score > current_best_score:
                current_best_score = score
                current_best_move = col

        # só atualiza se terminou essa profundidade
        if not time_exceeded():
            best_move = current_best_move
            best_score = current_best_score
    
    return best_move

def choose_move_randomly(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        return move
    
    move = random.choice(legal)
    return move


def choose_move_infinity(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    """
    Decide a coluna (0..6) para jogar agora.

    Parâmetros:
      - board: matriz 6x7 com valores {0,1,2}
      - turn: 1 ou 2
      - config: {"max_time_ms": int, "max_depth": int}

    Retorna:
      - col: int (0..6)
    """
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move
    
    # VERSÃO INICIAL: escolhe aleatoriamente entre as jogadas legais
    i = 0
    while True:
        i += 1

    return move