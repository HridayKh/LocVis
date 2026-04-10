import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import PowerNorm
import streamlit as st

st.set_page_config(page_title="LocVis - Location Visualizer", layout="wide")
st.title("📍 LocVis - Location Visualizer")

# --- 1. Initialize Session State ---
# This keeps track of which "tab" or view is active
if "view" not in st.session_state:
	st.session_state.view = "preview"  # default view

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
	# Drops and renames as per your logic
	cols_to_drop = ["time", "seconds_elapsed", "bearingAccuracy", "bearing", "altitude", "verticalAccuracy"]
	data = data.drop(columns=[c for c in cols_to_drop if c in data.columns])
	data = data.rename(columns={
	    "latitude": "lat",
	    "longitude": "long",
	    "speed": "speed",
	    "speedAccuracy": "speedAcc",
	    "horizontalAccuracy": "horiAcc"
	})
	data["speed"] = data["speed"] * 3.6
	data = data.dropna(subset=['speed'])

	start_lat, start_long = data['lat'].iloc[0], data['long'].iloc[0]
	data['x_meters'] = (data['long'] - start_long) * 94800
	data['y_meters'] = (data['lat'] - start_lat) * 110852
	return data


def show_stats(data: pd.DataFrame):
	st.subheader("📊 Trip Statistics")

	# Speed Metrics
	col1, col2, col3, col4 = st.columns(4)
	col1.metric("Avg Speed", f"{data['speed'].mean():.1f} km/h")
	col2.metric("Max Speed", f"{data['speed'].max():.1f} km/h")
	col3.metric("Median Speed", f"{data['speed'].median():.1f} km/h")
	col4.metric("Min (>0) Speed", f"{data['speed'][data['speed'] > 0].min():.1f} km/h")

	# Accuracy Metrics in an Expander to save space
	with st.expander("View Accuracy Details"):
		c1, c2 = st.columns(2)
		with c1:
			st.write("**Horizontal Accuracy (m)**")
			st.dataframe(data['horiAcc'].describe().to_frame().T)
		with c2:
			st.write("**Speed Accuracy (km/h)**")
			st.dataframe(data['speedAcc'].describe().to_frame().T)


def show_plot(data: pd.DataFrame):
	st.subheader("🗺️ Movement Path")
	fig, ax = plt.subplots(figsize=(10, 7))

	plt.plot(data['x_meters'], data['y_meters'], color='green', linewidth=1, zorder=1, alpha=0.5)
	sns.scatterplot(data=data, x='x_meters', y='y_meters', hue='speed', hue_norm=PowerNorm(gamma=2), s=50, edgecolor=None, zorder=2)

	plt.ylabel("North/South (m)")
	plt.xlabel("East/West (m)")
	plt.grid(True, linestyle='--', alpha=0.3)
	plt.axis('equal')
	st.pyplot(fig)


# --- 2. Main Logic ---
if uploaded_file:
	raw_data = pd.read_csv(uploaded_file)
	data = clean_data(raw_data)

	# Navigation Buttons
	col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])

	if col_nav1.button("📈 View Stats"):
		st.session_state.view = "stats"

	if col_nav2.button("🗺️ View Plot"):
		st.session_state.view = "plot"

	st.divider()

	# --- 3. Conditional Rendering based on Session State ---
	if st.session_state.view == "stats":
		show_stats(data)
	elif st.session_state.view == "plot":
		show_plot(data)
	else:
		st.write("### Data Preview", data.head())
		st.info("Click the buttons above to toggle between Statistics and the Map Plot.")
else:
	st.info("Please upload a CSV file to get started.")
	st.warning("Upload location data recorded using sensor logger app!")
