import streamlit as st

st.set_page_config(page_title="HEO Recipe Calculator", layout="wide")

st.title("HEO Recipe Calculator")
AVAILABLE_METALS = {
    "Nickel": 290.79,      
    "Lanthanum": 433.01,   
    "Cobalt": 291.03,      
    "Chromium": 400.15,    
    "Magnesium": 256.41,   
    "Calcium": 236.15,     
    "Copper": 241.60,      
    "Manganese": 251.01,   
    "Cerium": 434.22,      
    "Iron": 404.00,        
    "Yttrium": 364.99,     
    "Praseodymium": 435.01,
    "Zinc": 297.49,        
    "Neodymium": 438.35,   
    "Barium": 261.34,      
    "Strontium": 211.63    
}
ACRYLAMIDE_MW = 71.08
CITRIC_ACID_MONOHYDRATE_MW = 210.14
# --- TOP LEVEL INPUTS ---
col1, col2, col3 = st.columns(3)
with col1:
    target_mols = st.number_input("Target Total Moles of HEO", value=0.1, format="%.2f")
with col2:
    acry_ratio = st.number_input("Acrylamide : Total Metal Ratio", value=9.0, format="%.0f", step=1.0)
with col3:
    citric_ratio = st.number_input("Citric Acid : Total Metal Ratio", value=3.0, format="%.0f", step=1.0)

st.divider()
# --- PRECURSOR SELECTION ---
st.header("1. Select Metals")
st.write("Check exactly 5 metals to synthesize:")

selected_metals = []
cols = st.columns(4) 

for index, metal in enumerate(AVAILABLE_METALS.keys()):
    with cols[index % 4]:
        if st.checkbox(metal, key=f"check_{index}"):
            selected_metals.append(metal)

if len(selected_metals) != 5:
    st.warning(f"You have selected {len(selected_metals)} metals. Please select EXACTLY 5 metals to continue.")
    st.stop()

st.header("2. Define Stoichiometry")
st.markdown("Ensure the sum of your stoichiometric fractions ($x$) equals exactly **1.0**.")

metal_data = {}
total_fraction = 0.0

for metal in selected_metals:
    c_name, c_mw, c_frac = st.columns([2, 1, 1])
    
    with c_name:
        st.markdown(f"**{metal}**")
        
    with c_mw:
        default_mw = AVAILABLE_METALS[metal]
        mw = st.number_input(f"MW (g/mol)", value=default_mw, format="%.2f", key=f"mw_{metal}")
        
    with c_frac:
        default_frac = 1.0 / 5.0 
        frac = st.number_input(f"Fraction (x)", value=default_frac, format="%.3f", key=f"frac_{metal}")
        total_fraction += frac
        
    metal_data[metal] = {"MW": mw, "Fraction": frac}

st.write(f"**Total Stoichiometric Fraction:** {total_fraction:.3f}")

if abs(total_fraction - 1.0) > 0.005:
    st.error("The sum of stoichiometric fractions must equal 1.0!")
else:
    st.success("Fractions sum to 1.0. Ready to calculate.")

st.divider()

# --- RESULTS CALCULATION ---
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