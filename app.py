"""
Recurso interactivo - Situación 3A (Ingeniería de Software)
Rendimiento de una aplicación: modelo, derivada y decisión.
Ejecutar:  streamlit run app.py
"""
import inspect
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import modelo as m

st.set_page_config(page_title="Situación 3A · Rendimiento de una aplicación", layout="wide")

AZUL_OSC, AZUL, AZUL_CLARO, ACENTO = "#0B2A5B", "#1F5FAD", "#7FB2E5", "#E07B00"

# ------------------------------------------------------------------ Barra lateral: datos modificables
st.sidebar.header("Datos del escenario")
k = st.sidebar.number_input("Parámetro del grupo k", 0, 30, 8, 1)
K = st.sidebar.number_input("Capacidad de la infraestructura (miles de usuarios)", 5.0, 60.0, 20.0, 1.0)
r = st.sidebar.slider("Tasa de crecimiento r (1/semana)", 0.10, 1.00, 0.40, 0.05)
a = st.sidebar.slider("Constante a de x(t)", 2.0, 30.0, 9.0, 1.0)
c_srv = st.sidebar.number_input("Costo por servidor (miles de pesos/mes)", 50.0, 400.0, 120.0, 10.0)
n_max = st.sidebar.number_input("Espacio del centro de datos (servidores)", 5, 40, 20, 1)
st.sidebar.header("Punto a analizar")
t_sel = st.sidebar.slider("Semana t", 0.0, 15.0, 4.0, 0.5)
x_sel = st.sidebar.slider("Usuarios x (miles) para T y T*", 1.0, float(K), 6.0, 0.01, format="%.2f")
n_sel = st.sidebar.slider("Servidores n", 1, int(n_max), 7, 1)
st.sidebar.header("Umbrales de la zona de decisión")
alerta = st.sidebar.slider("Alerta de capacidad (% de K)", 50, 100, 80, 5)
tol = st.sidebar.slider("Tolerancia de costo sobre el mínimo (%)", 0, 10, 2, 1)

# ------------------------------------------------------------------ Validez de la versión original en x
EN_4 = abs(x_sel - 4) < 1e-9          # x = 4: asíntota de T (división entre cero)
T_VALIDA = x_sel > 4 and not EN_4     # T solo describe la operación por encima de 4 mil usuarios

def txt_dT(x):
    if abs(x - 4) < 1e-9:
        return "no definida (x = 4)"
    if x < 4:
        return "fuera de rango (x < 4)"
    return f"{m.dT(x):.2f} s/mil"

# ------------------------------------------------------------------ Cálculos
t_star = m.t_inflexion(K, r, a)
x_star = K / 2
v_max = r * K / 4
n_crit = m.n_critico(k, c_srv)
n_opt = m.n_optimo(k, c_srv, int(n_max))
c_min = m.C(n_opt, k, c_srv)
semanas_alerta = m.semana_para_usuarios(K * alerta / 100, K, r, a)
n_tol = m.rango_tolerancia(k, c_srv, int(n_max), tol / 100)

st.title("Rendimiento de una aplicación: modelo, derivada y decisión")
st.caption("Situación 3A · Ingeniería de Software · Cálculo diferencial 2026-II")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Zona de decisión", "Versiones T y T*", "Usuarios x(t)", "Costo C(n)", "Verificación", "Fórmulas y código"])

def base(fig, titulo, xt, yt):
    fig.update_layout(title=titulo, xaxis_title=xt, yaxis_title=yt, height=380,
                      margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h"))
    return fig

# ------------------------------------------------------------------ Pestaña 1: decisión
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Semana de mayor crecimiento t*", f"{t_star:.2f} sem")
    c2.metric("Usuarios en t*", f"{x_star:.1f} mil", f"+{v_max:.2f} mil/sem")
    c3.metric("Servidores óptimos", f"{n_opt}", f"n* = {n_crit:.2f}", delta_color="off")
    c4.metric("Costo mínimo", f"${c_min:,.1f} mil/mes")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("T'(x) con x elegido", txt_dT(x_sel))
    c2.metric("T*'(x) con x elegido", f"{m.dTs(x_sel):.3f} s/mil")
    c3.metric("x(t) en la semana elegida", f"{m.x_t(t_sel, K, r, a):.2f} mil")
    c4.metric("dT*/dt en la semana elegida", f"{m.dTs_dt(t_sel, K, r, a):.3f} s/sem")

    st.subheader("Zona de decisión")
    xs = m.x_t(t_sel, K, r, a)
    if t_sel < t_star - 1.5:
        estado, color = "PREPARAR: el crecimiento se acelera; contratar y tener listo el refuerzo.", "#2E86DE"
    elif t_sel < t_star + 1.5:
        estado, color = "REFORZAR: ritmo de llegada máximo; el refuerzo debe estar operando.", ACENTO
    elif xs < K * alerta / 100:
        estado, color = "FRENAR: el crecimiento se desacelera; vigilar la holgura.", "#1F5FAD"
    else:
        estado, color = "CRÍTICA: se superó la alerta de capacidad; ampliar la infraestructura.", "#B00020"
    st.markdown(f"<div style='padding:12px;border-radius:8px;background:{color};color:white;font-weight:600'>"
                f"Semana {t_sel:.1f} · {xs:.1f} mil usuarios ({100*xs/K:.0f}% de K) → {estado}</div>",
                unsafe_allow_html=True)
    st.write(f"**Contratación:** con k = {k}, el entero de menor costo es **n = {n_opt}** "
             f"(${c_min:,.1f} mil/mes). Valores de n dentro de {tol} % del mínimo: **{n_tol}**. "
             f"**Alerta del {alerta} % de K** ({K*alerta/100:.1f} mil usuarios) en la semana **{semanas_alerta:.1f}**.")
    tt = np.linspace(0, 15, 300)
    fig = go.Figure()
    fig.add_scatter(x=tt, y=[m.x_t(t, K, r, a) for t in tt], name="x(t)", line=dict(color=AZUL_OSC, width=3))
    fig.add_hrect(y0=0, y1=K, x0=0, x1=max(t_star - 1.5, 0), fillcolor="#2E86DE", opacity=0.10, line_width=0)
    fig.add_vrect(x0=max(t_star - 1.5, 0), x1=t_star + 1.5, fillcolor=ACENTO, opacity=0.15, line_width=0)
    fig.add_hline(y=K, line_dash="dash", line_color="#B00020", annotation_text="Capacidad K")
    fig.add_hline(y=K * alerta / 100, line_dash="dot", line_color=AZUL, annotation_text=f"Alerta {alerta}%")
    fig.add_scatter(x=[t_star], y=[x_star], mode="markers", name="Punto de inflexión",
                    marker=dict(color=ACENTO, size=12))
    fig.add_scatter(x=[t_sel], y=[xs], mode="markers", name="Semana elegida", marker=dict(color=AZUL, size=11))
    st.plotly_chart(base(fig, "Línea de tiempo del despliegue", "t (semanas)", "x (miles de usuarios)"),
                    use_container_width=True)

# ------------------------------------------------------------------ Pestaña 2: T y T*
with tab2:
    xx = np.linspace(0.3, K, 700)
    xo = xx[np.abs(xx - 4) > 0.02]
    f1 = go.Figure()
    xt_ = xo[xo > 4]
    f1.add_scatter(x=xt_, y=[m.T(v) for v in xt_], name="T(x) original", line=dict(color=AZUL_OSC, width=3))
    f1.add_scatter(x=xo, y=[m.Ts(v) for v in xo], name="T*(x) nueva", line=dict(color=AZUL_CLARO, width=3))
    f1.add_vline(x=4, line_dash="dash", line_color="#B00020", annotation_text="asíntota x = 4")
    f1.add_hline(y=5, line_dash="dot", line_color=AZUL_OSC, annotation_text="tope T → 5 s")
    f1.add_hline(y=1, line_dash="dot", line_color=AZUL, annotation_text="tope T* → 1 s")
    f1.add_scatter(x=[4], y=[2], mode="markers", name="hueco T*(4) = 2",
                   marker=dict(symbol="circle-open", size=12, color=ACENTO, line=dict(width=2)))
    if T_VALIDA:
        f1.add_scatter(x=[x_sel], y=[m.T(x_sel)], mode="markers", name="T en x elegido",
                       marker=dict(color=AZUL_OSC, size=11))
    if not EN_4:
        f1.add_scatter(x=[x_sel], y=[m.Ts(x_sel)], mode="markers", name="T* en x elegido",
                       marker=dict(color=AZUL, size=11))
    f1.update_yaxes(range=[0, 20])
    st.plotly_chart(base(f1, "Tiempo de respuesta", "x (miles de usuarios)", "T (s)"), use_container_width=True)
    f2 = go.Figure()
    f2.add_scatter(x=xt_, y=[m.dT(v) for v in xt_], name="T'(x)", line=dict(color=AZUL_OSC, width=3))
    f2.add_scatter(x=xo, y=[m.dTs(v) for v in xo], name="T*'(x)", line=dict(color=AZUL_CLARO, width=3))
    ys_sel = [m.dT(x_sel), m.dTs(x_sel)] if T_VALIDA else [m.dTs(x_sel)]
    f2.add_scatter(x=[x_sel] * len(ys_sel), y=ys_sel, mode="markers", name="x elegido",
                   marker=dict(color=ACENTO, size=11))
    f2.update_yaxes(range=[-60, 2])
    st.plotly_chart(base(f2, "Derivadas: ritmo de cambio del tiempo", "x (miles de usuarios)", "dT/dx (s por mil usuarios)"),
                    use_container_width=True)
    if T_VALIDA:
        st.info(f"Con x = {x_sel:.2f} mil: T = {m.T(x_sel):.2f} s y T* = {m.Ts(x_sel):.2f} s; "
                f"T' = {m.dT(x_sel):.2f} y T*' = {m.dTs(x_sel):.3f} s por mil usuarios; "
                f"la original es {abs(m.dT(x_sel) / m.dTs(x_sel)):.0f} veces más sensible.")
    elif EN_4:
        st.warning("Con x = 4,00 mil: la versión original T(x) no está definida (división entre cero): "
                   "es la asíntota vertical, el tiempo crece sin control. La fórmula de T* da 0/0 "
                   "(indeterminada), pero los valores a ambos lados se acercan a 2 s: lim T*(x) = 2 s "
                   "(el hueco naranja), y T*'(4) = −0,25 s por mil usuarios.")
    else:
        st.warning(f"Con x = {x_sel:.2f} mil: la versión original daría T = {m.T(x_sel):.2f} s, un tiempo "
                   f"negativo sin sentido; T(x) solo vale por encima de 4 mil usuarios. "
                   f"La versión nueva sí funciona: T* = {m.Ts(x_sel):.2f} s y T*' = {m.dTs(x_sel):.3f} s por mil usuarios.")

# ------------------------------------------------------------------ Pestaña 3: x(t)
with tab3:
    tt = np.linspace(0, 15, 400)
    g1 = go.Figure()
    g1.add_scatter(x=tt, y=[m.x_t(t, K, r, a) for t in tt], name="x(t)", line=dict(color=AZUL_OSC, width=3))
    h = 0.5
    tg = np.linspace(max(t_sel - 2, 0), t_sel + 2, 20)
    g1.add_scatter(x=tg, y=[m.x_t(t_sel, K, r, a) + m.dx_t(t_sel, K, r, a) * (t - t_sel) for t in tg],
                   name="tangente (pendiente x')", line=dict(color=ACENTO, dash="dash"))
    g1.add_hline(y=K, line_dash="dash", line_color="#B00020", annotation_text="tope K")
    g1.add_scatter(x=[t_star], y=[x_star], mode="markers", name="inflexión",
                   marker=dict(color=ACENTO, size=12))
    st.plotly_chart(base(g1, "Usuarios x(t)", "t (semanas)", "x (miles de usuarios)"), use_container_width=True)
    g2 = go.Figure()
    g2.add_scatter(x=tt, y=[m.dx_t(t, K, r, a) for t in tt], name="x'(t)", line=dict(color=AZUL, width=3))
    g2.add_scatter(x=[t_star], y=[v_max], mode="markers", name="máximo de x'", marker=dict(color=ACENTO, size=12))
    st.plotly_chart(base(g2, "Derivada x'(t): ritmo de llegada", "t (semanas)", "x' (miles de usuarios por semana)"),
                    use_container_width=True)
    st.info(f"t* = ln(a)/r = {t_star:.2f} semanas; x(t*) = K/2 = {x_star:.1f} mil; x'(t*) = rK/4 = {v_max:.2f} mil/sem.")

# ------------------------------------------------------------------ Pestaña 4: C(n)
with tab4:
    ns = np.arange(1, int(n_max) + 1)
    cs = [m.C(n, k, c_srv) for n in ns]
    h1 = go.Figure()
    h1.add_scatter(x=ns, y=cs, mode="lines+markers", name="C(n)", line=dict(color=AZUL_OSC, width=3))
    h1.add_scatter(x=[n_opt], y=[c_min], mode="markers", name="n óptimo", marker=dict(color=ACENTO, size=13))
    h1.add_scatter(x=[n_sel], y=[m.C(n_sel, k, c_srv)], mode="markers", name="n elegido",
                   marker=dict(color=AZUL_CLARO, size=11))
    h1.add_vline(x=n_crit, line_dash="dot", line_color=AZUL, annotation_text=f"n* = {n_crit:.2f}")
    h1.update_yaxes(range=[0, min(max(cs), 4 * c_min)])
    st.plotly_chart(base(h1, "Costo mensual", "n (servidores)", "C (miles de pesos/mes)"), use_container_width=True)
    nn = np.linspace(1, int(n_max), 300)
    h2 = go.Figure()
    h2.add_scatter(x=nn, y=[m.dC(v, k, c_srv) for v in nn], name="C'(n)", line=dict(color=AZUL, width=3))
    h2.add_hline(y=0, line_color="gray")
    h2.update_yaxes(range=[-300, 150])
    st.plotly_chart(base(h2, "Derivada C'(n)", "n (servidores)", "C' (miles de pesos/mes por servidor)"),
                    use_container_width=True)
    st.table({"n": [n_sel - 1, n_sel, n_sel + 1] if n_sel > 1 else [n_sel, n_sel + 1],
              "C(n) (miles $/mes)": [round(m.C(v, k, c_srv), 1) for v in
                                     ([n_sel - 1, n_sel, n_sel + 1] if n_sel > 1 else [n_sel, n_sel + 1])]})

# ------------------------------------------------------------------ Pestaña 5: verificación
with tab5:
    st.write("Cada derivada analítica se compara con una derivada numérica (diferencia central, h = 10⁻⁶).")
    hh = 1e-6
    filas = [
        ("T'(6)", m.dT(6), (m.T(6 + hh) - m.T(6 - hh)) / (2 * hh)),
        ("T*'(6)", m.dTs(6), (m.Ts(6 + hh) - m.Ts(6 - hh)) / (2 * hh)),
        ("T*'(4) por definición", -0.25, m.dTs_def(1e-6)),
        (f"x'({t_sel})", m.dx_t(t_sel, K, r, a), (m.x_t(t_sel + hh, K, r, a) - m.x_t(t_sel - hh, K, r, a)) / (2 * hh)),
        (f"dT*/dt ({t_sel})", m.dTs_dt(t_sel, K, r, a),
         (m.Ts(m.x_t(t_sel + hh, K, r, a)) - m.Ts(m.x_t(t_sel - hh, K, r, a))) / (2 * hh)),
        (f"C'({n_sel})", m.dC(n_sel, k, c_srv), (m.C(n_sel + hh, k, c_srv) - m.C(n_sel - hh, k, c_srv)) / (2 * hh)),
    ]
    st.table({"Derivada": [f[0] for f in filas], "Analítica": [round(f[1], 5) for f in filas],
              "Numérica": [round(f[2], 5) for f in filas],
              "Coinciden": ["Sí" if abs(f[1] - f[2]) < 1e-3 else "No" for f in filas]})
    if st.button("Ejecutar pruebas automáticas de modelo.py"):
        try:
            m.pruebas(k)
            st.success("Todas las pruebas pasaron (valores de referencia del reporte).")
        except AssertionError:
            st.warning("Alguna prueba no coincide: con datos distintos a los del escenario es esperable.")

# ------------------------------------------------------------------ Pestaña 6: fórmulas y código
with tab6:
    st.latex(r"T(x)=\frac{5x+40}{x-4},\quad T'(x)=\frac{-60}{(x-4)^2}")
    st.latex(r"T^*(x)=\frac{x^2-16}{x^2-4x}=\frac{x+4}{x},\quad T^{*\prime}(x)=\frac{-4}{x^2},\quad T^{*\prime}(4)=-\tfrac14")
    st.latex(r"x(t)=\frac{K}{1+a\,e^{-rt}},\quad x'(t)=r\,x\left(1-\frac{x}{K}\right),\quad t^*=\frac{\ln a}{r}")
    st.latex(r"\frac{dT^*}{dt}=T^{*\prime}(x(t))\cdot x'(t)")
    st.latex(r"C(n)=120n+\frac{4800+200k}{n},\quad C'(n)=120-\frac{4800+200k}{n^2},\quad n^*=\sqrt{\frac{4800+200k}{120}}")
    st.subheader("Código del modelo (modelo.py)")
    st.code(inspect.getsource(m), language="python")

