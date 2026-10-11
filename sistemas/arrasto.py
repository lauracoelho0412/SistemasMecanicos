"""Sistema 3.3 — Força de arrasto."""

import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# ---------------------------------------------------------------------------
# FÍSICA (separada da interface)
# ---------------------------------------------------------------------------

GRAVIDADE = 9.81


def calcular_grandezas(massa, coeficiente_linear, coeficiente_quadratico, gravidade=GRAVIDADE):
    """Calcula velocidades terminais e constante de tempo para os dois modelos."""
    velocidade_terminal_linear = massa * gravidade / coeficiente_linear
    constante_tempo_linear = massa / coeficiente_linear
    velocidade_terminal_quadratica = np.sqrt(massa * gravidade / coeficiente_quadratico)
    return (
        velocidade_terminal_linear,
        constante_tempo_linear,
        velocidade_terminal_quadratica,
    )


def velocidade_linear(
    tempo: np.ndarray, massa: float, coeficiente: float, gravidade: float = GRAVIDADE
) -> np.ndarray:
    """Velocidade de queda com arrasto linear, partindo do repouso."""
    velocidade_terminal = massa * gravidade / coeficiente
    constante_tempo = massa / coeficiente
    return velocidade_terminal * (1 - np.exp(-tempo / constante_tempo))


def velocidade_quadratica(
    tempo: np.ndarray, massa: float, coeficiente: float, gravidade: float = GRAVIDADE
) -> np.ndarray:
    """Velocidade de queda com arrasto quadrático, partindo do repouso."""
    velocidade_terminal = np.sqrt(massa * gravidade / coeficiente)
    return velocidade_terminal * np.tanh(gravidade * tempo / velocidade_terminal)


# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------


def criar_figura(
    tempo, velocidade_l, velocidade_q, velocidade_livre, instante=None, modelo=None,
    velocidade_atual=None, forca_arrasto=None, peso=None
):
    """Cria o gráfico escuro de velocidade em função do tempo."""
    figura, eixo = plt.subplots(figsize=(8, 4.6), facecolor="#0e1117")
    eixo.set_facecolor("#151a23")
    eixo.plot(
        tempo, velocidade_l, color="#38bdf8", linewidth=2.8, label="Arrasto linear"
    )
    eixo.plot(
        tempo,
        velocidade_q,
        color="#c084fc",
        linewidth=2.8,
        label="Arrasto quadrático",
    )
    eixo.plot(
        tempo,
        velocidade_livre,
        color="#fbbf24",
        linewidth=2,
        linestyle="--",
        label="Sem arrasto: queda livre",
    )
    eixo.set_xlabel("Tempo (s)", color="#cbd5e1")
    eixo.set_ylabel("Velocidade (m/s)", color="#cbd5e1")
    eixo.set_title("Velocidade de queda", color="#f8fafc", loc="left", pad=14)
    eixo.tick_params(colors="#cbd5e1")
    eixo.grid(color="#475569", alpha=0.3, linewidth=0.8)
    eixo.spines[["top", "right"]].set_visible(False)
    eixo.spines[["left", "bottom"]].set_color("#475569")
    eixo.legend(
        facecolor="#151a23",
        edgecolor="#334155",
        labelcolor="#e2e8f0",
        framealpha=1,
    )
    if instante is not None and velocidade_atual is not None:
        cor = "#38bdf8" if modelo == "linear" else "#c084fc"
        eixo.axvline(instante, color="#f8fafc", alpha=0.4, linewidth=1)
        eixo.scatter(
            [instante], [velocidade_atual], color=cor, edgecolor="#f8fafc",
            linewidth=1.2, s=85, zorder=5,
        )
        eixo.annotate(
            f"t = {instante:.1f} s\nv = {velocidade_atual:.2f} m/s\n"
            f"Fₐ = {forca_arrasto:.2f} N / mg = {peso:.2f} N",
            (instante, velocidade_atual),
            xytext=(12, 12),
            textcoords="offset points",
            color="#f8fafc",
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.4", "fc": "#0e1117", "ec": cor, "alpha": 0.95},
        )
    figura.tight_layout()
    return figura, eixo


def animar_grafico(
    area, tempo, velocidade_l, velocidade_q, velocidade_livre,
    massa, coeficiente_linear, coeficiente_quadratico, modelo
):
    """Anima o marcador no próprio gráfico das curvas de velocidade."""
    for instante in np.linspace(0, tempo[-1], 45):
        if modelo == "linear":
            velocidade = float(
                velocidade_linear(np.array([instante]), massa, coeficiente_linear)[0]
            )
            forca_arrasto = coeficiente_linear * velocidade
        else:
            velocidade = float(
                velocidade_quadratica(
                    np.array([instante]), massa, coeficiente_quadratico
                )[0]
            )
            forca_arrasto = coeficiente_quadratico * velocidade**2

        figura, _ = criar_figura(
            tempo,
            velocidade_l,
            velocidade_q,
            velocidade_livre,
            instante=instante,
            modelo=modelo,
            velocidade_atual=velocidade,
            forca_arrasto=forca_arrasto,
            peso=massa * GRAVIDADE,
        )
        area.pyplot(figura)
        plt.close(figura)
        time.sleep(0.04)


def renderizar():
    st.subheader("Força de arrasto")
    st.caption(
        "A força de arrasto se opõe à queda. A curva amarela tracejada representa "
        "a queda livre, sem resistência do ar."
    )

    col_controles, col_visualizacao, col_valores = st.columns([1.1, 2.4, 1.1])
    with col_controles:
        massa = st.slider("Massa (kg)", 0.1, 10.0, 1.0, 0.1)
        coeficiente_linear = st.slider(
            "Coeficiente linear b (kg/s)", 0.1, 5.0, 0.5, 0.1
        )
        coeficiente_quadratico = st.slider(
            "Coeficiente quadrático c (kg/m)", 0.1, 5.0, 0.5, 0.1
        )
        duracao = st.slider("Tempo máximo (s)", 0.1, 10.0, 10.0, 0.5)
        modelo = st.radio(
            "Animação",
            ("linear", "quadrático"),
            format_func=lambda valor: f"Arrasto {valor}",
        )

    vt_linear, _, vt_quadratico = calcular_grandezas(
        massa, coeficiente_linear, coeficiente_quadratico
    )
    tempo = np.linspace(0, duracao, 500)
    velocidade_l = velocidade_linear(tempo, massa, coeficiente_linear)
    velocidade_q = velocidade_quadratica(tempo, massa, coeficiente_quadratico)
    velocidade_livre = GRAVIDADE * tempo

    with col_visualizacao:
        area_grafico = st.empty()
        figura, _ = criar_figura(tempo, velocidade_l, velocidade_q, velocidade_livre)
        area_grafico.pyplot(figura)
        plt.close(figura)
        if st.button("▶ Iniciar animação"):
            animar_grafico(
                area_grafico,
                tempo,
                velocidade_l,
                velocidade_q,
                velocidade_livre,
                massa,
                coeficiente_linear,
                coeficiente_quadratico,
                modelo,
            )

    with col_valores:
        st.markdown("#### Valores")
        st.metric(
            "Terminal · linear",
            f"{vt_linear:.2f} m/s",
            delta=f"no gráfico: {velocidade_l[-1]:.2f} m/s",
            delta_color="off",
        )
        st.metric(
            "Terminal · quadrático",
            f"{vt_quadratico:.2f} m/s",
            delta=f"no gráfico: {velocidade_q[-1]:.2f} m/s",
            delta_color="off",
        )
        st.metric("Queda livre ao final", f"{velocidade_livre[-1]:.2f} m/s")
        st.caption("Durante a animação, o marcador mostra t, v e a força de arrasto.")

    with st.expander("Equações utilizadas"):
        st.latex(r"\text{Arrasto linear:} \qquad F_d = -b v")
        st.latex(r"v_{\text{terminal}} = \frac{mg}{b}")
        st.latex(r"\tau = \frac{m}{b}")
        st.latex(r"v(t) = v_{\text{terminal}} \left(1 - e^{-\frac{t}{\tau}}\right)")
        st.latex(
            r"x(t) = v_{\text{terminal}}\left[t-\tau\left(1-e^{-\frac{t}{\tau}}\right)\right]"
        )
        st.latex(r"\text{Arrasto quadrático:} \qquad F_d = -c v|v|")
        st.latex(r"v_{\text{terminal}} = \sqrt{\frac{mg}{c}}")
        st.latex(r"v(t) = v_{\text{terminal}} \tanh\left(\frac{g t}{v_{\text{terminal}}}\right)")
        st.latex(
            r"y(t) = \frac{v_{\text{terminal}}^2}{g} "
            r"\ln\left(\cosh\left(\frac{g t}{v_{\text{terminal}}}\right)\right)"
        )
