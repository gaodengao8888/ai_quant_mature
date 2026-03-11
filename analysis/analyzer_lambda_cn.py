from __future__ import annotations


def render_cn_summary(analysis):
    lines = [
        f"系统版本：{analysis.get('version', 'unknown')}",
        f"AI周期：{analysis.get('ai_cycle', 'unknown')}",
        f"市场状态：{analysis.get('market_regime', 'unknown')}",
        f"风险状态：{analysis.get('risk_status', 'unknown')}（分数 {analysis.get('risk_score', 0)}）",
    ]
    if analysis.get("highlights"):
        lines.append("关键信号：")
        lines.extend([f"- {x}" for x in analysis["highlights"][:8]])
    if analysis.get("actions"):
        lines.append("执行建议：")
        lines.extend([f"- {a['symbol']} {a['action']} {a.get('shares', 0)}股 @ {a.get('price') or a.get('exec_price')}" for a in analysis["actions"]])
    else:
        lines.append("执行建议：当前无新增交易动作。")
    if analysis.get("risks"):
        lines.append("主要风险：")
        lines.extend([f"- {r}" for r in analysis["risks"]])
    return "\n".join(lines)


def generate_analysis(portfolio, ai_cycle, market_regime, raw_signals, filtered_signals, risk, portfolio_plan, position_plan, trade_result, version_info=None):
    raw = raw_signals.get("signals", raw_signals if isinstance(raw_signals, list) else [])
    passed = filtered_signals.get("passed", [])
    rejected = filtered_signals.get("rejected", [])
    highlights = [f"{s['symbol']} 原始信号：{s['signal']}" for s in raw[:5]]
    highlights.extend([f"{s['symbol']} 通过过滤：{s['signal']}" for s in passed[:5]])
    highlights.extend([f"{s['symbol']} 阻断：{s.get('block_reason')}" for s in rejected[:5]])
    risks = list(risk.get("alerts", []))
    risks.extend([f"{x['order']['symbol']} 订单阻断：{x['reason']}" for x in trade_result.get("blocked_orders", [])])
    analysis = {
        "version": (version_info or {}).get("version", "unknown"),
        "ai_cycle": ai_cycle.get("ai_cycle", "unknown"),
        "market_regime": market_regime.get("market_regime", "unknown"),
        "risk_status": risk.get("status", "unknown"),
        "risk_score": risk.get("risk_score", 0),
        "portfolio_plan": portfolio_plan,
        "position_plan": position_plan,
        "highlights": highlights,
        "risks": risks,
        "actions": trade_result.get("results", []),
    }
    analysis["summary_cn"] = render_cn_summary(analysis)
    return analysis
