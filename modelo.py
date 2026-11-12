"""
modelo.py - Situación 3A (Ingeniería de Software): rendimiento de una aplicación.
Modelos, derivadas analíticas y verificaciones. Sin dependencias de Streamlit,
para poder probarse por separado:  python modelo.py
"""
import math

# ---------------------------------------------------------------- Versión original T(x)
def T(x):
    """Tiempo de respuesta (s) de la versión original; x en miles de usuarios."""
    return (5 * x + 40) / (x - 4)

def dT(x):
    """T'(x) = -60/(x-4)^2  (s por cada mil usuarios)."""
    return -60 / (x - 4) ** 2

# ---------------------------------------------------------------- Versión nueva T*(x)
def Ts(x):
    """T*(x) = (x^2-16)/(x^2-4x) = (x+4)/x = 1 + 4/x. En x=4 se define T*(4)=2."""
    if abs(x - 4) < 1e-12:
        return 2.0
    return (x + 4) / x

def dTs(x):
    """T*'(x) = -4/x^2  (s por cada mil usuarios)."""
    return -4 / x ** 2

def dTs_def(h=1e-6, x0=4.0):
    """Derivada de T* en x0 por definición de límite (cociente incremental)."""
    return (Ts(x0 + h) - Ts(x0)) / h

# ---------------------------------------------------------------- Usuarios x(t)
def x_t(t, K=20.0, r=0.4, a=9.0):
    """x(t) = K / (1 + a e^{-r t}), en miles de usuarios; t en semanas."""
    return K / (1 + a * math.exp(-r * t))

def dx_t(t, K=20.0, r=0.4, a=9.0):
    """x'(t) = r x (1 - x/K)  (miles de usuarios por semana)."""
    x = x_t(t, K, r, a)
    return r * x * (1 - x / K)

def d2x_t(t, K=20.0, r=0.4, a=9.0):
    """x''(t) = r x' (1 - 2x/K)."""
    x = x_t(t, K, r, a)
    return r * dx_t(t, K, r, a) * (1 - 2 * x / K)

def t_inflexion(K=20.0, r=0.4, a=9.0):
    """x''=0  <=>  x=K/2  <=>  a e^{-r t}=1  =>  t* = ln(a)/r."""
    return math.log(a) / r

def dTs_dt(t, K=20.0, r=0.4, a=9.0):
    """Regla de la cadena: dT*/dt = T*'(x(t)) * x'(t)."""
    return dTs(x_t(t, K, r, a)) * dx_t(t, K, r, a)

def semana_para_usuarios(x_obj, K=20.0, r=0.4, a=9.0):
    """Semana t en que x(t)=x_obj (0<x_obj<K)."""
    return math.log(a * x_obj / (K - x_obj)) / r

# ---------------------------------------------------------------- Costo C(n)
def penalidad(k):
    """Numerador de la penalidad (miles de pesos/mes): 4800 + 200 k."""
    return 4800 + 200 * k

def C(n, k=8, costo_servidor=120.0):
    """C(n) = 120 n + (4800+200k)/n  (miles de pesos por mes)."""
    return costo_servidor * n + penalidad(k) / n

def dC(n, k=8, costo_servidor=120.0):
    return costo_servidor - penalidad(k) / n ** 2

def d2C(n, k=8, costo_servidor=120.0):
    return 2 * penalidad(k) / n ** 3

def n_critico(k=8, costo_servidor=120.0):
    """C'(n)=0  =>  n* = sqrt((4800+200k)/120)."""
    return math.sqrt(penalidad(k) / costo_servidor)

def n_optimo(k=8, costo_servidor=120.0, n_max=20):
    """Entero n en [1, n_max] que minimiza C (se comparan todos; el óptimo está junto a n*)."""
    return min(range(1, n_max + 1), key=lambda n: C(n, k, costo_servidor))

def rango_tolerancia(k=8, costo_servidor=120.0, n_max=20, tol=0.02):
    """Enteros n con C(n) <= (1+tol) * C minimo."""
    cmin = C(n_optimo(k, costo_servidor, n_max), k, costo_servidor)
    return [n for n in range(1, n_max + 1) if C(n, k, costo_servidor) <= (1 + tol) * cmin]

# ---------------------------------------------------------------- Pruebas automáticas
def pruebas(k=8):
    ok = lambda a, b, tol=1e-3: abs(a - b) < tol
    # P1: límite de T* en x = 4
    assert ok(Ts(4 + 1e-7), 2, 1e-5) and ok(Ts(4 - 1e-7), 2, 1e-5)
    # P2a
    assert ok(dT(6), -15) and ok(dTs(6), -1 / 9)
    assert ok(dT(6) / dTs(6), 135)
    # P2b: derivada por definición en x=4
    assert ok(dTs_def(1e-6), -0.25, 1e-5) and ok(dTs_def(-1e-6), -0.25, 1e-5)
    # P3
    assert ok(x_t(4), 7.0996, 1e-3) and ok(dx_t(4), 1.8318, 1e-3)
    assert ok(dTs_dt(4), -0.1454, 1e-4)
    # P4
    ts = t_inflexion()
    assert ok(ts, 5.4931, 1e-3) and ok(x_t(ts), 10) and ok(dx_t(ts), 2) and ok(d2x_t(ts), 0, 1e-9)
    # derivada numérica de x (diferencia central) coincide con la analítica
    h = 1e-6
    assert ok((x_t(4 + h) - x_t(4 - h)) / (2 * h), dx_t(4), 1e-6)
    # P5 con k dado
    assert ok(C(7, 8), 1754.2857, 1e-3) and ok(C(8, 8), 1760.0) and ok(C(6, 8), 1786.6667, 1e-3)
    assert ok(n_critico(8), 7.3030, 1e-3) and n_optimo(8) == 7
    assert n_optimo(3) == 7 and n_optimo(1) == 6 and n_optimo(10) == 8
    h = 1e-6
    assert ok((C(7 + h, k) - C(7 - h, k)) / (2 * h), dC(7, k), 1e-5)
    return True

if __name__ == "__main__":
    print("Pruebas:", "OK" if pruebas() else "FALLO")
    print(f"n* = {n_critico(8):.4f}; n óptimo = {n_optimo(8)}; C(7) = {C(7):.4f}; C(8) = {C(8):.4f}")
