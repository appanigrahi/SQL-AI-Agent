import requests
import streamlit as st

st.set_page_config(
    page_title="SQL AI Agent",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ SQL AI Agent")

st.markdown(
    """
### SQL Server Build Automation Portal

Workflow:

Build Request → PreCheck → Build Plan → Installation → Validation
"""
)

st.divider()

# --------------------------------------------------
# Build Request Section
# --------------------------------------------------

st.subheader("Build Request")

col1, col2 = st.columns(2)

with col1:

    server_name = st.text_input(
        "Target Server",
        value="SQL01"
    )

    sql_version = st.selectbox(
        "SQL Version",
        [
            "SQL Server 2019",
            "SQL Server 2022"
        ]
    )

with col2:

    edition = st.selectbox(
        "Edition",
        [
            "Enterprise",
            "Standard",
            "Developer"
        ]
    )

    instance_name = st.text_input(
        "Instance Name",
        value="MSSQLSERVER"
    )

run_button = st.button(
    "Run PreCheck",
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# Build Request Summary
# --------------------------------------------------

st.subheader("Requested Build Configuration")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.info(server_name)

with c2:
    st.info(sql_version)

with c3:
    st.info(edition)

with c4:
    st.info(instance_name)

st.divider()

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

            if response.status_code != 200:

                st.error(
                    f"API Error: {response.status_code}"
                )

                st.json(response.json())

            else:

                result = response.json()

                report = result["PreCheckReport"]

                if report["ReadyForBuild"]:

                    st.success(
                        "✅ SERVER READY FOR BUILD"
                    )

                else:

                    st.warning(
                        "⚠️ SERVER NOT READY FOR BUILD"
                    )

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.metric(
                        "Server",
                        report["Hostname"]
                    )

                with c2:
                    st.metric(
                        "Domain",
                        report["Domain"]
                    )

                with c3:
                    st.metric(
                        "Memory (GB)",
                        report["MemoryGB"]
                    )

                with c4:
                    st.metric(
                        "CPU",
                        report["LogicalCPUCount"]
                    )

                st.divider()

                st.subheader(
                    "Build Readiness Checks"
                )

                for check in report["Checks"]:

                    if check["Status"] == "PASS":

                        st.success(
                            f"{check['CheckName']} | "
                            f"{check['Actual']}"
                        )

                    else:

                        st.error(
                            f"{check['CheckName']} | "
                            f"{check['Actual']}"
                        )

                st.divider()

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

                with st.expander(
                    "Full JSON Report"
                ):
                    st.json(report)

        except Exception as ex:

            st.error(str(ex))