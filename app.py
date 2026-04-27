

import base64
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import streamlit as st

from src.db.db import (
    get_all_extractions,
    get_extraction_by_id,
    init_db,
    save_extraction,
    update_extraction_json,
    update_extraction_status,
)
from src.export.export_to_excel import export_to_excel
from src.normalization.normalizer import normalize_extraction
from src.pipeline.run_pipeline import run_pipeline


UPLOAD_DIR = Path("data/uploaded_pdfs")
EXCEL_OUTPUT_PATH = Path("data/output/seveso_cov_export.xlsx")


def setup_page():
    """Configurações gerais da página Streamlit."""
    st.set_page_config(
        page_title="Aludec SDS Extractor",
        page_icon="📄",
        layout="wide",
    )
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_pdf(uploaded_file) -> Path:
    """Guarda o PDF carregado pelo utilizador numa pasta local."""
    pdf_path = UPLOAD_DIR / uploaded_file.name
    pdf_path.write_bytes(uploaded_file.getbuffer())
    return pdf_path


def render_pdf(pdf_path: str):
    """Mostra o PDF no browser através de um iframe embebido."""
    path = Path(pdf_path)

    if not path.exists():
        st.warning("PDF file not found on disk.")
        return

    pdf_bytes = path.read_bytes()
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f"""
    <iframe
        src="data:application/pdf;base64,{encoded_pdf}"
        width="100%"
        height="850px"
        type="application/pdf">
    </iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)


def substances_to_dataframe(data: dict) -> pd.DataFrame:
    """Converte a lista de substâncias para uma tabela editável."""
    substances = data.get("substances") or []

    if not substances:
        return pd.DataFrame(columns=["name", "cas_number", "percentage"])

    return pd.DataFrame(substances)


def dataframe_to_substances(df: pd.DataFrame) -> list[dict]:
    """Converte a tabela editada de volta para lista de substâncias."""
    substances = []

    for _, row in df.fillna("").iterrows():
        name = str(row.get("name", "")).strip()
        cas_number = str(row.get("cas_number", "")).strip()
        percentage = str(row.get("percentage", "")).strip()

        if not name and not cas_number and not percentage:
            continue

        substances.append({
            "name": name,
            "cas_number": cas_number,
            "percentage": percentage,
        })

    return substances


def hazards_to_dataframe(data: dict) -> pd.DataFrame:
    """Converte os perigos para uma tabela editável."""
    hazards = data.get("hazards") or []

    if not hazards:
        return pd.DataFrame(columns=["code", "description"])

    return pd.DataFrame(hazards)


def dataframe_to_hazards(df: pd.DataFrame) -> list[dict]:
    """Converte a tabela editada de perigos de volta para JSON."""
    hazards = []

    for _, row in df.fillna("").iterrows():
        code = str(row.get("code", "")).strip()
        description = str(row.get("description", "")).strip()

        if not code and not description:
            continue

        hazards.append({
            "code": code,
            "description": description,
        })

    return hazards


def key_value_editor(title: str, data: dict, key_prefix: str) -> dict:
    """Editor simples para blocos pequenos como transporte, Seveso e propriedades físicas."""
    st.subheader(title)

    edited = {}
    for field, value in (data or {}).items():
        edited[field] = st.text_input(
            field,
            value=str(value or ""),
            key=f"{key_prefix}_{field}",
        )

    return edited


def upload_page():
    """Página inicial: upload de PDF e processamento para estado pending_review."""
    st.header("1. Upload e extração")
    st.write("Carrega uma ficha SDS em PDF. A extração fica em revisão antes de entrar no Excel final.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file is None:
        return

    pdf_path = save_uploaded_pdf(uploaded_file)
    st.success(f"PDF saved: {pdf_path}")

    if st.button("Processar PDF", type="primary"):
        with st.spinner("A processar PDF com o pipeline..."):
            sds_document = run_pipeline(pdf_path)
            extracted_json = asdict(sds_document)

            extraction_id = save_extraction(
                file_name=pdf_path.name,
                pdf_path=str(pdf_path),
                extracted_json=extracted_json,
            )

        st.success(f"Extração criada em pending_review com ID {extraction_id}.")
        st.info("Vai à página 'Revisão manual' para validar e aprovar a extração.")


def review_page():
    """Página de revisão: tabela editável + PDF ao lado."""
    st.header("2. Revisão manual")

    extractions = get_all_extractions()
    pending = [item for item in extractions if item.get("status") == "pending_review"]

    if not pending:
        st.info("Não existem extrações pendentes de revisão.")
        return

    options = {
        f"ID {item['id']} - {item['file_name']}": item["id"]
        for item in pending
    }

    selected_label = st.selectbox("Extrações pendentes", list(options.keys()))
    extraction_id = options[selected_label]
    extraction = get_extraction_by_id(extraction_id)

    if extraction is None:
        st.error("Extração não encontrada.")
        return

    raw_data = extraction["extracted_json"]
    normalized_data = normalize_extraction(raw_data)

    left_col, right_col = st.columns([1.15, 1])

    with left_col:
        st.subheader("Dados extraídos")
        st.caption(f"Status atual: {extraction['status']}")
        st.caption(f"Validação automática: {normalized_data.get('validation_status', 'REVIEW')}")

        st.markdown("### Substâncias")
        substances_df = substances_to_dataframe(normalized_data)
        edited_substances = st.data_editor(
            substances_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"substances_{extraction_id}",
        )

        st.markdown("### Perigos")
        hazards_df = hazards_to_dataframe(normalized_data)
        edited_hazards = st.data_editor(
            hazards_df,
            num_rows="dynamic",
            use_container_width=True,
            key=f"hazards_{extraction_id}",
        )

        edited_transport = key_value_editor(
            "Transporte",
            normalized_data.get("transport") or {},
            f"transport_{extraction_id}",
        )

        edited_seveso = key_value_editor(
            "Seveso",
            normalized_data.get("seveso") or {},
            f"seveso_{extraction_id}",
        )

        edited_physical = key_value_editor(
            "Propriedades físicas",
            normalized_data.get("physical_properties") or {},
            f"physical_{extraction_id}",
        )

        approve = st.checkbox("Aprovar esta extração para exportação final", value=False)

        if st.button("Guardar revisão", type="primary"):
            updated_data = dict(raw_data)
            updated_data["substances"] = dataframe_to_substances(edited_substances)
            updated_data["hazards"] = dataframe_to_hazards(edited_hazards)
            updated_data["transport"] = edited_transport
            updated_data["seveso"] = edited_seveso
            updated_data["physical_properties"] = edited_physical

            update_extraction_json(extraction_id, updated_data)

            if approve:
                update_extraction_status(extraction_id, "approved")
                st.success("Revisão guardada e extração aprovada.")
            else:
                update_extraction_status(extraction_id, "reviewed")
                st.success("Revisão guardada. Extração ficou como reviewed.")

            st.rerun()

    with right_col:
        st.subheader("PDF original")
        render_pdf(extraction["pdf_path"])


def export_page():
    """Página para gerar e descarregar o Excel final com dados aprovados."""
    st.header("3. Exportar Excel")
    st.write("O Excel final só inclui extrações com estado approved.")

    approved = [item for item in get_all_extractions() if item.get("status") == "approved"]
    st.metric("Extrações aprovadas", len(approved))

    if st.button("Gerar Excel final", type="primary"):
        with st.spinner("A gerar Excel final..."):
            export_to_excel()
        st.success("Excel gerado com sucesso.")

    if EXCEL_OUTPUT_PATH.exists():
        st.download_button(
            label="Download Excel",
            data=EXCEL_OUTPUT_PATH.read_bytes(),
            file_name=EXCEL_OUTPUT_PATH.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.info("Ainda não existe Excel gerado.")


def database_page():
    """Página simples para consultar o estado das extrações na BD."""
    st.header("4. Extrações guardadas")

    extractions = get_all_extractions()

    if not extractions:
        st.info("Ainda não há extrações guardadas.")
        return

    df = pd.DataFrame(extractions)
    st.dataframe(df, use_container_width=True)


def main():
    setup_page()

    st.title("Aludec SDS Extractor")
    st.caption("Extração de fichas SDS, revisão manual e exportação para Excel SEVESO/COV.")

    page = st.sidebar.radio(
        "Menu",
        [
            "Upload e extração",
            "Revisão manual",
            "Exportar Excel",
            "Base de dados",
        ],
    )

    if page == "Upload e extração":
        upload_page()
    elif page == "Revisão manual":
        review_page()
    elif page == "Exportar Excel":
        export_page()
    elif page == "Base de dados":
        database_page()


if __name__ == "__main__":
    main()