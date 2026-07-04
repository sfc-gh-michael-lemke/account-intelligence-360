import snowflake.connector
import json, os

conn = snowflake.connector.connect(connection_name="SNOWHOUSE_AWS_US_WEST_2")
cur = conn.cursor()

REQUEST = json.dumps({
    "json_proto": {
        "name": "account_intelligence_360",
        "database": "MDM",
        "schema": "MDM_INTERFACES",
        "tables": [
            {
                "database": "MDM", "schema": "MDM_INTERFACES",
                "table": "SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY",
                "columnNames": ["SOURCE_SYSTEM_ENTITY_ID","ACCOUNT_TYPE","ACCOUNT_NAME",
                                 "FINAL_INDUSTRY","FINAL_SUBINDUSTRY","FINAL_LOGIC",
                                 "SFDC_INDUSTRY","SFDC_SUBINDUSTRY","CB_INDUSTRY",
                                 "CB_SUBINDUSTRY","GPU_INDUSTRY","GPU_SUBINDUSTRY"]
            },
            {
                "database": "MDM", "schema": "MDM_INTERFACES",
                "table": "SFDC_ACCOUNT_CONSOLIDATED_EMPLOYEE_COUNT",
                "columnNames": ["SOURCE_SYSTEM_ENTITY_ID","ACCOUNT_TYPE","ACCOUNT_NAME",
                                 "FINAL_EMPLOYEE_COUNT","FINAL_LOGIC","SFDC_EMPLOYEE_COUNT",
                                 "DNB_EMPLOYEE_COUNT","CB_EMPLOYEE_COUNT","GPU_EMPLOYEE_COUNT"]
            },
            {
                "database": "MDM", "schema": "MDM_INTERFACES",
                "table": "CRUNCHBASE_MAP_TO_ACCOUNT_SFDC",
                "columnNames": ["ACCOUNT_ID","SOURCE_SYSTEM_ENTITY_ID","ACCOUNT_TYPE",
                                 "ACCOUNT_SUBTYPE","ACCOUNT_ID_CRUNCHBASE"]
            },
            {
                "database": "MDM", "schema": "MDM_INTERFACES",
                "table": "SAI_PILOT_TECH_STACK",
                "columnNames": ["OBJECT_ID","NAME","TYPE","PROSPECT_TIER_C","APS_C",
                                 "INDUSTRY","CLEAN_ACCOUNT_TYPE_C"]
            },
            {
                "database": "MDM", "schema": "MDM_INTERFACES",
                "table": "CUSTOMER_PARTY_ACCOUNT_MAP_SFDC",
                "columnNames": ["SOURCE_SYSTEM_ENTITY_ID","PARTY_ID","ACCOUNT_ID","CUSTOMER_ID_WD"]
            }
        ],
        "sqlSource": {
            "queries": [
                {
                    "sqlText": "SELECT FINAL_INDUSTRY, ACCOUNT_TYPE, COUNT(DISTINCT SOURCE_SYSTEM_ENTITY_ID) AS account_count FROM MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY WHERE FINAL_INDUSTRY IS NOT NULL GROUP BY FINAL_INDUSTRY, ACCOUNT_TYPE ORDER BY account_count DESC",
                    "correspondingQuestion": "How many accounts are in each industry by account type?"
                },
                {
                    "sqlText": "SELECT ind.FINAL_INDUSTRY, ind.FINAL_SUBINDUSTRY, ind.ACCOUNT_TYPE, COUNT(DISTINCT ind.SOURCE_SYSTEM_ENTITY_ID) AS account_count FROM MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY ind WHERE ind.FINAL_INDUSTRY IS NOT NULL GROUP BY ind.FINAL_INDUSTRY, ind.FINAL_SUBINDUSTRY, ind.ACCOUNT_TYPE ORDER BY ind.FINAL_INDUSTRY, account_count DESC",
                    "correspondingQuestion": "Show me accounts by industry and subindustry"
                },
                {
                    "sqlText": "SELECT ind.FINAL_INDUSTRY, COUNT(DISTINCT ind.SOURCE_SYSTEM_ENTITY_ID) AS total_accounts, COUNT(DISTINCT cb.SOURCE_SYSTEM_ENTITY_ID) AS accounts_with_crunchbase FROM MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY ind LEFT JOIN MDM.MDM_INTERFACES.CRUNCHBASE_MAP_TO_ACCOUNT_SFDC cb ON ind.SOURCE_SYSTEM_ENTITY_ID = cb.SOURCE_SYSTEM_ENTITY_ID WHERE ind.FINAL_INDUSTRY IS NOT NULL GROUP BY ind.FINAL_INDUSTRY ORDER BY total_accounts DESC",
                    "correspondingQuestion": "Which industries have the most accounts with Crunchbase enrichment?"
                },
                {
                    "sqlText": "SELECT ind.FINAL_INDUSTRY, sai.PROSPECT_TIER_C, COUNT(DISTINCT ind.SOURCE_SYSTEM_ENTITY_ID) AS account_count, AVG(sai.APS_C) AS avg_aps_score FROM MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY ind LEFT JOIN MDM.MDM_INTERFACES.SAI_PILOT_TECH_STACK sai ON ind.SOURCE_SYSTEM_ENTITY_ID = sai.OBJECT_ID WHERE sai.PROSPECT_TIER_C IS NOT NULL GROUP BY ind.FINAL_INDUSTRY, sai.PROSPECT_TIER_C ORDER BY avg_aps_score DESC",
                    "correspondingQuestion": "What is the average APS score by industry and prospect tier?"
                },
                {
                    "sqlText": "SELECT ind.ACCOUNT_TYPE, ind.FINAL_INDUSTRY, COUNT(DISTINCT ind.SOURCE_SYSTEM_ENTITY_ID) AS account_count FROM MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY ind LEFT JOIN MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_EMPLOYEE_COUNT emp ON ind.SOURCE_SYSTEM_ENTITY_ID = emp.SOURCE_SYSTEM_ENTITY_ID WHERE ind.FINAL_INDUSTRY IS NOT NULL GROUP BY ind.ACCOUNT_TYPE, ind.FINAL_INDUSTRY ORDER BY account_count DESC",
                    "correspondingQuestion": "What is the breakdown of accounts by account type and industry?"
                }
            ]
        },
        "semanticDescription": "360-degree account intelligence semantic view for AEs and SDRs. Combines Salesforce account data with multi-source enrichment including industry classification (MDM-conformed from 7+ sources), employee count (consensus-scored), Crunchbase firmographic linkage, and SAI account priority scoring.",
        "metadata": {"warehouse": "SNOWHOUSE"}
    }
})

escaped = REQUEST.replace("'", "''")
cur.execute(f"SELECT SYSTEM$CORTEX_ANALYST_FAST_GENERATION('{escaped}') AS RESULT")
cur.execute("SET fastgen_qid = (SELECT LAST_QUERY_ID())")

cur.execute("SELECT PARSE_JSON($1):json_proto:semanticYaml::VARCHAR FROM TABLE(RESULT_SCAN($fastgen_qid))")
yaml_content = cur.fetchone()[0]

cur.execute("SELECT PARSE_JSON($1):json_proto:warnings FROM TABLE(RESULT_SCAN($fastgen_qid))")
warnings_raw = cur.fetchone()[0]

out_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(out_dir, "account_intelligence_360_semantic_model.yaml"), "w") as f:
    f.write(yaml_content)

metadata = {
    "semantic_view_name": "account_intelligence_360",
    "target_database": "MDM",
    "target_schema": "MDM_INTERFACES",
    "warnings": warnings_raw if warnings_raw else [],
    "errors": [],
    "suggestions_applied": [],
    "suggestions_filtered": [],
    "tables_included": [
        "MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_INDUSTRY",
        "MDM.MDM_INTERFACES.SFDC_ACCOUNT_CONSOLIDATED_EMPLOYEE_COUNT",
        "MDM.MDM_INTERFACES.CRUNCHBASE_MAP_TO_ACCOUNT_SFDC",
        "MDM.MDM_INTERFACES.SAI_PILOT_TECH_STACK",
        "MDM.MDM_INTERFACES.CUSTOMER_PARTY_ACCOUNT_MAP_SFDC"
    ]
}
with open(os.path.join(out_dir, "account_intelligence_360_metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

print(f"YAML length: {len(yaml_content)}")
print(f"Warnings: {warnings_raw}")
print("Files saved successfully.")
cur.close()
conn.close()
