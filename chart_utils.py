import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import COLORS


def create_standard_layout(height=300):
    """Create standard layout configuration for charts."""
    return dict(
        template="plotly_dark",
        font_color=COLORS["text_light"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        height=height,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            font_color=COLORS["text_black"],
        ),
    )


def add_value_labels(fig, values, size=14, color="#ffffff"):
    """Add value labels to chart traces."""
    fig.update_traces(
        text=[f"${v:,.0f}" for v in values],
        textposition="outside",
        textfont=dict(color=color, size=size, family="Arial Black"),
    )
    return fig


def create_timeline_chart(timeline_df):
    """Create income vs expense timeline chart."""
    fig = px.bar(
        timeline_df,
        x="date",
        y="amount",
        color="event",
        barmode="group",
        labels={"amount": "Amount (COP)", "date": "Date", "event": "Type"},
        color_discrete_map={
            "income": COLORS["income"],
            "expense": COLORS["expense"],
        },
    )
    fig.update_layout(**create_standard_layout(350))
    fig = add_value_labels(fig, timeline_df["amount"])
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>"
    )
    return fig


def create_pie_chart(values, names, title="Category share"):
    """Create pie chart with dark text."""
    fig = px.pie(values=values, names=names, title=title)
    fig.update_layout(
        template="plotly_dark",
        font=dict(color=COLORS["text_black"], size=14),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=450,
        showlegend=True,
        legend=dict(
            font=dict(color=COLORS["text_black"], size=13, family="Arial"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor=COLORS["text_black"],
            borderwidth=2,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            font_color=COLORS["text_black"],
        ),
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color=COLORS["text_dark"], size=12),
        hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.0f} COP<br>Percentage: %{percent}<extra></extra>",
        marker=dict(line=dict(color=COLORS["text_dark"], width=2)),
        hole=0.0,
        pull=[0.05] * len(values),
    )
    return fig


def create_bar_chart(x_data, y_data, title, x_label, y_label, add_labels=True):
    """Create standard bar chart with value labels."""
    fig = px.bar(
        x=x_data,
        y=y_data,
        labels={"x": x_label, "y": y_label},
        title=title,
        text=[f"${y:,.0f}" for y in y_data] if add_labels else None,
    )
    fig.update_layout(**create_standard_layout(300))
    if add_labels:
        fig.update_traces(
            textposition="outside",
            textfont=dict(color=COLORS["white"], size=14, family="Arial Black"),
        )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>"
    )
    return fig


def create_origin_chart_with_projections(origin_sum, projected_5050, already_paid_5050):
    """Create origin chart with projected and already paid 50/50 bars."""
    origin_data = origin_sum.to_dict()
    origin_data["Projected 50/50 (÷2)"] = projected_5050
    origin_data["Already Paid 50/50 (÷2)"] = already_paid_5050

    fig = px.bar(
        x=list(origin_data.keys()),
        y=list(origin_data.values()),
        labels={"x": "Origin", "y": "Amount (COP)"},
        title="Expenses by origin (includes 50/50 calculations)",
        text=[f"${y:,.0f}" for y in origin_data.values()],
    )
    fig.update_layout(**create_standard_layout(300))
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=COLORS["white"], size=14, family="Arial Black"),
        hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>",
    )
    return fig


def create_monthly_chart(monthly_df):
    """Create monthly income vs expense chart with value labels."""
    fig = px.bar(
        monthly_df,
        x="month",
        y="amount",
        color="event_lower",
        barmode="group",
        labels={"amount": "Amount (COP)", "month": "Month", "event_lower": "Type"},
        color_discrete_map={
            "income": COLORS["income"],
            "expense": COLORS["expense"],
        },
        text=[f"${y:,.0f}" for y in monthly_df["amount"]],
    )
    fig.update_layout(
        **create_standard_layout(300),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
            tickangle=45,
        ),
        legend=dict(font_color=COLORS["text_light"]),
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=COLORS["white"], size=12, family="Arial Black"),
        hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f} COP<extra></extra>",
    )
    return fig


def create_partner_ratio_chart(df_filtered):
    """Create Partner 1 vs Partner 2 expense ratio chart (non-50/50 expenses only)."""
    # Filter for non-50/50 expenses (Partner 1 and Partner 2 only)
    non_5050 = df_filtered[
        df_filtered["distribution"].isin(["Partner 1", "Partner 2"])
    ]

    if non_5050.empty:
        return None

    # Calculate totals
    ratio_data = non_5050.groupby("distribution")["amount"].sum()

    if ratio_data.empty:
        return None

    # Create horizontal bar chart
    fig = go.Figure()

    colors_map = {
        "Partner 1": "rgba(59, 130, 246, 0.8)",
        "Partner 2": "rgba(236, 72, 153, 0.8)",
    }

    for person in ratio_data.index:
        fig.add_trace(
            go.Bar(
                y=[person],
                x=[ratio_data[person]],
                orientation="h",
                marker=dict(
                    color=colors_map.get(person, "rgba(100, 100, 100, 0.8)")
                ),
                text=[f"${ratio_data[person]:,.0f}"],
                textposition="outside",
                textfont=dict(color=COLORS["white"], size=16, family="Arial Black"),
                name=person,
            )
        )

    # Calculate ratio
    total = ratio_data.sum()
    p1_pct = (ratio_data.get("Partner 1", 0) / total * 100) if total > 0 else 0
    p2_pct = (ratio_data.get("Partner 2", 0) / total * 100) if total > 0 else 0

    fig.update_layout(
        title=f"Partner 1 vs Partner 2 Expenses (non-50/50) — Ratio: {p1_pct:.1f}% / {p2_pct:.1f}%",
        template="plotly_dark",
        font_color=COLORS["text_light"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Amount (COP)",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
            tickfont=dict(color=COLORS["white"], size=14, family="Arial Black"),
        ),
        height=200,
        showlegend=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            font_color=COLORS["text_black"],
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.0f} COP<extra></extra>"
    )

    return fig


def create_fixed_expenses_chart(df_fixed):
    """Create fixed expenses expected vs already paid chart."""
    chart_data = []
    for _, row in df_fixed.iterrows():
        expense_name = row.get("details", "Unknown")
        expected_amount = row.get("amount", 0)
        paid_percentage = row.get("amount_paid%", 0)

        paid_amount = (
            expected_amount * (paid_percentage / 100) if paid_percentage > 0 else 0
        )

        chart_data.append(
            {"Expense": expense_name, "Type": "Expected", "Amount": expected_amount}
        )
        chart_data.append(
            {"Expense": expense_name, "Type": "Already Paid", "Amount": paid_amount}
        )

    df_chart = pd.DataFrame(chart_data)

    fig = go.Figure()

    # Add Expected bars
    expected_data = df_chart[df_chart["Type"] == "Expected"].sort_values(
        "Amount", ascending=True
    )
    fig.add_trace(
        go.Bar(
            y=expected_data["Expense"],
            x=expected_data["Amount"],
            name="Expected",
            orientation="h",
            marker=dict(color="rgba(59, 130, 246, 0.6)"),
            text=expected_data["Amount"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
            textfont=dict(color=COLORS["white"], size=16, family="Arial Black"),
        )
    )

    # Add Already Paid bars
    paid_data = df_chart[df_chart["Type"] == "Already Paid"].sort_values(
        "Amount", ascending=True
    )
    fig.add_trace(
        go.Bar(
            y=paid_data["Expense"],
            x=paid_data["Amount"],
            name="Already Paid",
            orientation="h",
            marker=dict(color="rgba(46, 204, 113, 0.8)"),
            text=paid_data["Amount"].apply(lambda x: f"${x:,.0f}" if x > 0 else ""),
            textposition="inside",
            textfont=dict(color=COLORS["white"], size=32, family="Arial Black"),
        )
    )

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        font_color=COLORS["text_dark"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Amount (COP)",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
            tickfont=dict(color=COLORS["white"], size=14, family="Arial Black"),
        ),
        legend=dict(
            font_color=COLORS["text_light"],
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        height=max(600, len(df_fixed) * 40),
        showlegend=True,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            font_color=COLORS["text_black"],
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.0f} COP<extra></extra>"
    )

    return fig


def create_one_time_expenses_chart(one_time_summary):
    """Create one-time expenses chart."""
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=one_time_summary.index,
            x=one_time_summary.values,
            orientation="h",
            marker=dict(color="rgba(255, 159, 64, 0.8)"),
            text=[f"${x:,.0f}" for x in one_time_summary.values],
            textposition="outside",
            textfont=dict(color=COLORS["white"], size=16, family="Arial Black"),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        font_color=COLORS["text_light"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Amount (COP)",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)",
            title_font_color=COLORS["text_light"],
        ),
        height=max(600, len(one_time_summary) * 40),
        showlegend=False,
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial",
            font_color=COLORS["text_black"],
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Amount: $%{x:,.0f} COP<extra></extra>"
    )

    return fig


def create_debt_sankey(df_expenses):
    """
    Create Sankey diagram showing expense flow and debt distribution.
    Based on 18 cases of distribution × origin combinations.

    Logic:
    - Nothing: distribution matches origin proportionally (6 cases)
    - Partner 2 owes: expenses paid from Partner 1's account (6 cases)
    - Partner 1 owes: expenses paid from Partner 2's account (6 cases)
    """
    if df_expenses.empty:
        return None

    # Calculate amounts for each case
    nothing_amount = 0
    p2_owes_50 = 0
    p2_owes_100 = 0
    p1_owes_50 = 0
    p1_owes_100 = 0

    for _, row in df_expenses.iterrows():
        distribution = row.get("distribution", "")
        origin = row.get("origin", "")
        amount = row.get("amount", 0)

        # Normalize origin names for comparison
        origin_lower = origin.lower()

        # NOTHING CASES (6 cases)
        # Case 1, 10: 50/50 + Rent
        if distribution == "50/50" and "rent" in origin_lower:
            nothing_amount += amount
        # Case 5, 14: Partner 1 + Savings account Partner 1
        elif distribution == "Partner 1" and "partner 1" in origin_lower and "savings" in origin_lower:
            nothing_amount += amount
        # Case 9, 18: Partner 2 + Savings account Partner 2
        elif distribution == "Partner 2" and "partner 2" in origin_lower and "savings" in origin_lower:
            nothing_amount += amount

        # PARTNER 2 OWES CASES (6 cases)
        # Case 2, 11: 50/50 + Savings account Partner 1 (Partner 2 owes 50% of total)
        elif distribution == "50/50" and "partner 1" in origin_lower and "savings" in origin_lower:
            p2_owes_50 += amount * 0.5
        # Case 7, 16: Partner 2 + Rent (Partner 2 owes 100%)
        elif distribution == "Partner 2" and "rent" in origin_lower:
            p2_owes_100 += amount
        # Case 8, 17: Partner 2 + Savings account Partner 1 (Partner 2 owes 100%)
        elif distribution == "Partner 2" and "partner 1" in origin_lower and "savings" in origin_lower:
            p2_owes_100 += amount

        # PARTNER 1 OWES CASES (6 cases)
        # Case 4, 13: Partner 1 + Rent (Partner 1 owes 50%)
        elif distribution == "Partner 1" and "rent" in origin_lower:
            p1_owes_50 += amount * 0.5
        # Case 3, 12: 50/50 + Savings account Partner 2 (Partner 1 owes 50%)
        elif distribution == "50/50" and "partner 2" in origin_lower and "savings" in origin_lower:
            p1_owes_100 += amount * 0.5
        # Case 6, 15: Partner 1 + Savings account Partner 2 (Partner 1 owes 100%)
        elif distribution == "Partner 1" and "partner 2" in origin_lower and "savings" in origin_lower:
            p1_owes_100 += amount

    # Build Sankey nodes
    labels = []
    node_colors = []

    def add_node(name, color):
        labels.append(name)
        node_colors.append(color)
        return len(labels) - 1

    # Left side - Layer 1: Individual nothing categories
    p1_nothing_node = add_node("P1 Nothing", "rgba(59, 130, 246, 0.5)")
    rent_5050_nothing_node = add_node("Rent 50/50", "rgba(100, 200, 100, 0.8)")
    p2_nothing_node = add_node("P2 Nothing", "rgba(236, 72, 153, 0.5)")

    # Left side - Layer 2: Summary nodes
    total_nothing_node = add_node("NOTHING OWED", "rgba(100, 200, 100, 1.0)")
    rent_owed_summary_node = add_node("RENT DEBT", "rgba(150, 150, 150, 0.8)")

    # Left side - Layer 3: Individual rent debts
    p2_rent_node = add_node("P2→Rent", "rgba(236, 72, 153, 0.7)")
    p1_rent_node = add_node("P1→Rent", "rgba(59, 130, 246, 0.7)")

    # Center node
    expenses_node = add_node("TOTAL", "rgba(200, 200, 200, 1.0)")

    # Right side - Layer 1: Summary nodes by person
    p2_total_expenses_node = add_node("P2 EXPENSES", "rgba(236, 72, 153, 0.6)")
    p1_total_expenses_node = add_node("P1 EXPENSES", "rgba(59, 130, 246, 0.6)")

    # Right side - Layer 2: Individual debt categories
    p2_5050_node = add_node("P2→50/50", "rgba(236, 72, 153, 0.7)")
    p2_p1_node = add_node("P2→P1", "rgba(236, 72, 153, 0.9)")
    p1_5050_node = add_node("P1→50/50", "rgba(59, 130, 246, 0.7)")
    p1_p2_node = add_node("P1→P2", "rgba(59, 130, 246, 0.9)")

    # Right side - Layer 3: Final totals
    p2_total_node = add_node("P2 OWES", "rgba(220, 38, 127, 1.0)")
    p1_total_node = add_node("P1 OWES", "rgba(37, 99, 235, 1.0)")

    # Calculate amounts for each category
    p1_nothing_amount = 0  # Case 5, 14: Partner 1 + Savings Partner 1
    rent_5050_amount = 0  # Case 1, 10: 50/50 + Rent
    p2_nothing_amount = 0  # Case 9, 18: Partner 2 + Savings Partner 2
    p2_rent_debt = 0  # Cases 7, 16: Partner 2 + Rent
    p1_rent_debt = 0  # Cases 4, 13: Partner 1 + Rent

    # Right side: Savings account expenses (full amounts)
    savings_p1_total = 0  # All from Savings Partner 1
    savings_p2_total = 0  # All from Savings Partner 2

    # Debt categories from savings accounts
    p2_5050_debt = 0  # Cases 2, 11: 50/50 + Savings Partner 1
    p2_p1_debt = 0  # Cases 8, 17: Partner 2 + Savings Partner 1
    p1_5050_debt = 0  # Cases 3, 12: 50/50 + Savings Partner 2
    p1_p2_debt = 0  # Cases 6, 15: Partner 1 + Savings Partner 2

    # Recalculate all amounts
    for _, row in df_expenses.iterrows():
        distribution = row.get("distribution", "")
        origin = row.get("origin", "")
        amount = row.get("amount", 0)
        origin_lower = origin.lower()

        # LEFT SIDE: Nothing cases
        if distribution == "Partner 1" and "partner 1" in origin_lower and "savings" in origin_lower:
            p1_nothing_amount += amount  # Case 5, 14
        elif distribution == "50/50" and "rent" in origin_lower:
            rent_5050_amount += amount  # Case 1, 10
        elif distribution == "Partner 2" and "partner 2" in origin_lower and "savings" in origin_lower:
            p2_nothing_amount += amount  # Case 9, 18

        # LEFT SIDE: Rent debts
        elif distribution == "Partner 2" and "rent" in origin_lower:
            p2_rent_debt += amount * 0.5  # Cases 7, 16
        elif distribution == "Partner 1" and "rent" in origin_lower:
            p1_rent_debt += amount * 0.5  # Cases 4, 13

        # RIGHT SIDE: Savings account totals and debts
        if "partner 1" in origin_lower and "savings" in origin_lower:
            if distribution == "50/50":
                p2_5050_debt += amount * 0.5  # Cases 2, 11
                savings_p1_total += amount
            elif distribution == "Partner 2":
                p2_p1_debt += amount  # Cases 8, 17
                savings_p1_total += amount

        if "partner 2" in origin_lower and "savings" in origin_lower:
            if distribution == "50/50":
                p1_5050_debt += amount * 0.5  # Cases 3, 12
                savings_p2_total += amount
            elif distribution == "Partner 1":
                p1_p2_debt += amount  # Cases 6, 15
                savings_p2_total += amount

    # Build links
    sources = []
    targets = []
    values = []
    link_colors = []

    # LEFT SIDE - Layer 1: Individual nothing → TOTAL NOTHING
    if p1_nothing_amount > 0:
        sources.append(p1_nothing_node)
        targets.append(total_nothing_node)
        values.append(p1_nothing_amount)
        link_colors.append("rgba(59, 130, 246, 0.3)")

    if rent_5050_amount > 0:
        sources.append(rent_5050_nothing_node)
        targets.append(total_nothing_node)
        values.append(rent_5050_amount)
        link_colors.append("rgba(100, 200, 100, 0.3)")

    if p2_nothing_amount > 0:
        sources.append(p2_nothing_node)
        targets.append(total_nothing_node)
        values.append(p2_nothing_amount)
        link_colors.append("rgba(236, 72, 153, 0.3)")

    # LEFT SIDE - Layer 2: TOTAL NOTHING → CENTER
    total_nothing = p1_nothing_amount + rent_5050_amount + p2_nothing_amount
    if total_nothing > 0:
        sources.append(total_nothing_node)
        targets.append(expenses_node)
        values.append(total_nothing)
        link_colors.append("rgba(100, 200, 100, 0.4)")

    # LEFT SIDE - Layer 1: Individual rent debts → RENT OWED
    if p2_rent_debt > 0:
        sources.append(p2_rent_node)
        targets.append(rent_owed_summary_node)
        values.append(p2_rent_debt)
        link_colors.append("rgba(236, 72, 153, 0.4)")

    if p1_rent_debt > 0:
        sources.append(p1_rent_node)
        targets.append(rent_owed_summary_node)
        values.append(p1_rent_debt)
        link_colors.append("rgba(59, 130, 246, 0.4)")

    # LEFT SIDE - Layer 2: RENT OWED → CENTER
    total_rent_owed = p2_rent_debt + p1_rent_debt
    if total_rent_owed > 0:
        sources.append(rent_owed_summary_node)
        targets.append(expenses_node)
        values.append(total_rent_owed)
        link_colors.append("rgba(150, 150, 150, 0.5)")

    # CENTER → RIGHT - Layer 1: debt-generating expenses BY ACCOUNT
    p2_account_expenses = savings_p2_total
    p1_account_expenses = savings_p1_total

    if p2_account_expenses > 0:
        sources.append(expenses_node)
        targets.append(p2_total_expenses_node)
        values.append(p2_account_expenses)
        link_colors.append("rgba(236, 72, 153, 0.4)")

    if p1_account_expenses > 0:
        sources.append(expenses_node)
        targets.append(p1_total_expenses_node)
        values.append(p1_account_expenses)
        link_colors.append("rgba(59, 130, 246, 0.4)")

    # RIGHT - Layer 2: Account expenses → Debts owed TO that account
    # Partner 1's account expenses → Partner 2 owes (because Partner 1 paid)
    if p2_5050_debt > 0:
        sources.append(p1_total_expenses_node)
        targets.append(p2_5050_node)
        values.append(p2_5050_debt)
        link_colors.append("rgba(236, 72, 153, 0.4)")

    if p2_p1_debt > 0:
        sources.append(p1_total_expenses_node)
        targets.append(p2_p1_node)
        values.append(p2_p1_debt)
        link_colors.append("rgba(236, 72, 153, 0.6)")

    # Partner 2's account expenses → Partner 1 owes (because Partner 2 paid)
    if p1_5050_debt > 0:
        sources.append(p2_total_expenses_node)
        targets.append(p1_5050_node)
        values.append(p1_5050_debt)
        link_colors.append("rgba(59, 130, 246, 0.4)")

    if p1_p2_debt > 0:
        sources.append(p2_total_expenses_node)
        targets.append(p1_p2_node)
        values.append(p1_p2_debt)
        link_colors.append("rgba(59, 130, 246, 0.6)")

    # FAR RIGHT - Layer 3: Individual debts → Final totals
    if p2_5050_debt > 0:
        sources.append(p2_5050_node)
        targets.append(p2_total_node)
        values.append(p2_5050_debt)
        link_colors.append("rgba(236, 72, 153, 0.5)")

    if p2_p1_debt > 0:
        sources.append(p2_p1_node)
        targets.append(p2_total_node)
        values.append(p2_p1_debt)
        link_colors.append("rgba(236, 72, 153, 0.7)")

    if p1_5050_debt > 0:
        sources.append(p1_5050_node)
        targets.append(p1_total_node)
        values.append(p1_5050_debt)
        link_colors.append("rgba(59, 130, 246, 0.5)")

    if p1_p2_debt > 0:
        sources.append(p1_p2_node)
        targets.append(p1_total_node)
        values.append(p1_p2_debt)
        link_colors.append("rgba(59, 130, 246, 0.7)")

    if not values:
        return None

    # Create Sankey diagram
    total_expenses = df_expenses["amount"].sum()
    node_values = []
    for idx in range(len(labels)):
        incoming = sum(
            [values[i] for i in range(len(values)) if targets[i] == idx]
        )
        node_values.append(
            incoming
            if incoming > 0
            else sum([values[i] for i in range(len(values)) if sources[i] == idx])
        )

    # Override center node to show total of ALL expenses
    node_values[expenses_node] = total_expenses

    fig = go.Figure(
        go.Sankey(
            node=dict(
                pad=20,
                thickness=30,
                line=dict(color="white", width=2),
                label=[
                    f"{labels[idx]}<br>${node_values[idx]:,.0f}"
                    for idx in range(len(labels))
                ],
                color=node_colors,
                customdata=[
                    f"${node_values[idx]:,.0f}" for idx in range(len(labels))
                ],
                hovertemplate="<b>%{label}</b><br>Amount: %{customdata}<extra></extra>",
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                hovertemplate="%{source.label} → %{target.label}<br>Amount: $%{value:,.0f}<extra></extra>",
            ),
            arrangement="snap",
            orientation="h",
        )
    )

    # Calculate totals for subtitle
    total_nothing = p1_nothing_amount + rent_5050_amount + p2_nothing_amount
    total_expenses = df_expenses["amount"].sum()
    p2_total = p2_rent_debt + p2_5050_debt + p2_p1_debt
    p1_total = p1_rent_debt + p1_5050_debt + p1_p2_debt

    fig.update_layout(
        title=dict(
            text=(
                f"Expense Flow & Debt Distribution<br>"
                f"<sub>Total Expenses: ${total_expenses:,.0f} | "
                f"P2 owes: ${p2_total:,.0f} | "
                f"P1 owes: ${p1_total:,.0f}</sub>"
            ),
            font=dict(size=20, color=COLORS["text_light"]),
        ),
        template="plotly_dark",
        font=dict(size=14, color=COLORS["text_light"], family="Arial Black"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=700,
        margin=dict(l=20, r=20, t=80, b=20),
    )

    return fig
