import streamlit as st
from PIL import Image
import c2pa

st.set_page_config(page_title="AI 이미지 판별기", page_icon="🔍")

st.title("🛡️ AI 이미지 생성 판별 프로그램")
st.write("📌 **판정 기준:** C2PA 서명, PNG 프롬프트 흔적, EXIF 카메라 정보를 모두 복합적으로 검사하여 최종 판정을 내립니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader("분석할 이미지 파일을 선택하세요 (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_column_width=True)
    st.divider()
    
    st.subheader("📊 상세 검사 내역 및 판정 결과")
    
    is_ai = False
    ai_reasons = []
    
    # 1. C2PA 메타데이터(디지털 서명) 검사
    c2pa_detected = False
    try:
        file_bytes = uploaded_file.getvalue()
        reader = c2pa.Reader.from_bytes(uploaded_file.type, file_bytes)
        json_result = reader.json()
        if json_result:
            c2pa_detected = True
            is_ai = True
            ai_reasons.append("C2PA 디지털 서명(콘텐츠 자격 증명)이 확인되었습니다.")
    except Exception:
        pass
        
    # 2. PNG 텍스트 청크(parameters) 검사 (스테이블 디퓨전 등)
    png_prompt_detected = False
    if uploaded_file.type == "image/png":
        meta = image.info
        if "parameters" in meta:
            png_prompt_detected = True
            is_ai = True
            ai_reasons.append("PNG 내부 파일 데이터에서 AI 생성 프롬프트(parameters) 설정값이 발견되었습니다.")
            
    # 3. EXIF 카메라 정보 검사
    exif_data = image.getexif()
    has_exif = bool(exif_data)
    
    if not has_exif:
        is_ai = True
        ai_reasons.append("실제 카메라 촬영 정보(EXIF)가 존재하지 않습니다.")

    # 상세 검사 결과 항목별 출력
    if c2pa_detected:
        st.write("- **C2PA 메타데이터 검사:** 🤖 서명 발견 (AI 관련 인증 정보 포함)")
    else:
        st.write("- **C2PA 메타데이터 검사:** 🔍 서명 없음")
        
    if uploaded_file.type == "image/png":
        if png_prompt_detected:
            st.write("- **PNG 프롬프트 검사:** 🤖 AI 생성 프롬프트(parameters) 설정값 확인됨")
        else:
            st.write("- **PNG 프롬프트 검사:** 🔍 프롬프트 흔적 없음")
            
    if has_exif:
        st.write("- **EXIF 카메라 정보 검사:** 📷 정상적인 카메라 촬영 정보 발견됨")
    else:
        st.write("- **EXIF 카메라 정보 검사:** ❌ 카메라 촬영 정보(EXIF)가 없음")

    st.divider()

    # 최종 판정 출력
    if is_ai:
        st.error("🤖 **[판정] 해당 이미지는 AI 이미지입니다.**")
        st.write("**[상세 판정 근거]**")
        for reason in ai_reasons:
            st.write(f"- {reason}")
    else:
        st.success("📷 **[판정] 해당 이미지는 AI가 아닙니다.**")
        st.write("- 모든 검사 결과 정상적인 실제 촬영 사진의 조건들을 충족합니다.")