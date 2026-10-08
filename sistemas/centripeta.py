import time
 
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
 
# ---------------------------------------------------------------------------
# FÍSICA (separada da interface)
# ---------------------------------------------------------------------------
 
def calcular_grandezas(R, v, m):
    """Calcula as grandezas do MCU a partir de R, v e m."""
    # Velocidade angular: no MCU o corpo percorre o arco v·t, e arco = R·θ,
    # logo θ = (v/R)·t, ou seja, ω = v / R.
    omega = v / R
 
    # Período: tempo de uma volta completa (2π rad) com velocidade angular ω.
    periodo = 2 * np.pi / omega
 
    # Aceleração centrípeta: a direção da velocidade muda o tempo todo, então
    # há aceleração apontando para o centro, de módulo a_c = v² / R = ω²·R.
    a_c = v ** 2 / R
 
    # 2ª Lei de Newton na direção radial: ΣF = m·a  →  Fc = m·v² / R = m·ω²·R.
    # A força centrípeta não é uma força nova: é a resultante (aqui, a tração
    # do fio) que aponta para o centro.
    f_c = m * a_c
 
    return omega, periodo, a_c, f_c
 
 
def calcular_posicao(R, omega, t):
    """Posição no círculo: x(t) = R·cos(ωt) e y(t) = R·sen(ωt).
    Aceita t escalar ou vetor NumPy."""
    x = R * np.cos(omega * t)
    y = R * np.sin(omega * t)
    return x, y
 
 
# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------
 
def criar_figura(R, omega, periodo):
    """Cria a figura uma única vez, com os elementos fixos (trajetória,
    centro, limites) e os elementos que se movem (fio, corpo, setas).
    Reaproveitar a figura entre os quadros deixa a animação bem mais leve."""
    fig, ax = plt.subplots(figsize=(4, 4))
 
    # Trajetória: uma volta completa avaliada sobre um vetor de tempo.
    t_volta = np.linspace(0, periodo, 200)
    xs, ys = calcular_posicao(R, omega, t_volta)
    ax.plot(xs, ys, "--", color="lightgray")
    ax.plot(0, 0, "k+", markersize=10)
 
    # Elementos que mudam a cada instante (posições definidas em atualizar_quadro).
    fio, = ax.plot([], [], color="gray", lw=1.5)
    corpo, = ax.plot([], [], "o", color="steelblue", markersize=12)
    seta_fc = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                          arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2))
    seta_v = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="-|>", color="seagreen", lw=2))
 
    # Legenda com linhas "fantasma" só para mostrar as cores das setas.
    ax.plot([], [], color="crimson", lw=2, label="Força centrípeta Fc")
    ax.plot([], [], color="seagreen", lw=2, label="Velocidade v")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=8)
 
    limite = 1.4 * R
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True, alpha=0.3)
    titulo = ax.set_title("")
 
    elementos = {"fio": fio, "corpo": corpo, "seta_fc": seta_fc,
                 "seta_v": seta_v, "titulo": titulo}
    return fig, elementos
 
 
def atualizar_quadro(elementos, R, omega, t):
    """Move o corpo, o fio e as setas para o instante t."""
    x, y = calcular_posicao(R, omega, t)
    ux, uy = x / R, y / R   # vetor unitário radial (do centro para o corpo)
    comprimento = 0.35 * R  # comprimento fixo das setas, só indica a direção
 
    elementos["fio"].set_data([0, x], [0, y])
    elementos["corpo"].set_data([x], [y])
 
    # Força centrípeta: aponta para o centro (sentido oposto ao radial).
    elementos["seta_fc"].set_position((x, y))
    elementos["seta_fc"].xy = (x - comprimento * ux, y - comprimento * uy)
 
    # Velocidade: tangente ao círculo, perpendicular ao raio.
    elementos["seta_v"].set_position((x, y))
    elementos["seta_v"].xy = (x - comprimento * uy, y + comprimento * ux)
 
    elementos["titulo"].set_text(f"t = {t:.2f} s")
 
 
def renderizar():
    """Tela do sistema: controles | gráfico | valores calculados."""
    st.subheader("Força Centrípeta — Movimento Circular Uniforme")
    st.write(
        "Uma massa presa a um fio gira em um círculo horizontal com velocidade "
        "tangencial constante. Ajuste os parâmetros e veja a força centrípeta."
    )
 
    col_controles, col_grafico, col_valores = st.columns([1, 1.3, 1])
 
    with col_controles:
        R = st.slider("Raio R (m)", 0.5, 10.0, 3.0, 0.1)
        v = st.slider("Velocidade tangencial v (m/s)", 0.5, 20.0, 5.0, 0.1)
        m = st.slider("Massa m (kg)", 0.1, 10.0, 1.0, 0.1)
        fracao = st.slider("Posição na volta (0 = início, 1 = volta completa)",
                           0.0, 1.0, 0.0, 0.01)
        animar = st.button("▶ Animar uma volta")
 
    omega, periodo, a_c, f_c = calcular_grandezas(R, v, m)
    t = fracao * periodo
 
    with col_grafico:
        area_grafico = st.empty()
        fig, elementos = criar_figura(R, omega, periodo)
        atualizar_quadro(elementos, R, omega, t)
        area_grafico.pyplot(fig)
 
    # Grandezas calculadas, atualizadas a cada mudança nos sliders.
    with col_valores:
        st.metric("Força centrípeta Fc", f"{f_c:.2f} N")
        st.metric("Velocidade angular ω", f"{omega:.2f} rad/s")
        st.metric("Aceleração centrípeta", f"{a_c:.2f} m/s²")
        st.metric("Período T (tempo de uma volta)", f"{periodo:.2f} s")
 
    with st.expander("Equações utilizadas"):
        st.latex(r"\omega = \frac{v}{R}")
        st.latex(r"x(t) = R\cos(\omega t) \qquad y(t) = R\sin(\omega t)")
        st.latex(r"F_c = \frac{m v^2}{R} = m \omega^2 R")
        st.latex(r"T = \frac{2\pi}{\omega}")
 
    # A animação fica por último, pois bloqueia o script enquanto roda.
    # Ela acompanha o relógio real: a cada quadro, o instante t desenhado é o
    # tempo realmente decorrido desde o clique. Uma volta leva exatamente T
    # segundos; se a tela demorar a redesenhar, os quadros são pulados, mas a
    # posição continua correta para aquele instante.
    if animar:
        inicio = time.perf_counter()
        while True:
            decorrido = time.perf_counter() - inicio
            atualizar_quadro(elementos, R, omega, min(decorrido, periodo))
            area_grafico.pyplot(fig)
            if decorrido >= periodo:
                break
 
    plt.close(fig)
 