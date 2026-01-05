import streamlit as st
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="حاسبة الفروقات", layout="wide")
st.title("حاسبة الفروقات الوظيفية")

col1, col2 = st.columns(2)
with col1:
    old_sal = st.number_input("الراتب الاسمي القديم", value=0)
    sal1 = st.number_input("راتب العلاوة 1", value=0)
    sal2 = st.number_input("راتب العلاوة 2", value=0)
    sal3 = st.number_input("راتب العلاوة 3", value=0)
    sal_p = st.number_input("الراتب بعد الترفيع", value=0)
with col2:
    d1 = st.date_input("تاريخ العلاوة 1", value=None)
    d2 = st.date_input("تاريخ العلاوة 2", value=None)
    d3 = st.date_input("تاريخ العلاوة 3", value=None)
    dp = st.date_input("تاريخ الترفيع", value=None)
    de = st.date_input("تاريخ نهاية الفترة", value=None)

degree = st.selectbox("التحصيل العلمي", ["بكالوريوس", "ماجستير", "دكتوراه", "غير ذلك"])

def get_m(s, e):
    if s and e and s < e:
        diff = relativedelta(e, s)
        return diff.years * 12 + diff.months
    return 0

m1, m2, m3, mp = get_m(d1, d2), get_m(d2, d3), get_m(d3, dp), get_m(dp, de)
f1, f2, f3, fp = (sal1-old_sal)*m1, (sal2-sal1)*m2, (sal3-sal2)*m3, (sal_p-sal3)*mp
total = f1 + f2 + f3 + fp
ratio = {"دكتوراه":1.0, "ماجستير":0.75, "بكالوريوس":0.50, "غير ذلك":0.0}.get(degree, 0)

st.divider()
st.subheader(f"المستحق النهائي: {total * ratio:,.0f}")
