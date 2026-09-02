import requests
import streamlit as st


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="SQL AI Agent",
    page_icon="🖥️",
    layout="wide"
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("SQL AI Agent")

st.markdown(
    "SQL Server Build Readiness Assessment"
)

# --------------------------------------------------
# Input Section
# --------------------------------------------------

server_name = st.text_input(
    "Server Name",
    value="SQL01"
)

run_button = st.button(
    "Run PreCheck"
)

# --------------------------------------------------
# Execute PreCheck
# --------------------------------------------------

if run_button:

    with st.spinner(
        f"Running PreCheck against {server_name}..."
    ):

        try:

            response = requests.get(
                "http://127.0.0.1:8000/precheck",
                params={
                    "server": server_name
                },
                timeout=120
            )

            if response.status_code != 200:

                st.error(
                    f"API Error: {response.status_code}"
                )

                st.json(
                    response.json()
                )

            else:

                result = response.json()

                report = result[
                    "PreCheckReport"
                ]

                st.success(
                    "PreCheck completed successfully."
                )

                # ----------------------------------
                # Summary Information
                # ----------------------------------

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Server",
                        report["Hostname"]
                    )

                with col2:
                    st.metric(
                        "Domain",
                        report["Domain"]
                    )

                with col3:
                    st.metric(
                        "Ready For Build",
                        str(
                            report["ReadyForBuild"]
                        )
                    )

                st.divider()

                # ----------------------------------
                # Infrastructure Details
                # ----------------------------------

                st.subheader(
                    "Infrastructure"
                )

                st.write(
                    f"Operating System: "
                    f"{report['OperatingSystem']}"
                )

                st.write(
                    f"Logical CPU Count: "
                    f"{report['LogicalCPUCount']}"
                )

                st.write(
                    f"Memory (GB): "
                    f"{report['MemoryGB']}"
                )

                st.write(
                    f"C Drive Free (GB): "
                    f"{report['CDriveFreeGB']}"
                )

                st.write(
                    f"C Drive Size (GB): "
                    f"{report['CDriveSizeGB']}"
                )

                st.divider()

                # ----------------------------------
                # Checks
                # ----------------------------------

                st.subheader(
                    "Checks"
                )

                for check in report["Checks"]:

                    status = check["Status"]

                    if status == "PASS":

                        st.success(
                            f"{check['CheckName']} "
                            f"→ PASS"
                        )

                    else:

                        st.error(
                            f"{check['CheckName']} "
                            f"→ FAIL"
                        )

                st.divider()

                # ----------------------------------
                # Summary
                # ----------------------------------

                st.subheader(
                    "Summary"
                )

                st.json(
                    report["Summary"]
                )

                st.divider()

                # ----------------------------------
                # Full JSON
                # ----------------------------------

                with st.expander(
                    "View Full Report"
                ):
                    st.json(report)

        except Exception as ex:

            st.error(
                str(ex)
            )