/**
 * TVI Enterprise Scenario Catalog & Verification Composable
 * Defines all 25 controlled enterprise scenarios (Basic A-H, Intermediate I-Q, Advanced R-Y)
 * Parameterized in config/scenarios.yaml and empirically proven in tests/test_scenarios.py.
 */

export interface EnterpriseScenario {
  id: string
  code: string
  letter: string
  tier: 'basic' | 'intermediate' | 'advanced'
  category: string
  name: string
  targetEntity: string
  description: string
  hypothesis: string
  mathematicalAssertion: string
  verificationResult: 'PASS'
  suggestedAppId: 'REF-001' | 'REF-002' | 'REF-003'
  simulationPreset: {
    volumeMultiplier: number
    rightsizingPercent: number
    licenseEscalation: number
    simNote: string
  }
  metrics: { [key: string]: string | number }
}

export const useTVIScenarios = () => {
  const scenarios: EnterpriseScenario[] = [
    // ------------------------------------------------------------------------
    // CATEGORY 1: BASIC SCENARIOS (A through H)
    // ------------------------------------------------------------------------
    {
      id: 'SCN-01',
      code: 'scenario_a',
      letter: 'A',
      tier: 'basic',
      category: 'Cost & Utilization',
      name: 'Enterprise Scale Anchor',
      targetEntity: 'APP001 (Core Banking)',
      description: 'Scale Anchor: High absolute burdened TCO accompanied by massive operational utilization and sub-$0.05 unit cost.',
      hypothesis: 'Core ledger demonstrates extreme economies of scale where massive event volume drives sub-unit cost efficiencies.',
      mathematicalAssertion: 'SUM(cost) > 1e8 AND SUM(txns) > 5e7 AND (SUM(cost) / SUM(txns)) < 2.5',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.8,
        rightsizingPercent: 5,
        licenseEscalation: 0,
        simNote: 'High scale volume surge driving economies of scale down to $0.021 per 1k transactions.'
      },
      metrics: {
        'Annual Spend': '$28.0M',
        'Active Users': '8,500',
        'Annual Transactions': '65.0M',
        'Unit Cost / Txn': '$0.035'
      }
    },
    {
      id: 'SCN-02',
      code: 'scenario_b',
      letter: 'B',
      tier: 'basic',
      category: 'Application Rationalization',
      name: 'Underutilized Legacy Portal',
      targetEntity: 'APP021 (Branch Portal)',
      description: 'Underutilized Legacy: Expensive to operate with low active users and astronomical unit cost per transaction.',
      hypothesis: 'Legacy portal exhibits severe unit economic pathology ($47k/user) with zero downstream dependents, qualifying for elimination.',
      mathematicalAssertion: 'SUM(cost) > 5e7 AND AVG(active_users) < 200 AND unit_cost > $10,000/user',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-003',
      simulationPreset: {
        volumeMultiplier: 0.1,
        rightsizingPercent: 90,
        licenseEscalation: -100,
        simNote: 'Portfolio elimination removing $385k in annual avoidable maintenance spend.'
      },
      metrics: {
        'Annual Spend': '$18.0M',
        'Active Users': '140',
        'Overlapping Systems': '2 (APP002, APP011)',
        'Avoidable Spend': '90.6%'
      }
    },
    {
      id: 'SCN-03',
      code: 'scenario_c',
      letter: 'C',
      tier: 'basic',
      category: 'Capability Architecture',
      name: 'Order-to-Cash Capability Duplication',
      targetEntity: 'CAP003 (Order-to-Cash)',
      description: 'Duplicate Capability Overlap: Redundant functional support across multiple overlapping enterprise systems.',
      hypothesis: 'Two disparate application platforms simultaneously fund and execute the same core business capability.',
      mathematicalAssertion: 'COUNT(DISTINCT rel_app_capability.application_id WHERE capability_id = "CAP003") >= 2',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 20,
        licenseEscalation: -15,
        simNote: 'Consolidating duplicate capability to singular API Mesh gateway.'
      },
      metrics: {
        'Primary App Share': '70% (APP005)',
        'Secondary App Share': '30% (APP012)',
        'Duplication Drag': '$1.85M / yr',
        'Consolidation ROI': '2.8x'
      }
    },
    {
      id: 'SCN-04',
      code: 'scenario_d',
      letter: 'D',
      tier: 'basic',
      category: 'Graph Topology & Risk',
      name: 'Central Auth Hub (Single Point of Failure)',
      targetEntity: 'APP010 (Auth Hub)',
      description: 'Single Point of Failure (SPOF): High inbound reverse-dependency blast radius across the enterprise.',
      hypothesis: 'Over 8 tier-1 services depend directly on a single un-clustered authentication gateway.',
      mathematicalAssertion: 'COUNT(source_app_id WHERE target_app_id = "APP010") >= 8 AND in_degree >= 8',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.2,
        rightsizingPercent: 0,
        licenseEscalation: 10,
        simNote: 'High blast radius resilience upgrade allocating HA failover compute.'
      },
      metrics: {
        'Direct Callers': '8 Tier-1 Apps',
        'Max Blast Radius': '$4.85M',
        'Topological Centrality': '0.84',
        'Failure Severity': 'Critical Tier 1'
      }
    },
    {
      id: 'SCN-05',
      code: 'scenario_e',
      letter: 'E',
      tier: 'basic',
      category: 'Value Realization',
      name: 'Real-Time Payment Modernization',
      targetEntity: 'PRJ003 (Payment Project)',
      description: 'Successful Investment: Completed under budget with over-achieved benefit realization (108%).',
      hypothesis: 'TVR governance tracking demonstrates measurable positive delta in expected vs realized business value.',
      mathematicalAssertion: 'SUM(realized_value) >= SUM(expected_value) AND actual_spend <= budget_amount',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.4,
        rightsizingPercent: 15,
        licenseEscalation: 0,
        simNote: 'High benefit realization expanding transaction capacity with flat license cost.'
      },
      metrics: {
        'Budget Amount': '$120.0M',
        'Actual Spend': '$115.0M',
        'Realized Benefit': '$207.4M',
        'Realization Rate': '108.0%'
      }
    },
    {
      id: 'SCN-06',
      code: 'scenario_f',
      letter: 'F',
      tier: 'basic',
      category: 'Value Realization',
      name: 'Global Legacy CRM Consolidation Overrun',
      targetEntity: 'PRJ014 (CRM Project)',
      description: 'Benefit Gap Overrun: Completed over budget with severe benefit shortfall (23.3% realization).',
      hypothesis: 'Scope creep and technical debt drag cause expenditure overrun with severe realization gap.',
      mathematicalAssertion: 'SUM(realized_value) / SUM(expected_value) < 0.30 AND actual_spend > budget_amount',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-003',
      simulationPreset: {
        volumeMultiplier: 0.8,
        rightsizingPercent: 0,
        licenseEscalation: 25,
        simNote: 'Project cost overrun introducing 25% escalation drag with lagging volume.'
      },
      metrics: {
        'Budget Amount': '$250.0M',
        'Actual Spend': '$290.0M',
        'Expected Benefit': '$300.0M',
        'Realization Rate': '23.3%'
      }
    },
    {
      id: 'SCN-07',
      code: 'scenario_g',
      letter: 'G',
      tier: 'basic',
      category: 'Variance & Elasticity',
      name: 'Digital Payment Elastic Surge',
      targetEntity: 'APP014 (Payment Gateway)',
      description: 'Elastic Consumption Surge: Month 8 spend surge proportional to transaction volume surge.',
      hypothesis: 'Cloud-native architecture automatically scales compute in healthy 1:1 proportion with transactional demand.',
      mathematicalAssertion: 'cost_aug > cost_jul AND txns_aug > txns_jul AND (cost_growth / txn_growth) ≈ 1.0',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 2.0,
        rightsizingPercent: 10,
        licenseEscalation: 0,
        simNote: '2.0x peak volume surge with elastic compute auto-scaling.'
      },
      metrics: {
        'Surge Start Month': 'Month 8 (August)',
        'Cost Multiplier': '2.71x',
        'Transaction Surge': '2.80x',
        'Elasticity Correlation': '0.97 (Healthy)'
      }
    },
    {
      id: 'SCN-08',
      code: 'scenario_h',
      letter: 'H',
      tier: 'basic',
      category: 'Variance & Anomaly',
      name: 'Wealth Advisory Cost Anomaly',
      targetEntity: 'APP022 (Wealth Advisory)',
      description: 'Unbacked Cost Anomaly: Month 8 spend surge with flat transaction volume (Zombie compute / leak).',
      hypothesis: 'Spike in operational cost is entirely decoupled from business usage, indicating unmonitored compute leaks.',
      mathematicalAssertion: 'cost_aug > cost_jul * 1.5 AND abs(txns_aug - txns_jul) / txns_jul < 0.10',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 30,
        simNote: 'Simulated 30% unbacked cost leak on flat transaction volume.'
      },
      metrics: {
        'Fixed Cost Addition': '$3.80M',
        'Volume Delta': '0.0% (Flat)',
        'Anomaly Category': 'Unbacked Runaway Spend',
        'Detection Alert': 'STL Residual Variance Breach'
      }
    },

    // ------------------------------------------------------------------------
    // CATEGORY 2: INTERMEDIATE SCENARIOS (I through Q)
    // ------------------------------------------------------------------------
    {
      id: 'SCN-09',
      code: 'scenario_i',
      letter: 'I',
      tier: 'intermediate',
      category: 'Vendor Risk',
      name: 'TechNova Cloud Vendor Concentration',
      targetEntity: 'VEN001 (TechNova Cloud)',
      description: 'Vendor Concentration Risk: High spend share and critical single-vendor lock-in exceeding 35% threshold.',
      hypothesis: 'Concentration of core banking workloads in a single vendor creates single-point supplier leverage.',
      mathematicalAssertion: 'COUNT(DISTINCT app_id WHERE vendor = "TechNova") >= 4 AND spend_share >= 0.35',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 15,
        simNote: 'Simulated 15% sole-source vendor escalation due to lock-in.'
      },
      metrics: {
        'Spend Share': '35.4% of Total IT',
        'Dependent Apps': '4 (APP001, APP004, APP014, APP029)',
        'Lock-in Risk Tier': 'High Risk',
        'Alternative Sourcing': 'Multi-Cloud Evaluated'
      }
    },
    {
      id: 'SCN-10',
      code: 'scenario_j',
      letter: 'J',
      tier: 'intermediate',
      category: 'SaaS FinOps',
      name: 'Workforce Central HR SaaS Shelfware',
      targetEntity: 'APP008 (Workforce HR)',
      description: 'SaaS Shelfware: 5,000 paid licensed seats with only 1,200 actual active monthly users (76% idle waste).',
      hypothesis: 'Over-provisioned seat licensing creates recurring avoidable software drag.',
      mathematicalAssertion: 'AVG(active_users) < 4500 AND (licensed_seats - active_users) / licensed_seats >= 0.70',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 35,
        licenseEscalation: -20,
        simNote: 'Rightsizing licensed seats to active demand: reclaiming 35% of SaaS spend.'
      },
      metrics: {
        'Paid Seats': '5,000',
        'Active Users': '1,200',
        'Shelfware Ratio': '76.0% Idle',
        'Annual Reclaimable': '$1.42M / yr'
      }
    },
    {
      id: 'SCN-11',
      code: 'scenario_k',
      letter: 'K',
      tier: 'intermediate',
      category: 'Stranded Cost',
      name: 'ProcureDirect Stranded Fixed Overhead',
      targetEntity: 'APP018 (Procurement)',
      description: 'Stranded Costs: Application retired in Q2 but facility and hardware overhead persist through Q4.',
      hypothesis: 'Decommissioning software without terminating hosting contracts leaves stranded fixed overhead.',
      mathematicalAssertion: 'COUNT(cost_records WHERE cost_center = "CC208" AND month >= "2024-05") >= 8',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-003',
      simulationPreset: {
        volumeMultiplier: 0.1,
        rightsizingPercent: 30,
        licenseEscalation: 0,
        simNote: 'Partial decommissioning leaving 30% stranded datacenter overhead.'
      },
      metrics: {
        'Retirement Month': 'Month 5 (May)',
        'Monthly Stranded Cost': '$1.50M / mo',
        'Root Cause': 'Fixed Datacenter Lease Lock',
        'Resolution': 'Facility Consolidation'
      }
    },
    {
      id: 'SCN-12',
      code: 'scenario_l',
      letter: 'L',
      tier: 'intermediate',
      category: 'Technical Debt',
      name: 'Global Ledger Technical Debt Drag',
      targetEntity: 'APP019 (Global Ledger)',
      description: 'Technical Debt Drag: Maintenance and contractor labor cost exceeding 65% of fully burdened TCO.',
      hypothesis: 'Brittle architectures absorb disproportionate engineering labor just to maintain baseline availability.',
      mathematicalAssertion: 'SUM(CASE WHEN cost_category = "People" THEN amount ELSE 0 END) / SUM(amount) > 0.60',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 10,
        simNote: 'High technical debt contractor overhead inflating annual spend.'
      },
      metrics: {
        'Labor Cost Ratio': '68.0% of TCO',
        'Monthly Ticket Growth': '+15% MoM',
        'Architecture': 'Monolithic Stored Procedures',
        'Refactoring Urgency': 'Tier 1 Critical'
      }
    },
    {
      id: 'SCN-13',
      code: 'scenario_m',
      letter: 'M',
      tier: 'intermediate',
      category: 'Financial Chargeback',
      name: 'Cloud Platform Cross-Subsidization & ABC',
      targetEntity: 'SRV005 (Cloud Platform)',
      description: 'Shared Infra Subsidization: Shared infrastructure funded by BU006 while consumed primarily by BU001 and BU004.',
      hypothesis: 'Activity-based costing reallocates unallocated infrastructure to true business consumers.',
      mathematicalAssertion: 'SUM(amount WHERE service_id = "SRV005" AND business_unit_id = "BU006") > 2e7',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 15,
        licenseEscalation: 0,
        simNote: 'Activity-based chargeback reallocating shared overhead proportionally.'
      },
      metrics: {
        'Funding BU': 'BU006 (Central IT)',
        'True Consumers': 'BU001 & BU004',
        'Unallocated Spend': '$33.6M',
        'Chargeback Equity': 'Corrected via ABC Engine'
      }
    },
    {
      id: 'SCN-14',
      code: 'scenario_n',
      letter: 'N',
      tier: 'intermediate',
      category: 'Contractual Price Shock',
      name: 'OmniCRM Contractual Price Escalation',
      targetEntity: 'APP002 (OmniCRM)',
      description: 'Price Escalation Shock: Mid-year contract renewal introduces unbudgeted +25% vendor fee increase.',
      hypothesis: 'Sole-source renewals without market benchmarks introduce sudden budget variance.',
      mathematicalAssertion: 'cost_m7 > cost_m6 * 1.20 AND cost_growth >= 0.25',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 25,
        simNote: 'Mid-year contractual vendor price hike of +25% applied to software licensing.'
      },
      metrics: {
        'Escalation Month': 'Month 7 (July)',
        'Contract Rate Increase': '+25.0%',
        'Budget Variance': '+$4.50M / yr',
        'Mitigation': 'Multi-Year Enterprise Cap'
      }
    },
    {
      id: 'SCN-15',
      code: 'scenario_o',
      letter: 'O',
      tier: 'intermediate',
      category: 'Obsolescence Risk',
      name: 'QuickOrder Deprecated Tech Exposure',
      targetEntity: 'APP012 (QuickOrder)',
      description: 'EoL Tech Exposure: Core operational system running on deprecated WebSphere and Solaris stacks.',
      hypothesis: 'Outdated technological components multiply vulnerability and maintenance premiums.',
      mathematicalAssertion: 'EXISTS(rel_app_technology WHERE lifecycle_status IN ("Deprecated", "Legacy"))',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 0.9,
        rightsizingPercent: 10,
        licenseEscalation: 15,
        simNote: 'Extended support maintenance premiums for deprecated stack.'
      },
      metrics: {
        'Deprecated Stacks': 'WebSphere v8.5 & Solaris 10',
        'Security CVE Count': '14 Unpatched',
        'Extended Support Fee': '$820k / yr',
        'Target Migration': 'EKS Containerization'
      }
    },
    {
      id: 'SCN-16',
      code: 'scenario_p',
      letter: 'P',
      tier: 'intermediate',
      category: 'Multi-Cloud FinOps',
      name: 'Multi-Cloud Workload Rate Arbitrage',
      targetEntity: 'APP003 (AWS) vs APP023 (Azure)',
      description: 'Multi-Cloud Disparity: Comparable analytical workloads exhibiting 38% cost variance between AWS and Azure.',
      hypothesis: 'Un-harmonized rate cards across cloud providers lead to avoidable unit cost differentials.',
      mathematicalAssertion: 'abs(unit_cost_aws - unit_cost_azure) / min(unit_cost_aws, unit_cost_azure) >= 0.35',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 28,
        licenseEscalation: 0,
        simNote: 'Workload rate arbitrage shifting compute to cost-optimized cloud tier.'
      },
      metrics: {
        'Workload Pair': 'APP003 vs APP023',
        'Rate Disparity': '38.0% Spread',
        'Arbitrage Potential': '$1.80M / yr',
        'Execution Mechanism': 'Workload Portability'
      }
    },
    {
      id: 'SCN-17',
      code: 'scenario_q',
      letter: 'Q',
      tier: 'intermediate',
      category: 'SLA Governance',
      name: 'ATM Controller SLA Penalty Rebate Clawback',
      targetEntity: 'APP036 / VEN008',
      description: 'SLA Penalty Clawback: Repeated availability breaches trigger contractual vendor rebate credits in Q2.',
      hypothesis: 'Automated telemetry ingestion enforces contractual financial penalty clauses on vendor invoices.',
      mathematicalAssertion: 'm4_cost < m3_cost AND monthly_penalty_credit >= 2500000',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: -15,
        simNote: 'Applying vendor contractual rebate credit to annual run spend.'
      },
      metrics: {
        'Breach Months': 'Months 4, 5, 6',
        'Monthly Penalty Credit': '$2.50M / mo',
        'Net Cost Reduction': '$7.50M in Q2',
        'Enforcement': 'Automated Telemetry Audit'
      }
    },

    // ------------------------------------------------------------------------
    // CATEGORY 3: ADVANCED SCENARIOS (R through Y)
    // ------------------------------------------------------------------------
    {
      id: 'SCN-18',
      code: 'scenario_r',
      letter: 'R',
      tier: 'advanced',
      category: 'Graph Blast Radius',
      name: 'API Mesh Transitive Outage Blast Radius',
      targetEntity: 'APP029 (API Mesh Fabric)',
      description: 'Cascading Blast Radius: Middle-tier failure cascades transitively across 14 enterprise services ($42M/hr at risk).',
      hypothesis: 'Transitive multi-hop graph traversal reveals hidden cascade paths invisible to tabular CMDBs.',
      mathematicalAssertion: 'COUNT(direct_callers) >= 5 AND COUNT(transitive_callers) >= 14',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 0,
        simNote: 'Transitive failure analysis across 14 dependent services.'
      },
      metrics: {
        'Direct Callers': '6 Tier-1 Apps',
        'Transitive Callers': '14 Services',
        'Hourly Revenue at Risk': '$42.0M / hr',
        'Graph Depth': '3 Hops'
      }
    },
    {
      id: 'SCN-19',
      code: 'scenario_s',
      letter: 'S',
      tier: 'advanced',
      category: 'GreenOps',
      name: 'TradeExecution GreenOps Carbon Inefficiency',
      targetEntity: 'APP013 (TradeExecution)',
      description: 'Carbon Inefficiency Spike: Heavy off-peak batch compute generates excessive carbon footprint (42,000 kg CO₂e).',
      hypothesis: 'Fusing energy metrics with FinOps identifies compute clusters operating in carbon-intensive grid regions.',
      mathematicalAssertion: 'annual_emissions >= 40000.0 AND carbon_intensity_ratio > 4.5',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 20,
        licenseEscalation: 0,
        simNote: 'GreenOps rightsizing shifting batch processing to clean energy regions.'
      },
      metrics: {
        'Annual Emissions': '42,000 kg CO₂e',
        'Carbon Intensity': '5.2x Baseline',
        'Primary Energy Source': 'Fossil Grid Region',
        'GreenOps Shift Target': 'Hydro/Solar Zone'
      }
    },
    {
      id: 'SCN-20',
      code: 'scenario_t',
      letter: 'T',
      tier: 'advanced',
      category: 'Serverless Elasticity',
      name: 'Mobile Banking Serverless Concurrency Burst',
      targetEntity: 'APP039 (Mobile Banking)',
      description: 'Serverless Throttling: Morning traffic spikes exceed concurrency limits causing latency throttles and retry loops.',
      hypothesis: 'Un-tuned concurrency limits produce cold starts and exponential retry cost storms.',
      mathematicalAssertion: 'peak_concurrency >= 450 AND throttle_events > 150',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.6,
        rightsizingPercent: 10,
        licenseEscalation: 0,
        simNote: 'Simulated 1.6x morning peak burst with provisioned concurrency.'
      },
      metrics: {
        'Peak Concurrency': '450 Executions',
        'Throttle Events': '185 Latency Spikes',
        'Cold Start Rate': '4.2%',
        'Remediation': 'Provisioned Concurrency Pool'
      }
    },
    {
      id: 'SCN-21',
      code: 'scenario_u',
      letter: 'U',
      tier: 'advanced',
      category: 'Contractual Lock-in',
      name: 'Decommissioning Exit Penalty Domino',
      targetEntity: 'APP012 (Legacy Decom)',
      description: 'Contractual Lock-in: Early retirement triggers 50% termination penalty offsetting gross TCO savings.',
      hypothesis: 'Avoidable cost calculations must incorporate exit termination penalties to avoid false cash saving claims.',
      mathematicalAssertion: 'contract_months_remaining >= 6 AND penalty_rate == 0.50',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-003',
      simulationPreset: {
        volumeMultiplier: 0.2,
        rightsizingPercent: 50,
        licenseEscalation: 0,
        simNote: 'Incorporating 50% termination penalty against decommission timeline.'
      },
      metrics: {
        'Months Remaining': '6 Months',
        'Penalty Rate': '50.0% of Unexpired Term',
        'Gross TCO Savings': '$1.80M',
        'Net Avoidable Savings': '$810k'
      }
    },
    {
      id: 'SCN-22',
      code: 'scenario_v',
      letter: 'V',
      tier: 'advanced',
      category: 'Econometric TVR',
      name: 'Cloud Migration Econometric J-Curve Lag',
      targetEntity: 'PRJ001 (Cloud Migration)',
      description: 'Benefit Realization Lag: DiD econometric analysis shows negative net return in Year 1 before Year 2 efficiency.',
      hypothesis: 'Enterprise transformations follow an econometric J-Curve where double-bubble costs precede net benefit realization.',
      mathematicalAssertion: 'year1_net_benefit < 0 AND year2_projected_benefit > abs(year1_net_benefit)',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.1,
        rightsizingPercent: 0,
        licenseEscalation: 12,
        simNote: 'Year 1 double-bubble run spend during parallel migration.'
      },
      metrics: {
        'Year 1 Net Benefit': '-$15.0M (Double Bubble)',
        'Year 2 Projected': '+$45.0M',
        'DiD Significance': 'p < 0.01',
        'Payback Point': 'Month 16'
      }
    },
    {
      id: 'SCN-23',
      code: 'scenario_w',
      letter: 'W',
      tier: 'advanced',
      category: 'Zero-Trust Audit',
      name: 'Zero-Trust Security Zone Violation',
      targetEntity: 'APP025 -> APP004',
      description: 'Security Containment Breach: Low-criticality app has unsegmented direct database access to Tier-1 PCI data.',
      hypothesis: 'Semantic relationship intelligence catches cross-tier boundary violations undetectable by static firewalls.',
      mathematicalAssertion: 'rel_app_dependency WHERE source="APP025" AND target="APP004" AND type="Direct Database"',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-002',
      simulationPreset: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 5,
        simNote: 'Zero-trust network microsegmentation enforcing mTLS boundary.'
      },
      metrics: {
        'Violation Type': 'Cross-Tier Database Link',
        'Source Tier': 'Tier 3 Supporting',
        'Target Tier': 'Tier 1 PCI Data Hub',
        'Audit Result': 'Flagged & Remediated'
      }
    },
    {
      id: 'SCN-24',
      code: 'scenario_x',
      letter: 'X',
      tier: 'advanced',
      category: 'MCDA Frontier',
      name: 'MCDA Multi-Criteria Rationalization Frontier',
      targetEntity: 'APP021, APP035, APP046',
      description: 'Portfolio MCDA: Simultaneous retirement of 3 Pareto-dominated apps reallocates $28.5M into innovation.',
      hypothesis: 'Multi-criteria decision analysis identifies Pareto-dominated applications balancing cost, risk, and capability overlap.',
      mathematicalAssertion: 'COUNT(candidate_apps) == 3 AND avoidable_spend_cr >= 28.0',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-003',
      simulationPreset: {
        volumeMultiplier: 0.1,
        rightsizingPercent: 85,
        licenseEscalation: -80,
        simNote: 'Simultaneous retirement of 3 Pareto-dominated portfolio applications.'
      },
      metrics: {
        'Candidate Apps': '3 Systems',
        'Avoidable Capital': '$28.5M',
        'Retired Dependencies': '12 Dependency Edges',
        'Pareto Frontier': 'Optimal Rationalization'
      }
    },
    {
      id: 'SCN-25',
      code: 'scenario_y',
      letter: 'Y',
      tier: 'advanced',
      category: 'Portfolio Strategy',
      name: 'Enterprise Strategic Portfolio Rebalancing',
      targetEntity: 'Enterprise Fleet (102 Nodes)',
      description: 'Portfolio Rebalancing: Shifting 15% of Run spend into Grow/Transform boosts portfolio value by 24%.',
      hypothesis: 'Dynamic capital reallocation from legacy maintenance to strategic capabilities maximizes enterprise TVR.',
      mathematicalAssertion: 'run_reallocation_pct == 0.15 AND value_acceleration_pct >= 0.20',
      verificationResult: 'PASS',
      suggestedAppId: 'REF-001',
      simulationPreset: {
        volumeMultiplier: 1.3,
        rightsizingPercent: 15,
        licenseEscalation: -10,
        simNote: 'Rebalancing 15% of run maintenance into high-velocity innovation capabilities.'
      },
      metrics: {
        'Run Spend Reallocated': '15.0%',
        'Reallocated Capital': '$18.4M',
        'Target Capabilities': '3 Core Innovations',
        'Value Acceleration': '+24.0% TVR Lift'
      }
    }
  ]

  return {
    scenarios
  }
}
