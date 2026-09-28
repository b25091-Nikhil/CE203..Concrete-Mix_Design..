import streamlit as st

st.set_page_config(
    page_title="IS 10262:2019 Concrete Mix Design Calculator",
    page_icon="🏗️",
    layout="wide",
)

# ============================================================
# CE203 / IS 10262 DATA
# ============================================================

# Standard-deviation / X values used in the CE203 example.
SD_TABLE = {
    10: (3.5, 5.0),
    15: (3.5, 5.0),
    20: (4.0, 5.5),
    25: (4.0, 5.5),
    30: (5.0, 6.5),
    35: (5.0, 6.5),
    40: (5.0, 6.5),
    45: (5.0, 6.5),
    50: (5.0, 6.5),
    55: (5.0, 6.5),
    60: (5.0, 6.5),
}

# Exposure values used for durability checks.
EXPOSURE = {
    "Mild": {
        "rcc_min_cement": 300,
        "rcc_max_wc": 0.55,
        "rcc_min_grade": 20,
        "pcc_min_cement": 220,
        "pcc_max_wc": 0.60,
        "pcc_min_grade": 0,
    },
    "Moderate": {
        "rcc_min_cement": 300,
        "rcc_max_wc": 0.50,
        "rcc_min_grade": 25,
        "pcc_min_cement": 240,
        "pcc_max_wc": 0.60,
        "pcc_min_grade": 15,
    },
    "Severe": {
        "rcc_min_cement": 320,
        "rcc_max_wc": 0.45,
        "rcc_min_grade": 30,
        "pcc_min_cement": 250,
        "pcc_max_wc": 0.50,
        "pcc_min_grade": 20,
    },
    "Very severe": {
        "rcc_min_cement": 340,
        "rcc_max_wc": 0.45,
        "rcc_min_grade": 35,
        "pcc_min_cement": 260,
        "pcc_max_wc": 0.45,
        "pcc_min_grade": 20,
    },
    "Extreme": {
        "rcc_min_cement": 360,
        "rcc_max_wc": 0.40,
        "rcc_min_grade": 40,
        "pcc_min_cement": 280,
        "pcc_max_wc": 0.40,
        "pcc_min_grade": 25,
    },
}

# Water content at 50 mm slump.
# CE203 Lecture 13 Table 4:
# 10 mm = 208 kg/m3
# 20 mm = 186 kg/m3
# 40 mm = 165 kg/m3
WATER_TABLE = {
    10: 208.0,
    20: 186.0,
    40: 165.0,
}

# Coarse aggregate reference values.
# The lecture explicitly demonstrates:
# 20 mm + Zone II + W/C 0.50 = 0.62
CA_REFERENCE_TABLE = {
    10: {
        "I": 0.44,
        "II": 0.46,
        "III": 0.48,
        "IV": 0.50,
    },
    20: {
        "I": 0.60,
        "II": 0.62,
        "III": 0.64,
        "IV": 0.66,
    },
    40: {
        "I": 0.69,
        "II": 0.71,
        "III": 0.73,
        "IV": 0.75,
    },
}

REFERENCE_CA_FRACTION = 0.62
REFERENCE_WC_FOR_CA_TABLE = 0.50

MAX_CEMENT = 450.0
AIR_CONTENT = 0.01


# ============================================================
# STRENGTH VS W/C GRAPH
# ============================================================

# Approximate digitization of the IS 10262 Fig. 1 shown
# in CE203 Lecture 13.
#
# Curve 1 = expected 28-day strength of 33 MPa and below
# Curve 2 = expected 28-day strength of 43 MPa and below 53 MPa
# Curve 3 = expected 28-day strength of 53 MPa and above
#
# These points are used to teach/interpolate the graph.

CURVE_X = [
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
]

CURVE_1 = [
    60.0,
    51.0,
    43.0,
    36.5,
    30.0,
    25.0,
    21.0,
    17.5,
    15.0,
]

CURVE_2 = [
    66.0,
    57.0,
    49.0,
    42.0,
    36.0,
    30.0,
    26.0,
    22.0,
    19.0,
]

CURVE_3 = [
    74.0,
    65.0,
    57.0,
    50.0,
    43.0,
    37.5,
    32.0,
    27.0,
    23.0,
]


def graph_wc_for_strength(target_strength, curve_points):
    """
    Piecewise-linear interpolation of the teaching version
    of the IS 10262 strength vs W/C graph.
    """

    import numpy as np

    x = np.asarray(CURVE_X, dtype=float)
    y = np.asarray(curve_points, dtype=float)

    if target_strength < y.min() or target_strength > y.max():
        return None

    return float(
        np.interp(
            target_strength,
            y[::-1],
            x[::-1],
        )
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 1.7rem 1.8rem;
    border-radius: 22px;
    background: linear-gradient(
        135deg,
        #101828 0%,
        #263b5a 100%
    );
    color: white;
    margin-bottom: 1.2rem;
}

.hero h1 {
    margin: 0;
    font-size: 2.15rem;
}

.hero p {
    margin: .45rem 0 0;
    opacity: .85;
}

.section {
    padding: 1rem 1.15rem;
    border: 1px solid #e4e7ec;
    border-radius: 18px;
    background: #fff;
    margin-bottom: 1rem;
}

.step {
    padding: 1rem 1.1rem;
    border-left: 5px solid #667085;
    border-radius: 12px;
    background: #f8fafc;
    margin: .65rem 0;
}

.result {
    padding: 1.15rem;
    border-radius: 17px;
    background: #f8fafc;
    border: 1px solid #e4e7ec;
}

.small {
    color: #667085;
    font-size: .9rem;
}

.big {
    font-size: 1.65rem;
    font-weight: 750;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="hero">
<h1>IS 10262:2019 Concrete Mix Design Calculator</h1>
<p>
CE203 Civil Engineering Materials • IIT Mandi
<br>
Calculation Steps + Graphs + Material Quantities
</p>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR INPUTS
# ============================================================

with st.sidebar:

    st.header("Design Inputs")

    grade = st.selectbox(
        "Concrete grade",
        [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60],
        index=6,
    )

    exposure = st.selectbox(
        "Exposure condition",
        list(EXPOSURE.keys()),
        index=2,
    )

    concrete_type = st.selectbox(
        "Concrete type",
        ["RCC", "PCC"],
    )

    cement_grade = st.selectbox(
        "Cement grade",
        [33, 43, 53],
        index=1,
    )

    st.divider()

    # --------------------------------------------------------
    # WORKABILITY
    # --------------------------------------------------------

    st.subheader("Workability")

    slump = st.number_input(
        "Required slump (mm)",
        min_value=25,
        max_value=200,
        value=75,
        step=25,
    )

    use_sp = st.checkbox(
        "Use superplasticizer",
        value=True,
    )

    sp_dosage = st.number_input(
        "SP dosage (% of cement)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.1,
        disabled=not use_sp,
    )

    sp_reduction = st.number_input(
        "Water reduction from SP (%)",
        min_value=0.0,
        max_value=50.0,
        value=23.0,
        step=1.0,
        disabled=not use_sp,
    )

    st.divider()

    # --------------------------------------------------------
    # STRENGTH / W/C
    # --------------------------------------------------------

    st.subheader("Strength / W-C Input")

    sd_auto = st.checkbox(
        "Use CE203/Table standard deviation",
        value=True,
    )

    if sd_auto:

        s_default, x_default = SD_TABLE.get(
            grade,
            (5.0, 6.5),
        )

        s = st.number_input(
            "Standard deviation, s (MPa)",
            min_value=0.0,
            value=float(s_default),
            step=0.1,
        )

        x = st.number_input(
            "X (MPa)",
            min_value=0.0,
            value=float(x_default),
            step=0.1,
        )

    else:

        s = st.number_input(
            "Standard deviation, s (MPa)",
            min_value=0.0,
            value=5.0,
            step=0.1,
        )

        x = st.number_input(
            "X (MPa)",
            min_value=0.0,
            value=6.5,
            step=0.1,
        )

    st.caption(
        "The calculator reads/interpolates the target strength "
        "from the CE203/IS 10262 Fig. 1 teaching graph."
    )

    use_graph_wc = st.checkbox(
        "Use Fig. 1 graph reading automatically",
        value=True,
    )

    strength_wc_manual = st.number_input(
        "Manual graph-read W/C",
        min_value=0.20,
        max_value=0.90,
        value=0.36,
        step=0.01,
        disabled=use_graph_wc,
    )

    st.divider()

    # --------------------------------------------------------
    # AGGREGATES
    # --------------------------------------------------------

    st.subheader("Aggregate Data")

    nominal_size = st.selectbox(
        "Nominal maximum aggregate size (mm)",
        [10, 20, 40],
        index=1,
    )

    zone = st.selectbox(
        "Fine aggregate zone",
        ["I", "II", "III", "IV"],
        index=1,
    )

    st.caption(
        "Reference CA fraction at W/C = 0.50."
    )

    ca_table_default = CA_REFERENCE_TABLE[
        nominal_size
    ][zone]

    ca_table_value = st.number_input(
        "CA volume fraction at W/C = 0.50",
        min_value=0.30,
        max_value=0.80,
        value=float(ca_table_default),
        step=0.01,
    )

    st.divider()

    # --------------------------------------------------------
    # MATERIAL TEST DATA
    # --------------------------------------------------------

    st.subheader("Material Test Data")

    cement_sg = st.number_input(
        "Cement specific gravity",
        min_value=2.5,
        max_value=3.5,
        value=3.15,
        step=0.01,
    )

    fa_sg = st.number_input(
        "Fine aggregate SG",
        min_value=2.0,
        max_value=3.5,
        value=2.65,
        step=0.01,
    )

    ca_sg = st.number_input(
        "Coarse aggregate SG",
        min_value=2.0,
        max_value=3.5,
        value=2.70,
        step=0.01,
    )

    sp_sg = st.number_input(
        "SP specific gravity",
        min_value=0.8,
        max_value=2.5,
        value=1.10,
        step=0.01,
    )

    # --------------------------------------------------------
    # AGGREGATE CONDITION
    # --------------------------------------------------------

    st.subheader("Aggregate Condition")

    fa_condition = st.selectbox(
        "Fine aggregate condition",
        ["SSD", "Dry", "Wet"],
    )

    fa_abs = st.number_input(
        "Fine aggregate absorption (%)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1,
    )

    fa_moisture = st.number_input(
        "Fine aggregate moisture (%)",
        min_value=0.0,
        max_value=15.0,
        value=0.0,
        step=0.1,
        disabled=fa_condition != "Wet",
    )

    ca_condition = st.selectbox(
        "Coarse aggregate condition",
        ["SSD", "Dry", "Wet"],
    )

    ca_abs = st.number_input(
        "Coarse aggregate absorption (%)",
        min_value=0.0,
        max_value=10.0,
        value=0.5,
        step=0.1,
    )

    ca_moisture = st.number_input(
        "Coarse aggregate moisture (%)",
        min_value=0.0,
        max_value=15.0,
        value=0.0,
        step=0.1,
        disabled=ca_condition != "Wet",
    )

    volume = st.number_input(
        "Concrete volume required (m³)",
        min_value=0.01,
        value=1.0,
        step=0.1,
    )


# ============================================================
# DURABILITY VALUES
# ============================================================

e = EXPOSURE[exposure]

if concrete_type == "RCC":

    min_cement = e["rcc_min_cement"]
    max_wc = e["rcc_max_wc"]
    min_grade = e["rcc_min_grade"]

else:

    min_cement = e["pcc_min_cement"]
    max_wc = e["pcc_max_wc"]
    min_grade = e["pcc_min_grade"]


# ============================================================
# TARGET MEAN STRENGTH
# ============================================================

target_1 = grade + 1.65 * s
target_2 = grade + x

target_mean = max(
    target_1,
    target_2,
)


# ============================================================
# STRENGTH BASED W/C
# ============================================================

if use_graph_wc:

    if cement_grade == 33:
        curve_number = 1
        selected_curve = CURVE_1

    elif cement_grade == 43:
        curve_number = 2
        selected_curve = CURVE_2

    else:
        curve_number = 3
        selected_curve = CURVE_3

    graph_wc = graph_wc_for_strength(
        target_mean,
        selected_curve,
    )

    if graph_wc is not None:
        strength_wc = graph_wc
    else:
        strength_wc = strength_wc_manual

else:

    curve_number = None
    graph_wc = None
    strength_wc = strength_wc_manual


# Durability maximum W/C also applies.
adopted_wc = min(
    strength_wc,
    max_wc,
)


# ============================================================
# WATER CONTENT
# ============================================================

water_base = WATER_TABLE[
    nominal_size
]

# CE203:
# +3% water for every 25 mm increase
# above 50 mm slump.

if slump >= 50:

    slump_steps = (
        slump - 50
    ) / 25

    water_before_sp = (
        water_base
        * (
            1
            + 0.03 * slump_steps
        )
    )

    water_rule_text = (
        f"{water_base:g} × "
        f"[1 + 0.03 × ({slump:g} − 50)/25]"
    )

else:

    water_before_sp = water_base

    water_rule_text = (
        f"{water_base:g} kg/m³ retained because "
        "the supplied CE203 rule specifies the "
        "+3% adjustment for increases above 50 mm."
    )


# ============================================================
# SUPERPLASTICIZER WATER REDUCTION
# ============================================================

if use_sp:

    water = (
        water_before_sp
        * (
            1
            - sp_reduction / 100
        )
    )

else:

    water = water_before_sp


# ============================================================
# CEMENT
# ============================================================

cement_strength = (
    water / adopted_wc
)

cement = max(
    cement_strength,
    min_cement,
)

# Actual final W/C after durability minimum cement.
actual_wc = (
    water / cement
)


# ============================================================
# COARSE AGGREGATE CORRECTION
# ============================================================

# CE203:
#
# Every 0.05 decrease in W/C
# → increase Vca by 0.01.

ca_correction = (
    REFERENCE_WC_FOR_CA_TABLE
    - actual_wc
) * (
    0.01 / 0.05
)

ca_fraction = (
    ca_table_value
    + ca_correction
)

ca_fraction = max(
    0.0,
    min(
        1.0,
        ca_fraction,
    ),
)

fa_fraction = (
    1.0 - ca_fraction
)


# ============================================================
# ABSOLUTE VOLUME METHOD
# ============================================================

v_cement = (
    cement
    / (
        cement_sg
        * 1000
    )
)

v_water = (
    water
    / 1000
)

if use_sp:

    sp_mass = (
        cement
        * sp_dosage
        / 100
    )

    v_sp = (
        sp_mass
        / (
            sp_sg
            * 1000
        )
    )

else:

    sp_mass = 0.0
    v_sp = 0.0


# Entrapped air
v_air = AIR_CONTENT


# Aggregate volume
v_aggregates = (
    1
    - (
        v_cement
        + v_water
        + v_sp
        + v_air
    )
)


# Aggregate volumes
v_ca_ssd = (
    v_aggregates
    * ca_fraction
)

v_fa_ssd = (
    v_aggregates
    * fa_fraction
)


# Aggregate masses
ca_ssd = (
    v_ca_ssd
    * ca_sg
    * 1000
)

fa_ssd = (
    v_fa_ssd
    * fa_sg
    * 1000
)


# ============================================================
# FIELD MOISTURE CORRECTION
# ============================================================

def field_batch_mass(
    ssd_mass,
    condition,
    absorption,
    moisture,
):

    if condition == "SSD":

        return (
            ssd_mass,
            0.0,
        )

    elif condition == "Dry":

        # SSD mass =
        # Dry mass × (1 + absorption)

        dry_mass = (
            ssd_mass
            / (
                1
                + absorption / 100
            )
        )

        water_needed = (
            ssd_mass
            - dry_mass
        )

        return (
            dry_mass,
            -water_needed,
        )

    else:

        # Wet aggregate
        wet_mass = (
            ssd_mass
            * (
                1
                + moisture / 100
            )
        )

        water_supplied = (
            wet_mass
            - ssd_mass
        )

        return (
            wet_mass,
            water_supplied,
        )


fa_batch, fa_water_delta = field_batch_mass(
    fa_ssd,
    fa_condition,
    fa_abs,
    fa_moisture,
)

ca_batch, ca_water_delta = field_batch_mass(
    ca_ssd,
    ca_condition,
    ca_abs,
    ca_moisture,
)

field_water = (
    water
    - fa_water_delta
    - ca_water_delta
)


# ============================================================
# DESIGN SUMMARY
# ============================================================

left, right = st.columns(
    [2.2, 1]
)

with left:

    st.markdown(
        "### Design Summary"
    )

    st.write(
        f"""
**M{grade} • {exposure} exposure • "
        f"{concrete_type} • {nominal_size} mm aggregate • "
        f"Zone {zone} • {slump:g} mm slump**
"""
    )

with right:

    st.metric(
        "Target mean strength",
        f"{target_mean:.2f} MPa",
    )


# ============================================================
# WARNINGS
# ============================================================

if grade < min_grade:

    st.error(
        f"M{grade} is below the {concrete_type} "
        f"minimum grade shown for {exposure} exposure: "
        f"M{min_grade}."
    )


if cement > MAX_CEMENT:

    st.warning(
        f"Calculated cement content = "
        f"{cement:.1f} kg/m³, which exceeds the "
        f"CE203 maximum of {MAX_CEMENT:.0f} kg/m³. "
        "The mix should be redesigned."
    )


# ============================================================
# MAIN METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Adopted W/C",
    f"{actual_wc:.3f}",
)

c2.metric(
    "Water",
    f"{water:.1f} kg/m³",
)

c3.metric(
    "Cement",
    f"{cement:.1f} kg/m³",
)

c4.metric(
    "Coarse Aggregate",
    f"{ca_ssd:.1f} kg/m³",
)


# ============================================================
# GRAPHS
# ============================================================

st.markdown(
    "## 📊 Graphs & Learning"
)

g1, g2, g3 = st.tabs(
    [
        "1. Strength vs W/C — IS 10262 Fig. 1",
        "2. Water vs Slump",
        "3. Coarse Aggregate Correction",
    ]
)


# ============================================================
# GRAPH 1
# ============================================================

with g1:

    import pandas as pd

    curve_df = pd.DataFrame(
        {
            "W/C": CURVE_X,
            "Curve 1 — 33 MPa and below": CURVE_1,
            "Curve 2 — 43 MPa to below 53 MPa": CURVE_2,
            "Curve 3 — 53 MPa and above": CURVE_3,
        }
    ).set_index(
        "W/C"
    )

    st.line_chart(
        curve_df,
        height=430,
    )

    st.markdown(
        """
### How to use the graph

1. Calculate the target mean strength.
2. Select the appropriate curve according to cement grade.
3. Locate the target strength on the Y-axis.
4. Move horizontally until the selected curve is reached.
5. Move vertically downward.
6. Read the corresponding W/C ratio from the X-axis.
"""
    )

    if graph_wc is not None:

        st.info(
            f"""
Selected cement grade = {cement_grade}

Target mean strength = {target_mean:.2f} MPa

Selected Curve = {curve_number}

Graph-based W/C ≈ {graph_wc:.3f}
"""
        )

    st.caption(
        "The points shown are approximate digitizations of "
        "the displayed CE203/IS 10262 graph and are used "
        "for teaching/interpolation."
    )


# ============================================================
# GRAPH 2
# ============================================================

with g2:

    import pandas as pd

    slump_values = list(
        range(
            50,
            201,
            25,
        )
    )

    water_graph = pd.DataFrame(
        {
            "Slump (mm)": slump_values,

            "Water (10 mm)": [
                WATER_TABLE[10]
                * (
                    1
                    + 0.03
                    * (
                        (s - 50)
                        / 25
                    )
                )
                for s in slump_values
            ],

            "Water (20 mm)": [
                WATER_TABLE[20]
                * (
                    1
                    + 0.03
                    * (
                        (s - 50)
                        / 25
                    )
                )
                for s in slump_values
            ],

            "Water (40 mm)": [
                WATER_TABLE[40]
                * (
                    1
                    + 0.03
                    * (
                        (s - 50)
                        / 25
                    )
                )
                for s in slump_values
            ],
        }
    ).set_index(
        "Slump (mm)"
    )

    st.line_chart(
        water_graph,
        height=400,
    )

    st.markdown(
        """
### How to use the graph

Start from the 50 mm slump water content:

| Aggregate size | Water at 50 mm slump |
|---|---:|
| 10 mm | 208 kg/m³ |
| 20 mm | 186 kg/m³ |
| 40 mm | 165 kg/m³ |

For every 25 mm increase in slump above 50 mm:

**Water increases by 3%.**
"""
    )

    st.caption(
        "The graph is generated from the CE203 Lecture 13 "
        "Table 4 values and the stated +3% adjustment rule."
    )


# ============================================================
# GRAPH 3
# ============================================================

with g3:

    import pandas as pd

    wc_values = [
        round(
            0.30 + 0.01 * i,
            2,
        )
        for i in range(31)
    ]

    ca_graph = pd.DataFrame(
        {
            "W/C": wc_values,

            "Vca — 20 mm + Zone II": [
                REFERENCE_CA_FRACTION
                + (
                    0.50 - wc
                )
                * (
                    0.01
                    / 0.05
                )
                for wc in wc_values
            ],
        }
    ).set_index(
        "W/C"
    )

    st.line_chart(
        ca_graph,
        height=400,
    )

    st.markdown(
        """
### Coarse aggregate correction

CE203 gives:

**For every 0.05 decrease in W/C → Vca increases by 0.01.**

Example:

If W/C decreases from 0.50 to 0.45:

**Vca = 0.62 + 0.01 = 0.63**
"""
    )

    st.caption(
        "This graph visualizes the correction relationship. "
        "It does not replace the original IS 10262 table."
    )


# ============================================================
# CALCULATION STEPS
# ============================================================

st.markdown(
    "## 🧮 Calculation Steps"
)


# ============================================================
# STEP 1
# ============================================================

with st.expander(
    "1. Target Mean Strength",
    expanded=True,
):

    st.markdown(
        f"""
### Characteristic strength

M{grade}

**fck = {grade:.1f} MPa**

### First expression

f'ck = fck + 1.65s

= {grade:.1f} + 1.65 × {s:.1f}

= **{target_1:.2f} MPa**

### Second expression

f'ck = fck + X

= {grade:.1f} + {x:.1f}

= **{target_2:.2f} MPa**

### Target mean strength

The higher value is selected:

**Target mean strength = {target_mean:.2f} MPa**
"""
    )


# ============================================================
# STEP 2
# ============================================================

with st.expander(
    "2. Water-Cement Ratio",
    expanded=True,
):

    st.markdown(
        f"""
### Strength requirement

Strength-based W/C from the CE203/IS 10262 Fig. 1 graph:

**W/C = {strength_wc:.3f}**

### Durability requirement

Maximum W/C for:

**{exposure} exposure + {concrete_type}**

= **{max_wc:.2f}**

### Adopted W/C

The more stringent requirement governs:

**Adopted W/C = min({strength_wc:.3f}, {max_wc:.2f})**

**Adopted W/C = {adopted_wc:.3f}**
"""
    )


# ============================================================
# STEP 3
# ============================================================

with st.expander(
    "3. Water Requirement",
    expanded=True,
):

    st.markdown(
        f"""
For {nominal_size}-mm aggregate at 50-mm slump:

**Base water = {water_base:.0f} kg/m³**

Required slump:

**{slump:g} mm**

Water calculation:

**{water_rule_text}**

Water before superplasticizer:

**{water_before_sp:.1f} kg/m³**
"""
    )

    if use_sp:

        st.markdown(
            f"""
Superplasticizer water reduction:

**{sp_reduction:.0f}%**

Water retained:

**{100 - sp_reduction:.0f}%**

Final water:

**{water:.1f} kg/m³**
"""
        )

    else:

        st.markdown(
            f"""
No superplasticizer used.

Final water:

**{water:.1f} kg/m³**
"""
        )


# ============================================================
# STEP 4
# ============================================================

with st.expander(
    "4. Cement Content",
    expanded=True,
):

    st.markdown(
        f"""
### Strength-based cement

C = Water / W/C

C = {water:.1f} / {adopted_wc:.3f}

C = **{cement_strength:.1f} kg/m³**

### Durability minimum cement

For {exposure} exposure:

**Minimum cement = {min_cement:.0f} kg/m³**

Therefore:

**Adopted cement = max({cement_strength:.1f}, {min_cement:.0f})**

**Adopted cement = {cement:.1f} kg/m³**

### Final W/C

W/C = Water / Cement

= {water:.1f} / {cement:.1f}

= **{actual_wc:.3f}**
"""
    )


# ============================================================
# STEP 5
# ============================================================

with st.expander(
    "5. Coarse Aggregate / Fine Aggregate Proportion",
    expanded=True,
):

    st.markdown(
        f"""
### IS 10262 reference value

For:

- Aggregate size = {nominal_size} mm
- Fine aggregate Zone = {zone}
- Reference W/C = 0.50

Entered CA volume fraction:

**Vca = {ca_table_value:.3f}**

### Correction

CE203 rule:

**Every 0.05 decrease in W/C → Vca increases by 0.01**

Correction:

({REFERENCE_WC_FOR_CA_TABLE:.2f} − {actual_wc:.3f})
× (0.01 / 0.05)

= **{ca_correction:+.3f}**

Therefore:

Vca = {ca_table_value:.3f} {ca_correction:+.3f}

**Vca = {ca_fraction:.3f}**

### Fine aggregate fraction

Vfa = 1 − Vca

= 1 − {ca_fraction:.3f}

**Vfa = {fa_fraction:.3f}**
"""
    )


# ============================================================
# STEP 6
# ============================================================

with st.expander(
    "6. Absolute Volume Method",
    expanded=True,
):

    st.markdown(
        f"""
### Volumes

#### Cement

Vcement = Cement / (SG × 1000)

= {cement:.1f} / ({cement_sg:.2f} × 1000)

= **{v_cement:.4f} m³**

#### Water

Vwater = Water / 1000

= {water:.1f} / 1000

= **{v_water:.4f} m³**

#### Superplasticizer

SP mass = **{sp_mass:.2f} kg**

VSP = **{v_sp:.4f} m³**

#### Entrapped air

Vair = **{v_air:.4f} m³**

### Total aggregate volume

Vagg = 1 − (Vcement + Vwater + VSP + Vair)

Vagg = **{v_aggregates:.4f} m³**

### Coarse aggregate

Vca = Vagg × CA fraction

= {v_aggregates:.4f} × {ca_fraction:.3f}

= **{v_ca_ssd:.4f} m³**

### Fine aggregate

Vfa = Vagg × FA fraction

= {v_aggregates:.4f} × {fa_fraction:.3f}

= **{v_fa_ssd:.4f} m³**
"""
    )


# ============================================================
# STEP 7
# ============================================================

with st.expander(
    "7. SSD Quantities & Moisture Correction",
    expanded=False,
):

    st.markdown(
        f"""
### SSD quantities for 1 m³

| Material | Quantity |
|---|---:|
| Cement | **{cement:.1f} kg** |
| Water | **{water:.1f} kg** |
| Fine aggregate | **{fa_ssd:.1f} kg** |
| Coarse aggregate | **{ca_ssd:.1f} kg** |
| Superplasticizer | **{sp_mass:.2f} kg** |

### Field quantities

Fine aggregate condition:

**{fa_condition}**

Fine aggregate field batch:

**{fa_batch:.1f} kg**

Coarse aggregate condition:

**{ca_condition}**

Coarse aggregate field batch:

**{ca_batch:.1f} kg**

Adjusted mixing water:

**{field_water:.1f} kg**
"""
    )


# ============================================================
# FINAL MIX
# ============================================================

st.markdown(
    "## 🏗️ Final Mix"
)

mix_ratio_sand = (
    fa_ssd / cement
)

mix_ratio_ca = (
    ca_ssd / cement
)

mix_ratio_water = (
    water / cement
)


r1, r2, r3, r4 = st.columns(4)

r1.metric(
    "Cement",
    f"{cement:.1f} kg/m³",
)

r2.metric(
    "Fine Aggregate",
    f"{fa_ssd:.1f} kg/m³",
)

r3.metric(
    "Coarse Aggregate",
    f"{ca_ssd:.1f} kg/m³",
)

r4.metric(
    "Water",
    f"{water:.1f} kg/m³",
)


st.markdown(
    f"""
<div class="result">

<div class="big">
Mix Ratio = 1 : {mix_ratio_sand:.2f} : {mix_ratio_ca:.2f}
</div>

<div class="small">
Cement : Fine Aggregate : Coarse Aggregate
</div>

<br>

<b>Water/Cement Ratio = {actual_wc:.3f}</b>

</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# PER 50 KG CEMENT
# ============================================================

st.markdown(
    "### Per 50 kg Cement"
)

bag_factor = (
    50 / cement
)

bag_data = {
    "Material": [
        "Cement",
        "Fine aggregate",
        "Coarse aggregate",
        "Water",
        "Superplasticizer",
    ],

    "Quantity": [
        50.0,
        fa_ssd * bag_factor,
        ca_ssd * bag_factor,
        water * bag_factor,
        sp_mass * bag_factor,
    ],

    "Unit": [
        "kg",
        "kg",
        "kg",
        "L",
        "kg",
    ],
}

st.dataframe(
    bag_data,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# REQUIRED VOLUME
# ============================================================

st.markdown(
    "### Mix Quantities for Required Volume"
)

final_data = {
    "Material": [
        "Cement",
        "Fine aggregate (SSD)",
        "Coarse aggregate (SSD)",
        "Water",
        "Superplasticizer",
    ],

    "Per 1 m³": [
        cement,
        fa_ssd,
        ca_ssd,
        water,
        sp_mass,
    ],

    f"For {volume:g} m³": [
        cement * volume,
        fa_ssd * volume,
        ca_ssd * volume,
        water * volume,
        sp_mass * volume,
    ],
}

st.dataframe(
    final_data,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CHECKS
# ============================================================

st.markdown(
    "## ✅ Design Checks"
)

checks = []

checks.append(
    (
        "✅"
        if grade >= min_grade
        else "⚠️",
        f"Grade M{grade} vs {concrete_type} minimum for "
        f"{exposure}: M{min_grade}.",
    )
)

checks.append(
    (
        "✅"
        if actual_wc <= max_wc + 1e-9
        else "⚠️",
        f"Final W/C = {actual_wc:.3f}; "
        f"maximum durability W/C = {max_wc:.2f}.",
    )
)

checks.append(
    (
        "✅"
        if cement <= MAX_CEMENT
        else "⚠️",
        f"Cement = {cement:.1f} kg/m³; "
        f"CE203 maximum shown = {MAX_CEMENT:.0f} kg/m³.",
    )
)

checks.append(
    (
        "✅"
        if v_aggregates > 0
        else "⚠️",
        f"Remaining aggregate volume = "
        f"{v_aggregates:.4f} m³.",
    )
)

checks.append(
    (
        "ℹ️",
        "Final proportions should be confirmed "
        "through trial mixes and actual laboratory "
        "material properties.",
    )
)

for icon, message in checks:

    st.write(
        f"{icon} {message}"
    )


# ============================================================
# LEARNING / LECTURE 15
# ============================================================

st.markdown(
    "## 📚 CE203 Learning Notes"
)

with st.expander(
    "Fresh Concrete",
    expanded=False,
):

    st.markdown(
        """
### Important fresh concrete properties

- Workability
- Consistency / slump
- Cohesiveness
- Segregation
- Bleeding
- Plasticity
- Setting time
- Finishability
- Pumpability
- Air content

These properties affect placing, compaction and
the selection of mix proportions.
"""
    )


with st.expander(
    "Hardened Concrete",
    expanded=False,
):

    st.markdown(
        """
### Important hardened concrete properties

- Compressive strength
- Tensile / flexural strength
- Modulus of elasticity
- Density
- Durability
- Permeability
- Shrinkage
- Creep
- Fire resistance
- Abrasion resistance
- Bond
- Thermal properties
"""
    )


with st.expander(
    "Durability",
    expanded=False,
):

    st.markdown(
        """
### Important durability problems

- Corrosion of reinforcement
- Carbonation
- Chloride attack
- Sulphate attack
- Alkali-silica reaction
- Freeze-thaw damage
- Abrasion
- Fire
- Leaching
- Shrinkage
- Chemical attack

### General durability idea

Aggressive environment
+
Permeability
+
Time

can lead to deterioration.

Durable concrete generally requires:

- Low permeability
- Adequate cover
- Suitable materials
- Proper compaction
- Proper curing
- Suitable mix proportions
- Good construction practices
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Source basis: CE203 Civil Engineering Materials Lectures 12–15 "
    "supplied for this project. Numerical mix-design steps are based "
    "mainly on Lectures 12–14. Lecture 15 provides fresh concrete, "
    "hardened concrete and durability context."
)