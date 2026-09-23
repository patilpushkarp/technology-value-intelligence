"""Deterministic Enterprise Data Generator for Technology Value Intelligence.

Generates consistent synthetic data modeling an enterprise technology landscape
including Business Units, Capabilities, IT Services, Applications, Infrastructure,
Vendors, Projects, Costs, Consumption, Benefits, and KPIs.

Explicitly incorporates Scenarios A through H:
- Scenario A: Expensive but highly utilized (APP001)
- Scenario B: Expensive and underutilized (APP021)
- Scenario C: Duplicate capability overlap (CAP003 supported by APP005 & APP012)
- Scenario D: Single critical dependency bottleneck (APP010)
- Scenario E: Successful investment with realized benefits (PRJ003)
- Scenario F: Benefit gap with cost overrun (PRJ014)
- Scenario G: Cost increase driven by consumption growth (APP014)
- Scenario H: Cost increase without consumption growth (APP022)
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from tvi.config import Config, load_config


class EnterpriseDataGenerator:
    """Generates synthetic enterprise datasets with deterministic seeds."""

    def __init__(self, config: Config | None = None):
        self.config = config or load_config()
        self.seed = self.config.project.random_seed
        self.rng = np.random.default_rng(self.seed)
        self.year = self.config.project.reporting_year
        self.months = [f"{self.year}-{m:02d}" for m in range(1, self.config.data.months + 1)]

    def generate_all(self, output_dir: str | Path | None = None) -> Dict[str, pd.DataFrame]:
        """Generate all enterprise entities and relationship tables.

        Args:
            output_dir: Optional path to save CSV files. Defaults to config generated_dir.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary of generated DataFrames.
        """
        # 1. Core Master Entities
        bu_df = self.generate_business_units()
        cap_df = self.generate_business_capabilities(bu_df)
        srv_df = self.generate_it_services()
        ven_df = self.generate_vendors()
        tech_df = self.generate_technologies(ven_df)
        app_df = self.generate_applications(srv_df, ven_df)
        prj_df = self.generate_projects(bu_df)

        # 2. Inter-entity Mapping / Relationships
        rel_app_tech = self.generate_app_technology_relations(app_df, tech_df)
        rel_app_cap = self.generate_app_capability_relations(app_df, cap_df)
        rel_app_dep = self.generate_app_dependencies(app_df)
        rel_prj_cap = self.generate_project_capability_relations(prj_df, cap_df)
        rel_app_prj = self.generate_app_project_relations(app_df, prj_df)

        # 3. Benefits and KPIs
        ben_df = self.generate_benefits(prj_df)
        kpi_df = self.generate_kpis()
        rel_ben_kpi = self.generate_benefit_kpi_relations(ben_df, kpi_df)

        # 4. Operational & Financial Time-series Data (12 months)
        cost_df = self.generate_cost_records(
            app_df, srv_df, bu_df, ven_df, prj_df, rel_app_cap
        )
        cons_df = self.generate_consumption_records(app_df, bu_df)

        datasets = {
            "business_units": bu_df,
            "business_capabilities": cap_df,
            "it_services": srv_df,
            "vendors": ven_df,
            "technologies": tech_df,
            "applications": app_df,
            "projects": prj_df,
            "rel_app_technology": rel_app_tech,
            "rel_app_capability": rel_app_cap,
            "rel_app_dependency": rel_app_dep,
            "rel_project_capability": rel_prj_cap,
            "rel_app_project": rel_app_prj,
            "benefits": ben_df,
            "kpis": kpi_df,
            "rel_benefit_kpi": rel_ben_kpi,
            "cost_records": cost_df,
            "consumption_records": cons_df,
        }

        if output_dir is not None or self.config.data.generated_dir:
            from tvi.config import get_project_root
            raw_target = Path(output_dir or self.config.data.generated_dir)
            if not raw_target.is_absolute():
                out_path = (get_project_root() / raw_target.name if raw_target.parts[0] == ".." else get_project_root() / raw_target).resolve()
            else:
                out_path = raw_target.resolve()
            out_path.mkdir(parents=True, exist_ok=True)
            for name, df in datasets.items():
                df.to_csv(out_path / f"{name}.csv", index=False)

        return datasets

    def generate_business_units(self) -> pd.DataFrame:
        """Generate Business Unit records."""
        bu_definitions = [
            ("BU001", "Retail Banking", "India", "Business Unit", 125000000000.0, 8500),
            ("BU002", "Commercial Banking", "India", "Business Unit", 95000000000.0, 4200),
            ("BU003", "Wealth Management", "Global", "Business Unit", 68000000000.0, 2800),
            ("BU004", "Digital Payments", "India", "Business Unit", 82000000000.0, 3100),
            ("BU005", "Cards & Lending", "India", "Business Unit", 74000000000.0, 3900),
            ("BU006", "Operations & Shared Services", "India", "Shared Services", 15000000000.0, 11200),
            ("BU007", "Corporate Functions", "Global", "Corporate Function", 8000000000.0, 2400),
            ("BU008", "Insurance Solutions", "APAC", "Business Unit", 45000000000.0, 1900),
            ("BU009", "Treasury & Capital Markets", "Global", "Business Unit", 54000000000.0, 1200),
            ("BU010", "Risk & Compliance", "Global", "Corporate Function", 6000000000.0, 1600),
        ]
        return pd.DataFrame(
            bu_definitions[: self.config.data.business_units],
            columns=[
                "business_unit_id",
                "business_unit_name",
                "region",
                "business_unit_type",
                "annual_revenue",
                "employee_count",
            ],
        )

    def generate_business_capabilities(self, bu_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Business Capability definitions."""
        capability_defs = [
            ("CAP001", "Customer Management", "BU001", "High", "Business Critical", "VP Customer Experience"),
            ("CAP002", "Order Management", "BU004", "High", "Mission Critical", "Head of Digital Operations"),
            ("CAP003", "Order-to-Cash", "BU004", "High", "Mission Critical", "Director Order Processing"),
            ("CAP004", "Procure-to-Pay", "BU006", "Medium", "Operational", "Head of Procurement"),
            ("CAP005", "Financial Reporting", "BU007", "High", "Mission Critical", "Chief Financial Officer"),
            ("CAP006", "Supply Chain Planning", "BU006", "Medium", "Business Critical", "VP Supply Chain"),
            ("CAP007", "Product Management", "BU001", "Medium", "Operational", "Head of Product Strategy"),
            ("CAP008", "Digital Commerce", "BU004", "High", "Mission Critical", "Head of eCommerce"),
            ("CAP009", "Workforce Management", "BU007", "Low", "Operational", "Chief People Officer"),
            ("CAP010", "Data & Analytics", "BU006", "High", "Business Critical", "Chief Data Officer"),
            ("CAP011", "Customer Service", "BU001", "High", "Business Critical", "Director Service Operations"),
            ("CAP012", "Risk Management", "BU010", "High", "Mission Critical", "Chief Risk Officer"),
            ("CAP013", "Regulatory Reporting", "BU010", "High", "Mission Critical", "Head of Regulatory Affairs"),
            ("CAP014", "Marketing", "BU001", "Medium", "Standard", "Chief Marketing Officer"),
            ("CAP015", "Sales Management", "BU002", "High", "Business Critical", "VP Enterprise Sales"),
            ("CAP016", "Enterprise Planning", "BU007", "Medium", "Business Critical", "Head of Corporate Planning"),
            ("CAP017", "Treasury Operations", "BU009", "High", "Mission Critical", "Head of Global Treasury"),
            ("CAP018", "Accounts Payable", "BU007", "Medium", "Operational", "Controller Accounts Payable"),
            ("CAP019", "Accounts Receivable", "BU007", "Medium", "Operational", "Controller Accounts Receivable"),
            ("CAP020", "Procurement Operations", "BU006", "Low", "Standard", "Director Strategic Sourcing"),
            ("CAP021", "Wealth Advisory", "BU003", "High", "Business Critical", "Head of Wealth Management"),
            ("CAP022", "Loan Origination", "BU005", "High", "Mission Critical", "Head of Retail Lending"),
            ("CAP023", "Fraud Detection", "BU010", "High", "Mission Critical", "Director Financial Crime"),
            ("CAP024", "Identity Verification", "BU006", "High", "Mission Critical", "Head of Identity Security"),
            ("CAP025", "Claims Processing", "BU008", "Medium", "Business Critical", "Head of Insurance Claims"),
        ]
        return pd.DataFrame(
            capability_defs[: self.config.data.capabilities],
            columns=[
                "capability_id",
                "capability_name",
                "business_unit_id",
                "strategic_priority",
                "criticality",
                "capability_owner",
            ],
        )

    def generate_it_services(self) -> pd.DataFrame:
        """Generate IT Service catalog entries."""
        services = [
            ("SRV001", "ERP Services", "Business Applications", "Director ERP Applications", "Tier 1", "99.99%"),
            ("SRV002", "CRM Services", "Business Applications", "Head of Customer Platforms", "Tier 2", "99.95%"),
            ("SRV003", "Data Analytics Platform", "Analytics", "Chief Data Architect", "Tier 2", "99.90%"),
            ("SRV004", "Enterprise Collaboration", "Workplace", "Head of End User Compute", "Tier 3", "99.50%"),
            ("SRV005", "Cloud Platform Services", "Infrastructure", "VP Cloud Engineering", "Tier 1", "99.99%"),
            ("SRV006", "Identity & Access Management", "Security", "Chief Information Security Officer", "Tier 1", "99.99%"),
            ("SRV007", "Customer Digital Banking Platform", "Business Applications", "Head of Digital Channels", "Tier 1", "99.99%"),
            ("SRV008", "Supply Chain Systems", "Business Applications", "Director Logistics Applications", "Tier 2", "99.90%"),
            ("SRV009", "Finance & Accounting Systems", "Business Applications", "Head of Financial Systems", "Tier 1", "99.95%"),
            ("SRV010", "Integration & API Services", "Platform", "Director Integration Architecture", "Tier 1", "99.99%"),
            ("SRV011", "Payment Processing Engine", "Business Applications", "Head of Payments Tech", "Tier 1", "99.99%"),
            ("SRV012", "Core Banking Services", "Business Applications", "Director Core Banking", "Tier 1", "99.99%"),
            ("SRV013", "Workflow Automation Suite", "Platform", "Head of Automation CoE", "Tier 2", "99.90%"),
            ("SRV014", "Enterprise Content Management", "Workplace", "Director Workplace Solutions", "Tier 3", "99.50%"),
            ("SRV015", "Cybersecurity Operations & SOC", "Security", "Head of Threat Operations", "Tier 1", "99.99%"),
            ("SRV016", "Data Lakehouse Infrastructure", "Platform", "Director Big Data Infrastructure", "Tier 2", "99.95%"),
            ("SRV017", "Global Network & Connectivity", "Infrastructure", "Director Network Services", "Tier 1", "99.99%"),
            ("SRV018", "Regulatory Compliance Systems", "Business Applications", "Head of RegTech", "Tier 1", "99.95%"),
        ]
        return pd.DataFrame(
            services[: self.config.data.services],
            columns=[
                "service_id",
                "service_name",
                "service_category",
                "service_owner",
                "criticality",
                "service_level",
            ],
        )

    def generate_vendors(self) -> pd.DataFrame:
        """Generate fictional Vendor records."""
        vendors = [
            ("VEN001", "TechNova", "Cloud Provider", 320000000.0, "2022-01-01", "2026-12-31"),
            ("VEN002", "CloudSphere", "Infrastructure", 185000000.0, "2023-03-01", "2025-02-28"),
            ("VEN003", "DataForge", "Data Platform", 140000000.0, "2022-07-01", "2025-06-30"),
            ("VEN004", "EnterpriseSoft", "Software License", 240000000.0, "2021-04-01", "2025-03-31"),
            ("VEN005", "InfraWorks", "Hardware", 95000000.0, "2023-01-01", "2026-12-31"),
            ("VEN006", "CyberShield", "Security", 110000000.0, "2023-06-01", "2026-05-31"),
            ("VEN007", "ApexLogic", "System Integrator", 160000000.0, "2022-10-01", "2025-09-30"),
            ("VEN008", "GlobalNet", "Telecom & Network", 125000000.0, "2021-01-01", "2025-12-31"),
            ("VEN009", "PrimeScale", "Compute & SaaS", 175000000.0, "2023-08-01", "2026-07-31"),
            ("VEN010", "SysCore", "Software License", 85000000.0, "2020-01-01", "2024-12-31"),
        ]
        return pd.DataFrame(
            vendors[: self.config.data.vendors],
            columns=[
                "vendor_id",
                "vendor_name",
                "vendor_category",
                "contract_value",
                "contract_start",
                "contract_end",
            ],
        )

    def generate_technologies(self, ven_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Technology catalog entries."""
        tech_list = [
            ("TECH001", "AWS Elastic Kubernetes Service", "Cloud", "TechNova", "Current", "Production"),
            ("TECH002", "PostgreSQL Enterprise Engine", "Database", "EnterpriseSoft", "Current", "Production"),
            ("TECH003", "Oracle Database 19c Enterprise", "Database", "EnterpriseSoft", "Tolerate", "Production"),
            ("TECH004", "Snowflake Cloud Data Warehouse", "Data Platform", "DataForge", "Current", "Production"),
            ("TECH005", "Apache Kafka Event Bus", "Middleware", "DataForge", "Current", "Production"),
            ("TECH006", "Redis In-Memory Cluster", "Database", "PrimeScale", "Current", "Production"),
            ("TECH007", "Red Hat Enterprise Linux 9", "Operating System", "SysCore", "Current", "Production"),
            ("TECH008", "Microsoft Azure Kubernetes Service", "Cloud", "CloudSphere", "Current", "Production"),
            ("TECH009", "Amazon S3 Object Storage", "Storage", "TechNova", "Current", "Production"),
            ("TECH010", "MongoDB Atlas Enterprise", "Database", "DataForge", "Current", "Production"),
            ("TECH011", "HashiCorp Terraform", "Middleware", "TechNova", "Current", "Production"),
            ("TECH012", "Cisco Catalyst Core Switches", "Network", "GlobalNet", "Current", "Production"),
            ("TECH013", "Palo Alto NextGen Firewalls", "Security", "CyberShield", "Current", "Production"),
            ("TECH014", "Docker Enterprise Container Runtime", "Compute", "PrimeScale", "Current", "Production"),
            ("TECH015", "Salesforce Financial Cloud", "SaaS", "EnterpriseSoft", "Current", "Production"),
            ("TECH016", "Apache Spark Analytical Engine", "Data Platform", "DataForge", "Current", "Production"),
            ("TECH017", "F5 BIG-IP Local Traffic Manager", "Network", "GlobalNet", "Current", "Production"),
            ("TECH018", "Elasticsearch Logging Cluster", "Data Platform", "DataForge", "Current", "Production"),
            ("TECH019", "IBM WebSphere Application Server", "Middleware", "SysCore", "Deprecated", "Production"),
            ("TECH020", "Solaris Operating Environment", "Operating System", "SysCore", "Legacy", "Production"),
            ("TECH021", "Dell PowerEdge Server Blades", "Hardware", "InfraWorks", "Current", "Production"),
            ("TECH022", "NetApp SAN Storage Arrays", "Storage", "InfraWorks", "Tolerate", "Production"),
            ("TECH023", "HashiCorp Vault Secrets Manager", "Security", "CyberShield", "Current", "Production"),
            ("TECH024", "Okta Workforce Identity", "Security", "CyberShield", "Current", "Production"),
            ("TECH025", "Kong API Gateway Enterprise", "Middleware", "PrimeScale", "Current", "Production"),
            ("TECH026", "Node.js Microservices Runtime", "Compute", "TechNova", "Current", "Production"),
            ("TECH027", "Python 3 Analytics Stack", "Compute", "DataForge", "Current", "Production"),
            ("TECH028", "Apache Cassandra NoSQL DB", "Database", "DataForge", "Tolerate", "Production"),
            ("TECH029", "RabbitMQ Messaging Broker", "Middleware", "PrimeScale", "Tolerate", "Production"),
            ("TECH030", "Splunk Enterprise SIEM", "Security", "CyberShield", "Current", "Production"),
            ("TECH031", "GitLab CI/CD Runner Farm", "Compute", "CloudSphere", "Current", "Production"),
            ("TECH032", "Dynatrace APM Monitoring", "Middleware", "CloudSphere", "Current", "Production"),
            ("TECH033", "VMware ESXi Hypervisor Cluster", "Compute", "InfraWorks", "Tolerate", "Production"),
            ("TECH034", "AWS Lambda Serverless Engine", "Cloud", "TechNova", "Current", "Production"),
            ("TECH035", "Mainframe z/OS Emulation Layer", "Compute", "SysCore", "Legacy", "Production"),
        ]
        return pd.DataFrame(
            tech_list[: self.config.data.technologies],
            columns=[
                "technology_id",
                "technology_name",
                "technology_category",
                "technology_vendor",
                "lifecycle_status",
                "environment",
            ],
        )

    def generate_applications(self, srv_df: pd.DataFrame, ven_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Application catalog entries with explicit lifecycle statuses."""
        app_names = [
            ("APP001", "CoreBanking Alpha", "SRV012", "Custom Built", "Strategic", "Mission Critical", "High", 35000000.0),
            ("APP002", "OmniCRM 360", "SRV002", "COTS", "Strategic", "Business Critical", "High", 28000000.0),
            ("APP003", "DataMesh Lakehouse", "SRV016", "Hybrid", "Strategic", "Business Critical", "High", 19500000.0),
            ("APP004", "Retail PayFlow Gateway", "SRV011", "Custom Built", "Strategic", "Mission Critical", "High", 22000000.0),
            ("APP005", "OrderFlow Enterprise", "SRV001", "COTS", "Strategic", "Mission Critical", "High", 25000000.0),
            ("APP006", "SmartProcure P2P", "SRV001", "COTS", "Strategic", "Operational", "Medium", 14000000.0),
            ("APP007", "Financial Consolidation Suite", "SRV009", "COTS", "Strategic", "Mission Critical", "High", 18000000.0),
            ("APP008", "Workforce Central HR", "SRV001", "SaaS", "Strategic", "Operational", "Medium", 12500000.0),
            ("APP009", "CloudVault Secrets Manager", "SRV006", "COTS", "Strategic", "Mission Critical", "High", 9500000.0),
            ("APP010", "Central Auth & Identity Hub", "SRV006", "Custom Built", "Strategic", "Mission Critical", "High", 16000000.0),
            ("APP011", "Customer Direct Portal", "SRV007", "Custom Built", "Strategic", "Mission Critical", "High", 31000000.0),
            ("APP012", "QuickOrder Legacy", "SRV001", "Custom Built", "Retire", "Operational", "Low", 11500000.0),
            ("APP013", "TradeExecution Engine", "SRV012", "Custom Built", "Strategic", "Mission Critical", "High", 29000000.0),
            ("APP014", "Cloud Payment Microhub", "SRV011", "Custom Built", "Strategic", "Mission Critical", "High", 14500000.0),
            ("APP015", "RiskPulse Engine", "SRV018", "COTS", "Strategic", "Mission Critical", "High", 21000000.0),
            ("APP016", "RegReport Automator", "SRV018", "Custom Built", "Strategic", "Mission Critical", "High", 15500000.0),
            ("APP017", "Campaign Studio Pro", "SRV002", "SaaS", "Tolerate", "Standard", "Low", 8500000.0),
            ("APP018", "ProcureDirect Legacy", "SRV001", "Custom Built", "Retire", "Operational", "Low", 9800000.0),
            ("APP019", "Global Ledger One", "SRV009", "COTS", "Strategic", "Mission Critical", "High", 38000000.0),
            ("APP020", "FraudSentry AI", "SRV015", "Hybrid", "Strategic", "Mission Critical", "High", 26000000.0),
            ("APP021", "Legacy Customer Web Portal", "SRV007", "Custom Built", "Tolerate", "Operational", "Medium", 24000000.0),
            ("APP022", "Batch Billing Engine v2", "SRV009", "Custom Built", "Migrate", "Operational", "Medium", 17500000.0),
            ("APP023", "Digital Lending Originator", "SRV012", "Custom Built", "Strategic", "Mission Critical", "High", 27500000.0),
            ("APP024", "WealthVision Portfolio", "SRV002", "COTS", "Strategic", "Business Critical", "High", 19000000.0),
            ("APP025", "ClaimsDirect Processor", "SRV013", "Custom Built", "Strategic", "Business Critical", "High", 13000000.0),
            ("APP026", "Strategic Sourcing Hub", "SRV001", "COTS", "Strategic", "Operational", "Low", 7800000.0),
            ("APP027", "Enterprise Service Desk", "SRV004", "SaaS", "Strategic", "Operational", "Medium", 9200000.0),
            ("APP028", "Document Vault Archive", "SRV014", "COTS", "Tolerate", "Standard", "Low", 6500000.0),
            ("APP029", "API Mesh Fabric", "SRV010", "Custom Built", "Strategic", "Mission Critical", "High", 18500000.0),
            ("APP030", "Corporate Treasury Net", "SRV009", "COTS", "Strategic", "Mission Critical", "High", 22500000.0),
            ("APP031", "Supplier Collaboration Portal", "SRV008", "Custom Built", "Tolerate", "Operational", "Low", 5800000.0),
            ("APP032", "Warehouse TrackMaster", "SRV008", "COTS", "Strategic", "Business Critical", "Medium", 11200000.0),
            ("APP033", "Logistics Fleet Dispatch", "SRV008", "Custom Built", "Strategic", "Business Critical", "Medium", 9500000.0),
            ("APP034", "Executive Dashboard BI", "SRV003", "COTS", "Strategic", "Business Critical", "High", 13500000.0),
            ("APP035", "Branch Teller Terminal", "SRV012", "Custom Built", "Tolerate", "Business Critical", "Medium", 19000000.0),
            ("APP036", "ATM Network Controller", "SRV011", "COTS", "Strategic", "Mission Critical", "High", 16500000.0),
            ("APP037", "Contact Center Telephony", "SRV004", "COTS", "Tolerate", "Business Critical", "Medium", 14200000.0),
            ("APP038", "Chatbot Virtual Assistant", "SRV007", "SaaS", "Strategic", "Operational", "Low", 6800000.0),
            ("APP039", "Mobile Banking App iOS/Android", "SRV007", "Custom Built", "Strategic", "Mission Critical", "High", 34000000.0),
            ("APP040", "Credit Bureau Interface", "SRV010", "Custom Built", "Strategic", "Mission Critical", "High", 8900000.0),
            ("APP041", "Anti-Money Laundering AML", "SRV018", "COTS", "Strategic", "Mission Critical", "High", 23000000.0),
            ("APP042", "Regulatory Archive System", "SRV014", "COTS", "Migrate", "Standard", "Low", 5100000.0),
            ("APP043", "Employee Travel & Expense", "SRV001", "SaaS", "Strategic", "Standard", "Low", 4200000.0),
            ("APP044", "Talent Acquisition Suite", "SRV004", "SaaS", "Tolerate", "Standard", "Low", 3800000.0),
            ("APP045", "Tax Calculation Engine", "SRV009", "COTS", "Strategic", "Mission Critical", "High", 10200000.0),
            ("APP046", "Fixed Asset Registry", "SRV009", "Custom Built", "Migrate", "Operational", "Low", 4900000.0),
            ("APP047", "Sales Forecasting Module", "SRV003", "Custom Built", "Strategic", "Operational", "Medium", 7200000.0),
            ("APP048", "Brand Asset Library", "SRV014", "SaaS", "Retire", "Standard", "Low", 3100000.0),
            ("APP049", "Security Incident Event Mgr", "SRV015", "COTS", "Strategic", "Mission Critical", "High", 24500000.0),
            ("APP050", "Vulnerability Scanner Hub", "SRV015", "COTS", "Strategic", "Business Critical", "High", 12800000.0),
        ]
        return pd.DataFrame(
            app_names[: self.config.data.applications],
            columns=[
                "application_id",
                "application_name",
                "service_id",
                "application_type",
                "lifecycle_status",
                "criticality",
                "business_criticality",
                "annual_license_cost",
            ],
        )

    def generate_projects(self, bu_df: pd.DataFrame) -> pd.DataFrame:
        """Generate Project and Investment records with variance profiles."""
        prj_data = [
            ("PRJ001", "Core Banking Cloud Migration", "Cloud Migration", "BU001", "2023-01-15", "2024-06-30", 180000000.0, 185000000.0, 45000000.0, "Completed"),
            ("PRJ002", "NextGen Enterprise Lakehouse", "AI", "BU006", "2023-04-01", "2024-09-30", 140000000.0, 138000000.0, 38000000.0, "Completed"),
            ("PRJ003", "Real-Time Payment Modernization", "Modernization", "BU004", "2023-03-01", "2024-05-31", 120000000.0, 115000000.0, 192000000.0, "Completed"),  # Scenario E: High realized benefit
            ("PRJ004", "Omnichannel CRM Rollout", "Transformation", "BU001", "2023-06-01", "2024-11-30", 95000000.0, 102000000.0, 26000000.0, "Completed"),
            ("PRJ005", "Procure-to-Pay Automation", "Automation", "BU006", "2023-08-01", "2024-07-31", 65000000.0, 62000000.0, 21000000.0, "Completed"),
            ("PRJ006", "Financial Consolidation Upgrade", "Modernization", "BU007", "2023-09-01", "2024-08-31", 72000000.0, 74000000.0, 18500000.0, "Completed"),
            ("PRJ007", "Zero-Trust Identity Fabric", "Infrastructure", "BU006", "2023-05-01", "2024-06-30", 88000000.0, 86000000.0, 24000000.0, "Completed"),
            ("PRJ008", "Mobile Banking 4.0 Redesign", "Transformation", "BU001", "2023-11-01", "2024-10-31", 110000000.0, 118000000.0, 42000000.0, "Completed"),
            ("PRJ009", "Order-to-Cash Optimization", "Automation", "BU004", "2024-01-01", "2024-12-31", 85000000.0, 84000000.0, 29000000.0, "In Progress"),
            ("PRJ010", "AI Fraud Prevention Shield", "AI", "BU010", "2023-07-01", "2024-08-31", 130000000.0, 126000000.0, 48000000.0, "Completed"),
            ("PRJ011", "Treasury Liquidity Hub", "Modernization", "BU009", "2024-02-01", "2024-11-30", 55000000.0, 57000000.0, 15000000.0, "In Progress"),
            ("PRJ012", "Retail Loan Origination FastTrack", "Transformation", "BU005", "2023-10-01", "2024-09-30", 92000000.0, 96000000.0, 31000000.0, "Completed"),
            ("PRJ013", "Claims Auto-Adjudication AI", "AI", "BU008", "2024-01-15", "2024-12-15", 78000000.0, 75000000.0, 22000000.0, "In Progress"),
            ("PRJ014", "Global Legacy CRM Consolidation", "Application Replacement", "BU001", "2023-01-01", "2024-08-31", 250000000.0, 290000000.0, 300000000.0, "Completed"),  # Scenario F: Major benefit gap
            ("PRJ015", "API Gateway Mesh Evolution", "Infrastructure", "BU006", "2023-09-01", "2024-04-30", 45000000.0, 44000000.0, 14000000.0, "Completed"),
            ("PRJ016", "Digital Workplace Modernization", "Modernization", "BU007", "2024-03-01", "2024-12-31", 62000000.0, 61000000.0, 16000000.0, "In Progress"),
            ("PRJ017", "Regulatory Basel IV Reporting", "Regulatory", "BU010", "2023-04-01", "2024-07-31", 105000000.0, 109000000.0, 28000000.0, "Completed"),
            ("PRJ018", "Commercial Lending Automation", "Automation", "BU002", "2024-02-01", "2024-11-30", 82000000.0, 80000000.0, 25000000.0, "In Progress"),
            ("PRJ019", "Cyber Threat Intelligence Hub", "Infrastructure", "BU006", "2023-08-01", "2024-05-31", 76000000.0, 74000000.0, 20000000.0, "Completed"),
            ("PRJ020", "Wealth Management Advisory Portal", "Transformation", "BU003", "2023-12-01", "2024-10-31", 89000000.0, 93000000.0, 27000000.0, "Completed"),
            ("PRJ021", "Warehouse IoT Logistics Upgrade", "Infrastructure", "BU006", "2024-04-01", "2025-01-31", 52000000.0, 48000000.0, 12000000.0, "In Progress"),
            ("PRJ022", "Customer Data Platform 360", "AI", "BU001", "2024-01-01", "2024-11-30", 94000000.0, 91000000.0, 33000000.0, "In Progress"),
            ("PRJ023", "Mainframe Decommission Wave 1", "Application Replacement", "BU006", "2023-02-01", "2024-06-30", 115000000.0, 128000000.0, 40000000.0, "Completed"),
            ("PRJ024", "Branch Network Virtualization", "Infrastructure", "BU001", "2024-03-01", "2024-12-31", 68000000.0, 67000000.0, 19000000.0, "In Progress"),
            ("PRJ025", "Enterprise Document AI Extraction", "AI", "BU006", "2024-02-15", "2024-10-15", 48000000.0, 47000000.0, 15000000.0, "In Progress"),
            ("PRJ026", "Digital Onboarding Biometrics", "Transformation", "BU001", "2023-09-01", "2024-06-30", 64000000.0, 63000000.0, 22000000.0, "Completed"),
            ("PRJ027", "Automated AML Surveillance", "Regulatory", "BU010", "2023-11-01", "2024-09-30", 86000000.0, 89000000.0, 26000000.0, "Completed"),
            ("PRJ028", "Supplier Self-Service Portal", "Automation", "BU006", "2024-05-01", "2025-02-28", 38000000.0, 36000000.0, 9500000.0, "In Progress"),
            ("PRJ029", "Multi-Cloud FinOps Engine", "Modernization", "BU006", "2024-01-01", "2024-08-31", 42000000.0, 41000000.0, 18000000.0, "Completed"),
            ("PRJ030", "Cards Microservices Re-platform", "Modernization", "BU005", "2023-07-01", "2024-07-31", 125000000.0, 129000000.0, 39000000.0, "Completed"),
            ("PRJ031", "Continuous Security Compliance", "Infrastructure", "BU010", "2024-03-01", "2024-11-30", 56000000.0, 54000000.0, 14000000.0, "In Progress"),
            ("PRJ032", "Tax Automation Overhaul", "Regulatory", "BU007", "2024-02-01", "2024-09-30", 49000000.0, 51000000.0, 13000000.0, "Completed"),
            ("PRJ033", "Intelligent Sales Recommender", "AI", "BU002", "2024-04-01", "2024-12-31", 67000000.0, 65000000.0, 20000000.0, "In Progress"),
            ("PRJ034", "Logistics Visibility Control Tower", "Modernization", "BU006", "2023-10-01", "2024-08-31", 73000000.0, 76000000.0, 23000000.0, "Completed"),
            ("PRJ035", "Contact Center Cloud Migration", "Cloud Migration", "BU001", "2024-01-15", "2024-10-31", 81000000.0, 83000000.0, 24000000.0, "In Progress"),
            ("PRJ036", "Enterprise Asset Management Cloud", "Cloud Migration", "BU007", "2024-03-15", "2024-12-31", 44000000.0, 43000000.0, 11000000.0, "In Progress"),
            ("PRJ037", "Algorithmic Market Risk Analyzer", "Transformation", "BU009", "2023-08-01", "2024-07-31", 96000000.0, 98000000.0, 32000000.0, "Completed"),
            ("PRJ038", "Customer Feedback Sentiment AI", "AI", "BU001", "2024-06-01", "2025-01-31", 35000000.0, 32000000.0, 8000000.0, "In Progress"),
            ("PRJ039", "Insurance Underwriting Engine", "Modernization", "BU008", "2023-12-01", "2024-11-30", 87000000.0, 89000000.0, 27000000.0, "In Progress"),
            ("PRJ040", "NextGen Enterprise Integration Bus", "Infrastructure", "BU006", "2024-01-01", "2024-10-31", 69000000.0, 68000000.0, 21000000.0, "In Progress"),
        ]
        return pd.DataFrame(
            prj_data[: self.config.data.projects],
            columns=[
                "project_id",
                "project_name",
                "project_type",
                "sponsor_business_unit",
                "start_date",
                "end_date",
                "investment_budget",
                "actual_spend",
                "expected_annual_benefit",
                "status",
            ],
        )

    def generate_app_technology_relations(
        self, app_df: pd.DataFrame, tech_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Map applications to underlying technologies."""
        records = []
        tech_ids = tech_df["technology_id"].tolist()
        for app_id in app_df["application_id"]:
            # Pick 2-4 technologies deterministically per app
            app_num = int(app_id.replace("APP", ""))
            count = 2 + (app_num % 3)
            # Pick deterministically using modulo stride
            chosen_indices = [(app_num * 7 + i * 5) % len(tech_ids) for i in range(count)]
            for idx in set(chosen_indices):
                records.append({
                    "application_id": app_id,
                    "technology_id": tech_ids[idx],
                })
        return pd.DataFrame(records)

    def generate_app_capability_relations(
        self, app_df: pd.DataFrame, cap_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Map applications to capabilities, explicitly modeling Scenario C overlap."""
        records = []
        cap_ids = cap_df["capability_id"].tolist()

        # Deterministic primary mapping
        for idx, app_id in enumerate(app_df["application_id"]):
            cap_idx = idx % len(cap_ids)
            records.append({
                "application_id": app_id,
                "capability_id": cap_ids[cap_idx],
                "support_type": "Primary",
            })
            # Secondary capability mapping for some apps
            if idx % 3 == 0:
                sec_idx = (idx + 4) % len(cap_ids)
                records.append({
                    "application_id": app_id,
                    "capability_id": cap_ids[sec_idx],
                    "support_type": "Secondary",
                })

        # Explicit Scenario C: Duplicate capability overlap
        # CAP003 (Order-to-Cash) supported by APP005 (OrderFlow) and APP012 (QuickOrder Legacy)
        records.append({"application_id": "APP005", "capability_id": "CAP003", "support_type": "Primary"})
        records.append({"application_id": "APP012", "capability_id": "CAP003", "support_type": "Overlapping"})

        # CAP004 (Procure-to-Pay) supported by APP006 (SmartProcure) and APP018 (ProcureDirect Legacy)
        records.append({"application_id": "APP006", "capability_id": "CAP004", "support_type": "Primary"})
        records.append({"application_id": "APP018", "capability_id": "CAP004", "support_type": "Overlapping"})

        # Scenario B: APP021 supports CAP001 & CAP008 but overlaps with APP002 & APP011
        records.append({"application_id": "APP021", "capability_id": "CAP001", "support_type": "Overlapping"})

        df = pd.DataFrame(records).drop_duplicates(subset=["application_id", "capability_id"])
        return df

    def generate_app_dependencies(self, app_df: pd.DataFrame) -> pd.DataFrame:
        """Generate app-to-app dependencies with Scenario D single bottleneck."""
        records = []
        apps = app_df["application_id"].tolist()

        # Regular dependencies: 20-30 dependency edges
        for i in range(len(apps) - 1):
            if i % 2 == 0 and (i + 3) < len(apps):
                records.append({
                    "source_app_id": apps[i + 3],
                    "target_app_id": apps[i],
                    "dependency_type": "Synchronous API",
                    "criticality": "High",
                })

        # Scenario D: APP010 is a critical central identity/auth bottleneck
        # 8 applications directly depend on APP010
        dependent_apps = ["APP001", "APP002", "APP004", "APP005", "APP011", "APP013", "APP014", "APP023"]
        for dep_app in dependent_apps:
            if dep_app in apps and dep_app != "APP010":
                records.append({
                    "source_app_id": dep_app,
                    "target_app_id": "APP010",
                    "dependency_type": "Synchronous API",
                    "criticality": "Mission Critical",
                })

        df = pd.DataFrame(records).drop_duplicates(subset=["source_app_id", "target_app_id"])
        return df

    def generate_project_capability_relations(
        self, prj_df: pd.DataFrame, cap_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Map projects to targeted capabilities."""
        records = []
        cap_ids = cap_df["capability_id"].tolist()
        for idx, prj_id in enumerate(prj_df["project_id"]):
            cap_idx = (idx * 2) % len(cap_ids)
            records.append({
                "project_id": prj_id,
                "capability_id": cap_ids[cap_idx],
            })
            if idx % 2 == 1:
                cap_idx2 = (idx * 2 + 1) % len(cap_ids)
                records.append({
                    "project_id": prj_id,
                    "capability_id": cap_ids[cap_idx2],
                })
        return pd.DataFrame(records).drop_duplicates()

    def generate_app_project_relations(
        self, app_df: pd.DataFrame, prj_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Map applications funded by or transformed by projects."""
        records = []
        apps = app_df["application_id"].tolist()
        for idx, prj_id in enumerate(prj_df["project_id"]):
            app_idx = (idx * 3) % len(apps)
            records.append({
                "application_id": apps[app_idx],
                "project_id": prj_id,
                "relationship_type": "Funded/Modernized",
            })
        return pd.DataFrame(records).drop_duplicates()

    def generate_benefits(self, prj_df: pd.DataFrame) -> pd.DataFrame:
        """Generate benefit realization records including Scenario E and F."""
        benefit_types = [
            "Cost Reduction",
            "Productivity",
            "Revenue Enablement",
            "Risk Reduction",
            "Cycle Time Reduction",
            "Capacity Release",
            "Customer Experience",
        ]
        records = []
        b_idx = 1

        for _, prj in prj_df.iterrows():
            prj_id = prj["project_id"]
            expected_total = float(prj["expected_annual_benefit"])

            # Determine realized ratio based on scenario or general seed
            if prj_id == "PRJ003":
                # Scenario E: High realization (>100%)
                ratio = 1.08
                status = "Exceeded"
            elif prj_id == "PRJ014":
                # Scenario F: Benefit gap (<25%)
                ratio = 0.233
                status = "Unrealized"
            elif prj["status"] == "Completed":
                ratio = self.rng.uniform(0.75, 1.05)
                status = "Realized" if ratio >= 0.90 else "Partially Realized"
            else:
                ratio = self.rng.uniform(0.20, 0.60)
                status = "In Progress"

            realized_total = round(expected_total * ratio, 2)

            # Generate 2 benefit lines per project
            b_type1 = benefit_types[(b_idx) % len(benefit_types)]
            b_type2 = benefit_types[(b_idx + 2) % len(benefit_types)]

            exp_1 = round(expected_total * 0.60, 2)
            exp_2 = round(expected_total * 0.40, 2)
            rel_1 = round(realized_total * 0.60, 2)
            rel_2 = round(realized_total * 0.40, 2)

            records.append({
                "benefit_id": f"BEN{b_idx:03d}",
                "project_id": prj_id,
                "benefit_type": b_type1,
                "expected_value": exp_1,
                "realized_value": rel_1,
                "measurement_period": f"FY{self.year}-Annual",
                "benefit_status": status,
            })
            b_idx += 1

            records.append({
                "benefit_id": f"BEN{b_idx:03d}",
                "project_id": prj_id,
                "benefit_type": b_type2,
                "expected_value": exp_2,
                "realized_value": rel_2,
                "measurement_period": f"FY{self.year}-Annual",
                "benefit_status": status,
            })
            b_idx += 1

        return pd.DataFrame(records)

    def generate_kpis(self) -> pd.DataFrame:
        """Generate organizational and operational KPI catalog."""
        kpi_defs = [
            ("KPI001", "Cost per Digital Transaction", "Financial", 4.25, 2.80, 2.65, "₹"),
            ("KPI002", "Average Incident Resolution Time", "Operational", 180.0, 60.0, 72.0, "Minutes"),
            ("KPI003", "Order Cycle Time", "Operational", 48.0, 12.0, 14.5, "Hours"),
            ("KPI004", "Procure-to-Pay Processing Time", "Operational", 14.0, 3.0, 3.5, "Days"),
            ("KPI005", "Digital Channel Adoption Rate", "Customer", 52.0, 85.0, 88.5, "%"),
            ("KPI006", "Process Automation Rate", "Operational", 35.0, 75.0, 71.0, "%"),
            ("KPI007", "Core Banking Availability", "Reliability", 99.80, 99.99, 99.98, "%"),
            ("KPI008", "Customer Support First-Call Resolution", "Customer", 64.0, 85.0, 82.0, "%"),
            ("KPI009", "Loan Origination Turnaround Time", "Operational", 72.0, 4.0, 5.2, "Hours"),
            ("KPI010", "Fraud Detection Accuracy Rate", "Agility", 84.0, 98.0, 97.4, "%"),
            ("KPI011", "Claims Processing Cycle Time", "Operational", 120.0, 24.0, 28.0, "Hours"),
            ("KPI012", "API Endpoint Response Latency", "Reliability", 450.0, 80.0, 85.0, "ms"),
            ("KPI013", "Cloud Resource Cost Efficiency Index", "Financial", 65.0, 90.0, 86.5, "%"),
            ("KPI014", "Identity Verification Pass Rate", "Customer", 78.0, 96.0, 95.2, "%"),
            ("KPI015", "Monthly Data Lake Ingestion Volume", "Agility", 120.0, 500.0, 480.0, "TB"),
        ]
        return pd.DataFrame(
            kpi_defs,
            columns=[
                "kpi_id",
                "kpi_name",
                "kpi_category",
                "baseline_value",
                "target_value",
                "actual_value",
                "unit",
            ],
        )

    def generate_benefit_kpi_relations(
        self, ben_df: pd.DataFrame, kpi_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Map benefits to governing KPIs."""
        records = []
        kpis = kpi_df["kpi_id"].tolist()
        for idx, b_id in enumerate(ben_df["benefit_id"]):
            kpi_id = kpis[idx % len(kpis)]
            records.append({
                "benefit_id": b_id,
                "kpi_id": kpi_id,
                "weight": 1.0,
            })
        return pd.DataFrame(records)

    def generate_cost_records(
        self,
        app_df: pd.DataFrame,
        srv_df: pd.DataFrame,
        bu_df: pd.DataFrame,
        ven_df: pd.DataFrame,
        prj_df: pd.DataFrame,
        rel_app_cap: pd.DataFrame,
    ) -> pd.DataFrame:
        """Generate monthly cost ledger records embedding explicit scenarios."""
        cost_pools = [
            "Internal Labor",
            "External Labor",
            "Software",
            "Hardware",
            "Telecom",
            "Outside Services",
            "Facilities",
        ]
        cost_categories = [
            "People",
            "Software",
            "Hardware",
            "Cloud",
            "Infrastructure",
            "Network",
            "External Services",
            "Security",
            "Data",
            "Support",
        ]

        records = []
        cost_id_counter = 1

        apps = app_df.to_dict("records")
        services = srv_df["service_id"].tolist()
        b_units = bu_df["business_unit_id"].tolist()
        vendors = ven_df["vendor_id"].tolist()
        projects = prj_df["project_id"].tolist()

        for month_idx, month in enumerate(self.months, start=1):
            # 1. Direct Application Monthly Costs
            for app in apps:
                app_id = app["application_id"]
                srv_id = app["service_id"]
                license_annual = app["annual_license_cost"]
                base_monthly = license_annual / 12.0

                # Scenario A: APP001 is expensive & highly utilized
                if app_id == "APP001":
                    base_monthly = 12500000.0  # ₹1.25 Cr / mo

                # Scenario B: APP021 is expensive & underutilized
                elif app_id == "APP021":
                    base_monthly = 7000000.0  # ₹70 Lakh / mo

                # Scenario G: APP014 cost surges in August onwards driven by cloud usage
                elif app_id == "APP014":
                    if month_idx < 8:
                        base_monthly = 3500000.0
                    else:
                        base_monthly = 9500000.0 + (month_idx - 8) * 800000.0

                # Scenario H: APP022 cost surges in August onwards WITHOUT consumption growth
                elif app_id == "APP022":
                    if month_idx < 8:
                        base_monthly = 2000000.0
                    else:
                        base_monthly = 5800000.0  # sudden +₹38 Lakh jump

                # Primary application costs across categories
                # Software / License
                app_num = int(app_id.replace("APP", ""))
                ven_id = vendors[app_num % len(vendors)]
                bu_id = b_units[app_num % len(b_units)]

                records.append({
                    "cost_id": f"CST{cost_id_counter:05d}",
                    "month": month,
                    "cost_center": f"CC{100 + (app_num % 10)}",
                    "cost_pool": "Software",
                    "cost_category": "Software",
                    "amount": round(base_monthly * 0.45, 2),
                    "application_id": app_id,
                    "service_id": srv_id,
                    "business_unit_id": bu_id,
                    "vendor_id": ven_id,
                    "project_id": projects[app_num % len(projects)] if app_num % 4 == 0 else None,
                })
                cost_id_counter += 1

                # People / Support
                records.append({
                    "cost_id": f"CST{cost_id_counter:05d}",
                    "month": month,
                    "cost_center": f"CC{100 + (app_num % 10)}",
                    "cost_pool": "Internal Labor",
                    "cost_category": "People",
                    "amount": round(base_monthly * 0.30, 2),
                    "application_id": app_id,
                    "service_id": srv_id,
                    "business_unit_id": bu_id,
                    "vendor_id": None,
                    "project_id": None,
                })
                cost_id_counter += 1

                # Cloud / Infrastructure
                cat = "Cloud" if app["application_type"] in ["Custom Built", "Hybrid"] else "Infrastructure"
                records.append({
                    "cost_id": f"CST{cost_id_counter:05d}",
                    "month": month,
                    "cost_center": f"CC{100 + (app_num % 10)}",
                    "cost_pool": "Outside Services",
                    "cost_category": cat,
                    "amount": round(base_monthly * 0.25, 2),
                    "application_id": app_id,
                    "service_id": srv_id,
                    "business_unit_id": bu_id,
                    "vendor_id": ven_id,
                    "project_id": None,
                })
                cost_id_counter += 1

            # 2. Shared IT Service & Infrastructure Costs (Non-app specific)
            for s_idx, srv_id in enumerate(services):
                records.append({
                    "cost_id": f"CST{cost_id_counter:05d}",
                    "month": month,
                    "cost_center": f"CC{200 + s_idx}",
                    "cost_pool": "Outside Services",
                    "cost_category": "Infrastructure",
                    "amount": round(1500000.0 + (s_idx * 120000.0), 2),
                    "application_id": None,
                    "service_id": srv_id,
                    "business_unit_id": "BU006",
                    "vendor_id": vendors[s_idx % len(vendors)],
                    "project_id": None,
                })
                cost_id_counter += 1

        return pd.DataFrame(records)

    def generate_consumption_records(
        self, app_df: pd.DataFrame, bu_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate monthly consumption records embedding explicit scenarios."""
        records = []
        c_id_counter = 1
        apps = app_df["application_id"].tolist()
        b_units = bu_df["business_unit_id"].tolist()

        for month_idx, month in enumerate(self.months, start=1):
            for app_id in apps:
                app_num = int(app_id.replace("APP", ""))

                # Assign 1 to 2 consuming BUs
                consuming_bus = [b_units[app_num % len(b_units)]]
                if app_num % 3 == 0:
                    consuming_bus.append(b_units[(app_num + 2) % len(b_units)])

                for bu_id in consuming_bus:
                    # Scenario A: APP001 - Very high users and transactions
                    if app_id == "APP001":
                        users = 8500 + int(self.rng.normal(200, 50))
                        txns = 6500000 + int(self.rng.normal(200000, 30000))
                        api_calls = 25000000 + int(self.rng.normal(1000000, 100000))
                        compute = 4200.0 + self.rng.normal(100, 20)
                        storage = 8500.0
                        tickets = 45

                    # Scenario B: APP021 - High cost, LOW users and transactions
                    elif app_id == "APP021":
                        users = 145 + int(self.rng.normal(10, 3))
                        txns = 12000 + int(self.rng.normal(1000, 200))
                        api_calls = 45000 + int(self.rng.normal(3000, 500))
                        compute = 650.0
                        storage = 1200.0
                        tickets = 68

                    # Scenario G: APP014 - Consumption surges in August onwards
                    elif app_id == "APP014":
                        multiplier = 1.0 if month_idx < 8 else (1.0 + (month_idx - 7) * 0.45)
                        users = int((3200 + self.rng.normal(100, 20)) * multiplier)
                        txns = int((1800000 + self.rng.normal(50000, 10000)) * multiplier)
                        api_calls = int((8500000 + self.rng.normal(200000, 30000)) * multiplier)
                        compute = round((1800.0 + self.rng.normal(50, 10)) * multiplier, 1)
                        storage = round(2400.0 * multiplier, 1)
                        tickets = int(35 * multiplier)

                    # Scenario H: APP022 - Consumption remains flat despite cost jump
                    elif app_id == "APP022":
                        users = 520 + int(self.rng.normal(15, 5))
                        txns = 420000 + int(self.rng.normal(8000, 1000))
                        api_calls = 950000 + int(self.rng.normal(20000, 3000))
                        compute = 980.0
                        storage = 3100.0
                        tickets = 28

                    # Standard application consumption
                    else:
                        base_u = 400 + (app_num * 65) % 2500
                        users = max(20, int(base_u + self.rng.normal(0, 20)))
                        txns = max(1000, int(users * (150 + (app_num * 17) % 300)))
                        api_calls = int(txns * (2.5 + (app_num % 5)))
                        compute = round(150.0 + (app_num * 45) % 1200, 1)
                        storage = round(200.0 + (app_num * 80) % 3000, 1)
                        tickets = max(2, int(users * 0.015))

                    records.append({
                        "consumption_id": f"CON{c_id_counter:06d}",
                        "month": month,
                        "application_id": app_id,
                        "business_unit_id": bu_id,
                        "active_users": users,
                        "transactions": txns,
                        "api_calls": api_calls,
                        "compute_hours": compute,
                        "storage_gb": storage,
                        "tickets": tickets,
                    })
                    c_id_counter += 1

        return pd.DataFrame(records)
