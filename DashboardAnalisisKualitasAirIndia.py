from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st


# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================
st.set_page_config(
    page_title="Dashboard Kualitas Air India",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATHS = [
    APP_DIR / "data" / "IndiaAffectedWaterQualityAreas.csv",
    APP_DIR / "IndiaAffectedWaterQualityAreas.csv",
]

REQUIRED_COLUMNS = [
    "State Name",
    "District Name",
    "Block Name",
    "Panchayat Name",
    "Village Name",
    "Habitation Name",
    "Quality Parameter",
    "Year",
]

COUNT_LABEL = "Jumlah Lokasi Terdampak"

COLUMN_RENAME_ID = {
    "State Standardized": "Negara Bagian",
    "State Name": "Negara Bagian Asli",
    "District Clean": "Distrik",
    "District Code": "Kode Distrik",
    "Block Name": "Blok",
    "Panchayat Name": "Panchayat",
    "Village Name": "Desa",
    "Habitation Name": "Permukiman",
    "Quality Parameter": "Parameter Kualitas Air",
    "Year Number": "Tahun",
    "Date": "Tanggal",
    "State - District": "Negara Bagian - Distrik",
}

PARAMETER_ORDER = ["IRON", "SALINITY", "FLUORIDE", "ARSENIC", "NITRATE"]

DATA_SOURCE_URL = "https://www.kaggle.com/datasets/venkatramakrishnan/india-water-quality-data/data"


# =============================================================================
# TAMPILAN CSS
# =============================================================================
st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1.35rem;
            padding-bottom: 2.5rem;
        }
        .hero-card {
            padding: 1.4rem 1.55rem;
            border-radius: 1.1rem;
            background: linear-gradient(135deg, #ECFDF5 0%, #EFF6FF 52%, #FFF7ED 100%);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2.05rem;
            line-height: 1.15;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.35rem;
        }
        .hero-subtitle {
            font-size: 1rem;
            color: #475569;
            margin-bottom: 0rem;
        }
        .section-note {
            padding: 0.85rem 1rem;
            border-radius: 0.9rem;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            color: #334155;
            font-size: 0.95rem;
            margin-bottom: 0.75rem;
        }
        .small-note {
            color: #64748B;
            font-size: 0.9rem;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 0.85rem 1rem;
            border-radius: 1rem;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        }
        .footer-copyright {
            margin-top: 0.75rem;
            padding: 0.9rem 1rem;
            border-top: 1px solid #E2E8F0;
            color: #0F172A;
            font-size: 0.95rem;
            font-weight: 600;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# FUNGSI BANTU
# =============================================================================
def find_default_data_path() -> Path | None:
    for path in DEFAULT_DATA_PATHS:
        if path.exists():
            return path
    return None


@st.cache_data(show_spinner=False)
def load_csv_from_path(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="latin1")


@st.cache_data(show_spinner=False)
def load_csv_from_upload(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file, encoding="latin1")


def normalize_text(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )


@st.cache_data(show_spinner=False)
def clean_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Membersihkan data dan menyiapkan kolom untuk dashboard."""
    df = df_raw.copy()

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing_columns}")

    before_rows = len(df)

    for col in REQUIRED_COLUMNS:
        df[col] = normalize_text(df[col])

    df["Date"] = pd.to_datetime(df["Year"], dayfirst=True, errors="coerce")
    df["Year Number"] = df["Date"].dt.year.astype("Int64")
    df["Month Number"] = df["Date"].dt.month.astype("Int64")

    state_standard_map = {
        "CHATTISGARH": "CHHATTISGARH",
        "ORISSA": "ODISHA",
    }
    df["State Standardized"] = df["State Name"].replace(state_standard_map)

    district_extract = df["District Name"].str.extract(
        r"^(?P<DistrictClean>.*?)(?:\((?P<DistrictCode>[^)]*)\))?$"
    )
    df["District Clean"] = district_extract["DistrictClean"].fillna(df["District Name"]).str.strip()
    df["District Code"] = district_extract["DistrictCode"].fillna("").str.strip()

    df = df.drop_duplicates().reset_index(drop=True)
    after_rows = len(df)

    df["State - District"] = df["State Standardized"] + " | " + df["District Clean"]

    profile = {
        "before_rows": before_rows,
        "after_rows": after_rows,
        "duplicate_removed": before_rows - after_rows,
        "invalid_date": int(df["Date"].isna().sum()),
    }
    return df, profile


def format_number(value: int | float) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}".replace(",", ".")


def pct(part: int | float, total: int | float) -> float:
    if total == 0 or pd.isna(total):
        return 0.0
    return float(part / total * 100)


def title_case(value: str) -> str:
    return str(value).title()


def build_multiselect(label: str, options: Iterable[str], help_text: str | None = None) -> list[str]:
    options = sorted([str(opt) for opt in options if pd.notna(opt)])
    return st.sidebar.multiselect(label, options=options, default=[], help=help_text)


def apply_filters(
    df: pd.DataFrame,
    selected_states: list[str],
    selected_districts: list[str],
    selected_parameters: list[str],
    selected_years: list[int],
) -> pd.DataFrame:
    filtered = df.copy()
    if selected_states:
        filtered = filtered[filtered["State Standardized"].isin(selected_states)]
    if selected_districts:
        filtered = filtered[filtered["District Clean"].isin(selected_districts)]
    if selected_parameters:
        filtered = filtered[filtered["Quality Parameter"].isin(selected_parameters)]
    if selected_years:
        filtered = filtered[filtered["Year Number"].isin(selected_years)]
    return filtered


def make_group_count(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=group_cols + [COUNT_LABEL])
    return df.groupby(group_cols, dropna=False).size().reset_index(name=COUNT_LABEL)


def rename_for_display(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={key: value for key, value in COLUMN_RENAME_ID.items() if key in df.columns})


def download_button_for_df(df: pd.DataFrame, label: str, filename: str) -> None:
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def show_bar_chart(source: pd.DataFrame, category_col: str, value_col: str = COUNT_LABEL) -> None:
    if source.empty:
        st.info("Data belum tersedia untuk pilihan filter saat ini.")
        return
    chart_source = source[[category_col, value_col]].copy()
    chart_source[category_col] = chart_source[category_col].map(title_case)
    chart_source = chart_source.set_index(category_col)
    st.bar_chart(chart_source, height=380)


def show_line_chart(source: pd.DataFrame, index_col: str, category_col: str, value_col: str = COUNT_LABEL) -> None:
    if source.empty:
        st.info("Data tren belum tersedia untuk pilihan filter saat ini.")
        return
    pivot = source.pivot_table(
        index=index_col,
        columns=category_col,
        values=value_col,
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    # Tahun dijadikan teks agar sumbu grafik tampil sebagai 2009, 2010, 2011, 2012
    # dan tidak terbaca sebagai angka ribuan seperti 2,009 atau 2,010.
    if index_col.lower() == "tahun":
        pivot.index = [str(int(year)) if pd.notna(year) else "-" for year in pivot.index]

    st.line_chart(pivot, height=420)


# =============================================================================
# HEADER DAN DATA
# =============================================================================
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">💧 Dashboard Sebaran Parameter Kualitas Air</div>
        <p class="hero-subtitle">
            Dashboard untuk melihat wilayah yang tercatat terdampak berdasarkan negara bagian,
            distrik, parameter kualitas air, dan tahun pengamatan.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("⚙️ Filter Dashboard")
    st.caption("Kosongkan pilihan untuk menampilkan seluruh data.")

    default_path = find_default_data_path()
    uploaded_file = st.file_uploader(
        "Unggah CSV lain bila ingin mengganti dataset",
        type=["csv"],
        help="Opsional. Bila tidak diunggah, dashboard memakai file CSV di folder data atau folder yang sama dengan app.py.",
    )

    st.info(
        "Dataset bawaan bersumber dari Kaggle: India Water Quality Data. "
        "Apabila mengunggah data lain, pastikan struktur kolomnya sama."
    )
    st.markdown(f"Sumber data: [Kaggle - India Water Quality Data]({DATA_SOURCE_URL})")

try:
    if uploaded_file is not None:
        raw_df = load_csv_from_upload(uploaded_file)
        data_source_label = "CSV yang diunggah"
    elif default_path is not None:
        raw_df = load_csv_from_path(str(default_path))
        try:
            data_source_label = str(default_path.relative_to(APP_DIR))
        except ValueError:
            data_source_label = str(default_path)
    else:
        st.error(
            "Dataset tidak ditemukan. Letakkan file `IndiaAffectedWaterQualityAreas.csv` "
            "di folder yang sama dengan `app.py`, atau masukkan ke folder `data/`, "
            "atau unggah CSV melalui sidebar."
        )
        st.stop()

    df, profile = clean_data(raw_df)
except Exception as exc:
    st.error(f"Gagal membaca atau menyiapkan dataset: {exc}")
    st.stop()


# =============================================================================
# FILTER SIDEBAR
# =============================================================================
with st.sidebar:
    st.divider()

    selected_states = build_multiselect(
        "Negara Bagian",
        df["State Standardized"].dropna().unique(),
        "Pilih satu atau beberapa negara bagian.",
    )

    district_base = df[df["State Standardized"].isin(selected_states)] if selected_states else df
    selected_districts = build_multiselect(
        "Distrik",
        district_base["District Clean"].dropna().unique(),
        "Daftar distrik mengikuti pilihan negara bagian.",
    )

    selected_parameters = build_multiselect(
        "Parameter Kualitas Air",
        df["Quality Parameter"].dropna().unique(),
        "Contoh: Iron, Salinity, Fluoride, Arsenic, Nitrate.",
    )

    year_options = sorted([int(y) for y in df["Year Number"].dropna().unique()])
    selected_years = st.multiselect("Tahun", options=year_options, default=[])

    top_n = st.slider("Jumlah peringkat yang ditampilkan", min_value=5, max_value=30, value=10, step=5)

filtered_df = apply_filters(df, selected_states, selected_districts, selected_parameters, selected_years)

if filtered_df.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Kurangi filter untuk melihat hasil.")
    st.stop()


# =============================================================================
# KPI UTAMA
# =============================================================================
total_affected_locations = len(filtered_df)
total_states = filtered_df["State Standardized"].nunique()
total_districts = filtered_df["District Clean"].nunique()
total_villages = filtered_df["Village Name"].nunique()
total_habitations = filtered_df["Habitation Name"].nunique()
parameter_counts = filtered_df["Quality Parameter"].value_counts()
dominant_parameter = parameter_counts.idxmax() if not parameter_counts.empty else "-"
dominant_parameter_count = int(parameter_counts.max()) if not parameter_counts.empty else 0
dominant_parameter_share = pct(dominant_parameter_count, total_affected_locations)

cols = st.columns(5)
cols[0].metric("Jumlah Lokasi Terdampak", format_number(total_affected_locations))
cols[1].metric("Negara Bagian", format_number(total_states))
cols[2].metric("Distrik", format_number(total_districts))
cols[3].metric("Desa", format_number(total_villages))
cols[4].metric("Parameter Terbanyak", dominant_parameter.title(), f"{dominant_parameter_share:.1f}%")

# =============================================================================
# TAB DASHBOARD
# =============================================================================
tab_overview, tab_region, tab_parameter, tab_insight, tab_data = st.tabs(
    [
        "🏠 Ringkasan Nasional",
        "🗺️ Analisis Wilayah",
        "🧪 Parameter Kualitas Air",
        "💡 Ringkasan Otomatis",
        "📄 Tabel & Unduh Data",
    ]
)


with tab_overview:
    st.subheader("Ringkasan Sebaran Parameter Kualitas Air")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### Jumlah Lokasi Terdampak per Parameter Kualitas Air")
        national_parameter = make_group_count(filtered_df, ["Quality Parameter"])
        national_parameter = national_parameter.sort_values(COUNT_LABEL, ascending=False)
        display_parameter = national_parameter.rename(columns={"Quality Parameter": "Parameter Kualitas Air"})
        show_bar_chart(display_parameter, "Parameter Kualitas Air")
        st.dataframe(display_parameter, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown(f"#### {top_n} Negara Bagian dengan Lokasi Terdampak Terbanyak")
        state_rank = make_group_count(filtered_df, ["State Standardized"])
        state_rank = state_rank.sort_values(COUNT_LABEL, ascending=False).head(top_n)
        display_state = state_rank.rename(columns={"State Standardized": "Negara Bagian"})
        show_bar_chart(display_state, "Negara Bagian")
        st.dataframe(display_state, use_container_width=True, hide_index=True)

    st.markdown("#### Tren Jumlah Lokasi Terdampak per Tahun dan Parameter Kualitas Air")
    trend = make_group_count(filtered_df.dropna(subset=["Year Number"]), ["Year Number", "Quality Parameter"])
    trend = trend.rename(columns={"Year Number": "Tahun", "Quality Parameter": "Parameter Kualitas Air"})
    show_line_chart(trend, "Tahun", "Parameter Kualitas Air")


with tab_region:
    st.subheader("Analisis Wilayah")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### {top_n} Distrik dengan Lokasi Terdampak Terbanyak")
        district_rank = make_group_count(filtered_df, ["State - District"])
        district_rank = district_rank.sort_values(COUNT_LABEL, ascending=False).head(top_n)
        display_district = district_rank.rename(columns={"State - District": "Negara Bagian - Distrik"})
        show_bar_chart(display_district, "Negara Bagian - Distrik")
        st.dataframe(display_district, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown(f"#### Komposisi Parameter pada {top_n} Negara Bagian Teratas")
        state_parameter = make_group_count(filtered_df, ["State Standardized", "Quality Parameter"])
        top_states = (
            state_parameter.groupby("State Standardized")[COUNT_LABEL]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        state_parameter_top = state_parameter[state_parameter["State Standardized"].isin(top_states)]
        pivot_state_parameter = state_parameter_top.pivot_table(
            index="State Standardized",
            columns="Quality Parameter",
            values=COUNT_LABEL,
            aggfunc="sum",
            fill_value=0,
        )
        pivot_state_parameter.index = pivot_state_parameter.index.map(title_case)
        ordered_columns = [col for col in PARAMETER_ORDER if col in pivot_state_parameter.columns]
        pivot_state_parameter = pivot_state_parameter[ordered_columns]
        st.bar_chart(pivot_state_parameter, height=430)
        st.dataframe(pivot_state_parameter.reset_index().rename(columns={"State Standardized": "Negara Bagian"}), use_container_width=True, hide_index=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown(f"#### {top_n} Desa dengan Lokasi Terdampak Terbanyak")
        village_rank = make_group_count(filtered_df, ["Village Name"])
        village_rank = village_rank.sort_values(COUNT_LABEL, ascending=False).head(top_n)
        display_village = village_rank.rename(columns={"Village Name": "Desa"})
        show_bar_chart(display_village, "Desa")
        st.dataframe(display_village, use_container_width=True, hide_index=True)

    with col_d:
        st.markdown(f"#### {top_n} Permukiman dengan Lokasi Terdampak Terbanyak")
        habitation_rank = make_group_count(filtered_df, ["Habitation Name"])
        habitation_rank = habitation_rank.sort_values(COUNT_LABEL, ascending=False).head(top_n)
        display_habitation = habitation_rank.rename(columns={"Habitation Name": "Permukiman"})
        show_bar_chart(display_habitation, "Permukiman")
        st.dataframe(display_habitation, use_container_width=True, hide_index=True)


with tab_parameter:
    st.subheader("Pendalaman Parameter Kualitas Air")

    col_e, col_f = st.columns([1, 1])

    with col_e:
        st.markdown("#### Persentase Lokasi Terdampak per Parameter")
        parameter_share = make_group_count(filtered_df, ["Quality Parameter"])
        parameter_share["Persentase (%)"] = parameter_share[COUNT_LABEL] / parameter_share[COUNT_LABEL].sum() * 100
        parameter_share = parameter_share.sort_values(COUNT_LABEL, ascending=False)
        display_share = parameter_share.rename(columns={"Quality Parameter": "Parameter Kualitas Air"})
        st.bar_chart(display_share.set_index("Parameter Kualitas Air")[["Persentase (%)"]], height=350)
        st.dataframe(
            display_share.assign(**{"Persentase (%)": display_share["Persentase (%)"].round(2)}),
            use_container_width=True,
            hide_index=True,
        )

    with col_f:
        st.markdown("#### Negara Bagian Utama pada Tiap Parameter")
        parameter_state = make_group_count(filtered_df, ["Quality Parameter", "State Standardized"])
        if not parameter_state.empty:
            main_state_per_parameter = (
                parameter_state.sort_values(["Quality Parameter", COUNT_LABEL], ascending=[True, False])
                .groupby("Quality Parameter")
                .head(1)
                .sort_values(COUNT_LABEL, ascending=False)
            )
            display_main = main_state_per_parameter.rename(
                columns={
                    "Quality Parameter": "Parameter Kualitas Air",
                    "State Standardized": "Negara Bagian",
                }
            )
            st.bar_chart(display_main.set_index("Parameter Kualitas Air")[[COUNT_LABEL]], height=350)
            st.dataframe(display_main, use_container_width=True, hide_index=True)
        else:
            st.info("Data belum tersedia untuk pilihan filter saat ini.")

    st.markdown(f"#### Peta Warna {top_n} Negara Bagian x Parameter Kualitas Air")
    peta_warna_source = make_group_count(filtered_df, ["State Standardized", "Quality Parameter"])
    if not peta_warna_source.empty:
        top_peta_states = (
            peta_warna_source.groupby("State Standardized")[COUNT_LABEL]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        peta_warna_source = peta_warna_source[peta_warna_source["State Standardized"].isin(top_peta_states)]
        peta_warna = peta_warna_source.pivot_table(
            index="State Standardized",
            columns="Quality Parameter",
            values=COUNT_LABEL,
            aggfunc="sum",
            fill_value=0,
        )
        ordered_cols = [col for col in PARAMETER_ORDER if col in peta_warna.columns]
        peta_warna = peta_warna[ordered_cols]
        peta_warna.index = peta_warna.index.map(title_case)
        st.dataframe(peta_warna, use_container_width=True)
        st.caption("Angka pada tabel menunjukkan jumlah lokasi terdampak pada kombinasi negara bagian dan parameter kualitas air.")

    st.markdown("#### Tabel Ringkasan Parameter")
    parameter_table = make_group_count(
        filtered_df,
        ["State Standardized", "District Clean", "Quality Parameter", "Year Number"],
    ).sort_values(COUNT_LABEL, ascending=False)
    parameter_table_display = rename_for_display(parameter_table)
    st.dataframe(parameter_table_display, use_container_width=True, hide_index=True)


with tab_insight:
    st.subheader("Ringkasan Otomatis Berdasarkan Filter Aktif")

    state_counts = filtered_df["State Standardized"].value_counts()
    district_counts = filtered_df["State - District"].value_counts()
    year_counts = filtered_df["Year Number"].value_counts().sort_index()

    top_state = state_counts.index[0]
    top_state_count = int(state_counts.iloc[0])
    top_district = district_counts.index[0]
    top_district_count = int(district_counts.iloc[0])

    if not year_counts.empty:
        peak_year = int(year_counts.idxmax())
        peak_year_count = int(year_counts.max())
        first_year = int(year_counts.index.min())
        last_year = int(year_counts.index.max())
    else:
        peak_year = first_year = last_year = None
        peak_year_count = 0

    parameter_rank = make_group_count(filtered_df, ["Quality Parameter"]).sort_values(COUNT_LABEL, ascending=False)
    second_parameter = parameter_rank.iloc[1] if len(parameter_rank) > 1 else None

    col_i1, col_i2, col_i3 = st.columns(3)
    col_i1.metric("Negara Bagian Tertinggi", top_state.title(), f"{pct(top_state_count, total_affected_locations):.1f}%")
    col_i2.metric("Distrik Tertinggi", top_district.title(), f"{format_number(top_district_count)} lokasi")
    col_i3.metric("Tahun Tertinggi", str(peak_year) if peak_year else "-", f"{format_number(peak_year_count)} lokasi")

    st.markdown("#### Ringkasan untuk Pimpinan")
    insight_lines = [
        f"Data hasil filter mencakup **{format_number(total_affected_locations)} lokasi terdampak** yang tersebar pada **{format_number(total_states)} negara bagian** dan **{format_number(total_districts)} distrik**.",
        f"Parameter kualitas air yang paling banyak tercatat adalah **{dominant_parameter.title()}** dengan **{format_number(dominant_parameter_count)} lokasi terdampak**, atau sekitar **{dominant_parameter_share:.1f}%** dari data yang ditampilkan.",
        f"Negara bagian dengan jumlah lokasi terdampak tertinggi adalah **{top_state.title()}** dengan **{format_number(top_state_count)} lokasi**, atau sekitar **{pct(top_state_count, total_affected_locations):.1f}%** dari data yang ditampilkan.",
        f"Distrik yang paling menonjol adalah **{top_district.title()}** dengan **{format_number(top_district_count)} lokasi terdampak**.",
    ]

    if peak_year is not None:
        insight_lines.append(
            f"Berdasarkan dimensi waktu, tahun dengan jumlah lokasi terdampak terbanyak adalah **{peak_year}** sebanyak **{format_number(peak_year_count)} lokasi**. Rentang tahun pada filter aktif adalah **{first_year}–{last_year}**."
        )

    if second_parameter is not None:
        insight_lines.append(
            f"Parameter terbanyak kedua adalah **{str(second_parameter['Quality Parameter']).title()}** dengan **{format_number(second_parameter[COUNT_LABEL])} lokasi terdampak**."
        )

    for line in insight_lines:
        st.markdown(f"- {line}")

    st.markdown("#### Arahan Pemanfaatan Dashboard")
    st.markdown(
        """
        - Gunakan filter negara bagian dan distrik untuk melihat wilayah yang memerlukan perhatian awal.
        - Gunakan tab parameter kualitas air untuk melihat parameter yang paling sering tercatat pada wilayah terdampak.
        - Gunakan tabel dan tombol unduh untuk menyiapkan bahan paparan atau analisis lanjutan.
        - Perlu ditekankan bahwa dashboard ini menunjukkan jumlah lokasi yang tercatat terdampak, bukan kadar kimia air atau status hukum pencemaran.
        """
    )


with tab_data:
    st.subheader("Tabel Data dan Unduh")

    display_cols = [
        "State Standardized",
        "State Name",
        "District Clean",
        "District Code",
        "Block Name",
        "Panchayat Name",
        "Village Name",
        "Habitation Name",
        "Quality Parameter",
        "Date",
        "Year Number",
    ]
    display_cols = [col for col in display_cols if col in filtered_df.columns]

    st.markdown("#### Data Hasil Filter")
    display_data = rename_for_display(filtered_df[display_cols].head(5000))
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    st.caption("Tampilan tabel dibatasi 5.000 baris pertama agar dashboard tetap ringan. File yang diunduh tetap berisi seluruh data sesuai filter.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        download_button_for_df(
            rename_for_display(filtered_df[display_cols]),
            "⬇️ Unduh data hasil filter",
            "data_kualitas_air_hasil_filter.csv",
        )

    aggregate_download = make_group_count(
        filtered_df,
        ["State Standardized", "District Clean", "Quality Parameter", "Year Number"],
    ).sort_values(COUNT_LABEL, ascending=False)
    with col_d2:
        download_button_for_df(
            rename_for_display(aggregate_download),
            "⬇️ Unduh tabel ringkasan",
            "ringkasan_kualitas_air.csv",
        )

    st.markdown("#### Profil Dataset")
    profile_table = pd.DataFrame(
        {
            "Keterangan": [
                "Jumlah data awal",
                "Jumlah data setelah pembersihan",
                "Data duplikat yang dihapus",
                "Tanggal tidak valid",
                "Jumlah negara bagian",
                "Jumlah distrik",
                "Jumlah parameter kualitas air",
                "Tahun awal",
                "Tahun akhir",
            ],
            "Nilai": [
                format_number(profile["before_rows"]),
                format_number(profile["after_rows"]),
                format_number(profile["duplicate_removed"]),
                format_number(profile["invalid_date"]),
                format_number(df["State Standardized"].nunique()),
                format_number(df["District Clean"].nunique()),
                format_number(df["Quality Parameter"].nunique()),
                int(df["Year Number"].min()) if not df["Year Number"].isna().all() else "-",
                int(df["Year Number"].max()) if not df["Year Number"].isna().all() else "-",
            ],
        }
    )
    st.dataframe(profile_table, use_container_width=True, hide_index=True)


st.markdown("---")
st.markdown(
    f"""
    <div class="section-note">
        <b>Sumber data aktif:</b> {data_source_label} &nbsp;|&nbsp;
        <b>Jumlah data awal:</b> {format_number(profile['before_rows'])} &nbsp;|&nbsp;
        <b>Jumlah data setelah pembersihan:</b> {format_number(profile['after_rows'])} &nbsp;|&nbsp;
        <b>Data duplikat yang dihapus:</b> {format_number(profile['duplicate_removed'])} &nbsp;|&nbsp;
        <b>Tanggal tidak valid:</b> {format_number(profile['invalid_date'])}.
        <br>
        <span class="small-note">
            Catatan: jumlah lokasi terdampak menunjukkan banyaknya entri lokasi/wilayah yang tercatat dalam dataset,
            bukan ukuran kadar kimia atau tingkat bahaya secara langsung.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Catatan: dashboard ini menghitung jumlah lokasi/wilayah yang tercatat terdampak dalam dataset. "
    "Interpretasi kualitas air tetap perlu mempertimbangkan metadata dan definisi dari sumber data. "
    f"Sumber dataset bawaan: {DATA_SOURCE_URL}"
)

# Footer copyright ditampilkan paling bawah dashboard.
st.markdown(
    """
    <div class="footer-copyright">
        © 2026 Raihan Ferdyanza • Pusdatin KLH/BPLH
    </div>
    """,
    unsafe_allow_html=True,
)
