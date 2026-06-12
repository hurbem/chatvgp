import { useState } from "react";

// ─── Shield SVG por tamanho ───────────────────────────────────────────────────

const SIZES = {
  sm: {
    width: 24,
    height: 28,
    shield: "M12 1 L23 5.5 L23 14.5 Q23 21 12 25 Q1 21 1 14.5 L1 5.5 Z",
    inner: "M12 3 L21 7 L21 14.5 Q21 20 12 23 Q3 20 3 14.5 L3 7 Z",
    check: "M6,14 L10,18 L18,10",
    checkWidth: 2.2,
    star: null,
  },
  md: {
    width: 36,
    height: 42,
    shield: "M18 2 L34 9 L34 22 Q34 33 18 39 Q2 33 2 22 L2 9 Z",
    inner: "M18 5 L31 11 L31 22 Q31 31 18 36 Q5 31 5 22 L5 11 Z",
    check: "M9,22 L15,29 L27,16",
    checkWidth: 3.5,
    star: "M18,8 L20,13 L25,13 L21,16 L23,22 L18,19 L13,22 L15,16 L11,13 L16,13 Z",
  },
  lg: {
    width: 72,
    height: 84,
    shield: "M36 3 L69 17 L69 45 Q69 67 36 79 Q3 67 3 45 L3 17 Z",
    inner: "M36 8 L63 21 L63 45 Q63 63 36 73 Q9 63 9 45 L9 21 Z",
    check: "M18,45 L30,58 L54,32",
    checkWidth: 6,
    star: "M36,16 L39,24 L48,24 L41,29 L44,37 L36,32 L28,37 L31,29 L24,24 L33,24 Z",
  },
};

// ─── Escudo SVG ───────────────────────────────────────────────────────────────

function ShieldIcon({ size = "sm" }) {
  const s = SIZES[size];
  return (
    <svg
      width={s.width}
      height={s.height}
      viewBox={`0 0 ${s.width} ${s.height}`}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* Escudo base */}
      <path d={s.shield} fill="#F59E0B" stroke="#B45309" strokeWidth="1.2" />
      {/* Camada interna brilho */}
      <path d={s.inner} fill="#FBBF24" opacity="0.35" />
      {/* Estrela decorativa no topo (md e lg) */}
      {s.star && (
        <polygon points={s.star} fill="white" opacity="0.9" />
      )}
      {/* Checkmark */}
      <polyline
        points={s.check}
        stroke="white"
        strokeWidth={s.checkWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

// ─── Tooltip ──────────────────────────────────────────────────────────────────

function Tooltip({ children, text }) {
  const [visible, setVisible] = useState(false);

  return (
    <span
      style={{ position: "relative", display: "inline-flex", alignItems: "center" }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span
          role="tooltip"
          style={{
            position: "absolute",
            bottom: "calc(100% + 8px)",
            left: "50%",
            transform: "translateX(-50%)",
            background: "#1C1917",
            color: "#fff",
            fontSize: "11px",
            fontWeight: 400,
            whiteSpace: "nowrap",
            padding: "5px 10px",
            borderRadius: "5px",
            pointerEvents: "none",
            zIndex: 50,
            letterSpacing: "0.01em",
          }}
        >
          {text}
          {/* seta */}
          <span
            style={{
              position: "absolute",
              top: "100%",
              left: "50%",
              transform: "translateX(-50%)",
              width: 0,
              height: 0,
              borderLeft: "5px solid transparent",
              borderRight: "5px solid transparent",
              borderTop: "5px solid #1C1917",
            }}
          />
        </span>
      )}
    </span>
  );
}

// ─── FounderBadge ─────────────────────────────────────────────────────────────

/**
 * Selo "Aprovado pelo Fundador" do chatVGP.
 *
 * Props:
 *   size          "sm" | "md" | "lg"   — padrão "sm"
 *   showLabel     boolean              — exibe texto ao lado (padrão false)
 *   iverificado   boolean              — se false, não renderiza nada
 *   tooltipText   string               — texto do tooltip (opcional)
 */
export function FounderBadge({
  size = "sm",
  showLabel = false,
  iverificado = true,
  tooltipText = "Verificado pelo Fundador VGP",
}) {
  if (!iverificado) return null;

  const labelStyle = {
    sm: { fontSize: "11px", gap: "4px" },
    md: { fontSize: "13px", gap: "6px" },
    lg: { fontSize: "15px", gap: "8px" },
  }[size];

  const badge = (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: labelStyle.gap,
        cursor: "default",
      }}
      tabIndex={0}
    >
      <ShieldIcon size={size} />
      {showLabel && (
        <span
          style={{
            fontSize: labelStyle.fontSize,
            fontWeight: 500,
            color: "#B45309",
            lineHeight: 1,
          }}
        >
          Aprovado pelo Fundador
        </span>
      )}
    </span>
  );

  return <Tooltip text={tooltipText}>{badge}</Tooltip>;
}

export default FounderBadge;
