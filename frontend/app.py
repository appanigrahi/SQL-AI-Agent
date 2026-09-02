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
# Header
# --------------------------------------------------

st.title("🖥️ SQL AI Agent")

st.markdown(
    """
AI Powered SQL Server Build Assistant

Current Workflow:

Build Request → PreCheck → Build Plan → Installation → Validation
"""
)

st.divider()

# --------------------------------------------------
# Input Section
# --------------------------------------------------

left, right = st.columns([3, 1])

with left:

    server_name = st.text_input(
        "Server Name",
        value="SQL01"
    )

with right:

    st.write("")
    st.write("")

    run_button = st.button(
        "Run PreCheck",
        use_container_width=True
    )

# --------------------------------------------------
# Run PreCheck
# --------------------------------------------------

if run_button:

    with st.spinner(
        f"Running PreCheck against {server_name}"
    ):

        try:

            response = requests.get(
                "http://127.0.0.1:8000/precheck",
                params={
                    "server": server_name
                },
                timeout=120
            )

            # ----------------------------------
            # Error Handling
            # ----------------------------------

            if response.status_code != 200:

                st.error(
                    f"API Error: {response.status_code}"
                )

                st.json(
                    response.json()
                )

            else:

                result = response.json()

                report = result["PreCheckReport"]

                # ----------------------------------
                # Status Banner
                # ----------------------------------

                if report["ReadyForBuild"]:

                    st.success(
                        "✅ SERVER READY FOR BUILD"
                    )

                else:

                    st.warning(
                        "⚠️ SERVER NOT READY FOR BUILD"
                    )

                # ----------------------------------
                # Summary Cards
                # ----------------------------------

                card1, card2, card3, card4 = st.columns(4)

                with card1:

                    st.metric(
                        "Server",
                        report["Hostname"]
                    )

                with card2:

                    st.metric(
                        "Domain",
                        report["Domain"]
                    )

                with card3:

                    st.metric(
                        "Memory (GB)",
                        report["MemoryGB"]
                    )

                with card4:

                    st.metric(
                        "CPU",
                        report["LogicalCPUCount"]
                    )

                st.divider()

                # ----------------------------------
                # Infrastructure Section
                # ----------------------------------

                st.subheader(
                    "Infrastructure Details"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"Operating System: {report['OperatingSystem']}"
                    )

                    st.write(
                        f"C Drive Free: {report['CDriveFreeGB']} GB"
                    )

                with col2:

                    st.write(
                        f"C Drive Size: {report['CDriveSizeGB']} GB"
                    )

                    st.write(
                        f"Pending Reboot: {report['PendingReboot']}"
                    )

                st.divider()

                # ----------------------------------
                # Check Results
                # ----------------------------------

                st.subheader(
                    "Build Readiness Checks"
                )

                for check in report["Checks"]:

                    if check["Status"] == "PASS":

                        st.success(
                            f"{check['CheckName']} | "
                            f"Expected: {check['Expected']} | "
                            f"Actual: {check['Actual']}"
                        )

                    else:

                        st.error(
                            f"{check['CheckName']} | "
                            f"Expected: {check['Expected']} | "
                            f"Actual: {check['Actual']}"
                        )

                st.divider()

                # ----------------------------------
                # Summary Dashboard
                # ----------------------------------

                st.subheader(
                    "Summary"
                )

                s1, s2, s3 = st.columns(3)

                with s1:

                    st.metric(
                        "Total Checks",
                        report["Summary"]["TotalChecks"]
                    )

                with s2:

                    st.metric(
                        "Passed",
                        report["Summary"]["PassedChecks"]
                    )

                with s3:

                    st.metric(
                        "Failed",
                        report["Summary"]["FailedChecks"]
                    )

                st.divider()

                # ----------------------------------
                # Full JSON Report
                # ----------------------------------

                with st.expander(
                    "View Full JSON Report"
                ):

                    st.json(
                        report
                    )

        except Exception as ex:

            st.error(
                str(ex)
            )