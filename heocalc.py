import streamlit as st

st.set_page_config(page_title="Flexible HEO Pechini Calculator", layout="wide")

# --- CSS INJECTION FOR STYLING ---
st.markdown(
    """
    <style>
    /* Hide the up/down arrows (spinners) in number inputs */
    input[type="number"]::-webkit-inner-spin-button, 
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="number"] {
        -moz-appearance: textfield;
    }
    
    /* INCREASE CHECKBOX TEXT SIZE */
    div[data-testid="stCheckbox"] label span {
        font-size: 1.3rem !important; 
        font-weight: 600;             
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Flexible HEO Pechini Recipe Calculator")

AVAILABLE_METALS = {
    "Barium": 261.34,      
    "Calcium": 236.15,     
    "Cerium": 434.22,      
    "Chromium": 400.15,    
    "Cobalt": 291.03,      
    "Copper": 241.60,      
    "Iron": 404.00,        
    "Lanthanum": 433.01,   
    "Magnesium": 256.41,   
    "Manganese": 251.01,   
    "Neodymium": 438.35,   
    "Nickel": 290.79,      
    "Praseodymium": 435.01,
    "Strontium": 211.63,    
    "Yttrium": 364.99,     
    "Zinc": 297.49,        
}    

ACRYLAMIDE_MW = 71.08
CITRIC_ACID_MONOHYDRATE_MW = 210.14

# --- SESSION STATE SETUP ---
# This allows the app to "remember" that you pressed the proceed button
if "metals_confirmed" not in st.session_state:
    st.session_state.metals_confirmed = False

# Callback to reset the form if the user checks/unchecks a box
def reset_confirmation():
    st.session_state.metals_confirmed = False

# --- TOP LEVEL INPUTS ---
col1, col2, col3 = st.columns(3)
with col1:
    target_mols = st.number_input("Target Total Moles of HEO", value=0.1, format="%.2f")
with col2:
    acry_ratio = st.number_input("Acrylamide : Total Metal Ratio", value=4.5, format="%.1f", step=0.1)
with col3:
    citric_ratio = st.number_input("Citric Acid : Total Metal Ratio", value=1.5, format="%.1f", step=0.1)

st.divider()

# --- 1. PRECURSOR SELECTION ---
st.header("1. Select Metals")
st.write("Check the metals you want to include in your synthesis:")

selected_metals = []
cols = st.columns(4) 

for index, metal in enumerate(AVAILABLE_METALS.keys()):
    with cols[index % 4]:
        # The on_change triggers the reset function if a box is toggled
        if st.checkbox(metal, key=f"check_{index}", on_change=reset_confirmation):
            selected_metals.append(metal)

# Prevent division by zero and hide the button if nothing is selected
if not selected_metals:
    st.warning("Please select at least one metal to continue.")
    st.stop() 

# The Proceed Button
if not st.session_state.metals_confirmed:
    if st.button("Confirm Metals & Proceed to Stoichiometry", type="primary"):
        st.session_state.metals_confirmed = True
        st.rerun() # Reloads the page to immediately show the next section

# --- 2. DEFINE STOICHIOMETRY ---
# This block only executes if the button above was clicked
if st.session_state.metals_confirmed:
    st.header("2. Define Stoichiometry")
    st.markdown("Ensure the sum of your stoichiometric fractions ($x$) equals exactly **1.0**.")

    metal_data = {}
    total_fraction = 0.0

    for metal in selected_metals:
        c_name, c_mw, c_frac = st.columns([2, 1, 1])
        
        with c_name:
            st.markdown(f"### **{metal}**")
            
        with c_mw:
            default_mw = AVAILABLE_METALS[metal]
            mw = st.number_input(f"MW (g/mol)", value=default_mw, format="%.2f", key=f"mw_{metal}")
            
        with c_frac:
            # Dynamically sets default based on however many metals are selected
            default_frac = 1.0 / len(selected_metals) 
            frac = st.number_input(f"Fraction (x)", value=default_frac, format="%.3f", key=f"frac_{metal}")
            total_fraction += frac
            
        metal_data[metal] = {"MW": mw, "Fraction": frac}

    st.write(f"**Total Stoichiometric Fraction:** {total_fraction:.3f}")

    # Slightly widened tolerance (0.01) to account for fractions like 1/3 (0.333 + 0.333 + 0.333 = 0.999)
    if abs(total_fraction - 1.0) > 0.01:
        st.error("The sum of stoichiometric fractions must equal 1.0!")
    else:
        st.success("Fractions sum to 1.0. Ready to calculate.")

    st.divider()

    # --- 3. RESULTS CALCULATION ---
    if st.button("Calculate Recipe", type="primary", use_container_width=True):
        st.header("3. Required Masses")
        
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.subheader("Metals")
            for metal, data in metal_data.items():
                mass = target_mols * data["Fraction"] * data["MW"]
                st.info(f"**{metal}:** {mass:.4f} g")
                
        with res_col2:
            st.subheader("Additives")
            acry_mass = (target_mols * acry_ratio) * ACRYLAMIDE_MW
            citric_mass = (target_mols * citric_ratio) * CITRIC_ACID_MONOHYDRATE_MW
            
            st.success(f"**Acrylamide:** {acry_mass:.4f} g")
            st.success(f"**Citric Acid Monohydrate:** {citric_mass:.4f} g")