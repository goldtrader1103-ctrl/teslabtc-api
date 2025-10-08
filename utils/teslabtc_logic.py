from typing import Dict, Any

def evaluate_confirmations(
    tendencia_h4: bool,
    bos_m15: bool,
    poi_ob_fvg: bool,
    retroceso_ok: bool,
    volumen_ok: bool,
    sesion_ok: bool
) -> Dict[str, Any]:
    conf = {
        "Tendencia H4": "✅" if tendencia_h4 else "❌",
        "BOS M15": "✅" if bos_m15 else "⚠️ Pendiente",
        "POI/OB/FVG": "✅" if poi_ob_fvg else "❌",
        "Retroceso <61.8%": "✅" if retroceso_ok else "⚠️",
        "Volumen": "✅" if volumen_ok else "⚠️",
        "Sesión NY": "✅" if sesion_ok else "❌"
    }
    score = sum([v == "✅" for v in conf.values()])
    return conf, score

def teslabtc_conclusion(direction_macro_up: bool, bos_m15: bool) -> str:
    if direction_macro_up and bos_m15:
        return "📊 Alcista: Esperar retroceso en demanda para BUY en M15 (Ejecución M5 — Level Entry)."
    if (not direction_macro_up) and bos_m15:
        return "📊 Bajista: Esperar retroceso en oferta para SELL en M15 (Ejecución M5 — Level Entry)."
    return "📊 Setup potencial: Esperar BOS en M15 dentro de zona H1/H4 antes de ejecutar."

def level_entry_guidance(long: bool = True) -> Dict[str, str]:
    if long:
        return {
            "entrada": "OB/FVG M5 (inicio o 50%) tras BOS M15 alcista",
            "sl": "Bajo el mínimo de invalidación estructural",
            "tp": "Liquidez siguiente, RRR ≥ 1:3",
            "gestion": "BE en 1:1, 50% en 1:2, dejar correr a 1:3"
        }
    else:
        return {
            "entrada": "OB/FVG M5 (inicio o 50%) tras BOS M15 bajista",
            "sl": "Sobre el máximo de invalidación estructural",
            "tp": "Liquidez siguiente, RRR ≥ 1:3",
            "gestion": "BE en 1:1, 50% en 1:2, dejar correr a 1:3"
        }
