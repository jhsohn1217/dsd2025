import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="인터랙티브 파이차트", layout="centered")
st.title("🧁 인터랙티브 파이차트")
st.caption("엑셀 파일을 업로드하면 시트를 선택하고 파이차트를 그립니다.")

# 파일 업로더
uploaded_file = st.file_uploader("엑셀 파일 업로드 (.xlsx, .xls)", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("예: '파이차트' 시트에 `제품명`, `1분기 매출` 열이 있는 엑셀을 업로드하세요.")
    st.stop()

# 엑셀 파일 열기
try:
    xls = pd.ExcelFile(uploaded_file)
except Exception as e:
    st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 시트 선택 (기본: '파이차트'가 있으면 그것으로)
default_sheet = "파이차트" if "파이차트" in xls.sheet_names else xls.sheet_names[0]
sheet_name = st.selectbox("시트 선택", xls.sheet_names, index=xls.sheet_names.index(default_sheet))

# 데이터프레임 로드
try:
    df = xls.parse(sheet_name)
except Exception as e:
    st.error(f"시트를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 열 선택 (기본값은 '제품명' / '1분기 매출'이 있으면 자동 선택)
cols = list(df.columns)
if len(cols) < 2:
    st.error("파이차트를 그리려면 최소 두 개의 열(라벨, 값)이 필요합니다.")
    st.stop()

name_col_default = cols.index("제품명") if "제품명" in cols else 0
value_col_default = cols.index("1분기 매출") if "1분기 매출" in cols else (1 if len(cols) > 1 else 0)

name_col = st.selectbox("라벨(이름) 열 선택", cols, index=name_col_default)
value_col = st.selectbox("값(수치) 열 선택", cols, index=value_col_default)

# 숫자형 변환 시도
try:
    values = pd.to_numeric(df[value_col], errors="coerce")
    if values.isna().all():
        st.error(f"선택한 값 열 `{value_col}` 에 숫자가 없습니다. 숫자형 열을 선택하세요.")
        st.stop()
    df_plot = pd.DataFrame({name_col: df[name_col], value_col: values}).dropna()
except Exception as e:
    st.error(f"값 열 처리 중 오류가 발생했습니다: {e}")
    st.stop()

# 파이차트 그리기
fig = px.pie(
    df_plot,
    names=name_col,
    values=value_col,
    title=f"{sheet_name} · {name_col}별 비율",
    hole=0.3,  # 도넛 형태
)
fig.update_traces(
    textinfo="percent+label",
    hovertemplate="%{label}: %{value}<br>(%{percent})"
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("원본 데이터 보기"):
    st.dataframe(df, use_container_width=True)
