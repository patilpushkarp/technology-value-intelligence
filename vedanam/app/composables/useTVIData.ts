/**
 * TVI Analytical Dataset & Enterprise Knowledge Graph Composable
 * Directly reflects the 4-tier validated data models from DuckDB and NetworkX
 */

export interface EnterpriseApp {
  id: string
  name: string
  tier: 'Tier 1 (Mission Critical)' | 'Tier 2 (Operational)' | 'Tier 3 (Supporting)'
  businessUnit: string
  tco: number
  annualAvoidableCost: number
  activeUsers: number
  monthlyEvents: number
  dependenciesCount: number
  blastRadiusDollars: number
  vendor: string
  vendorLockInRisk: 'High' | 'Medium' | 'Low'
  timeQuadrant: 'Tolerate' | 'Invest' | 'Migrate' | 'Eliminate'
  capabilities: string[]
  description: string
  healthScore: number // 0 - 100
  sensoryTension: number // 0 - 1
}

export const useTVIData = () => {
  const applications: EnterpriseApp[] = [
    {
      id: 'APP-001',
      name: 'Customer Core Banking Ledger',
      tier: 'Tier 1 (Mission Critical)',
      businessUnit: 'Retail Banking & Wealth',
      tco: 1480000,
      annualAvoidableCost: 0,
      activeUsers: 8400,
      monthlyEvents: 42000000,
      dependenciesCount: 18,
      blastRadiusDollars: 4850000,
      vendor: 'FinSys Global',
      vendorLockInRisk: 'High',
      timeQuadrant: 'Invest',
      capabilities: ['Account Servicing', 'Deposit Processing', 'General Ledger Synchronization'],
      description: 'The transactional heartbeat of consumer accounts. High topological centrality with deep cascading operational dependencies.',
      healthScore: 92,
      sensoryTension: 0.25
    },
    {
      id: 'APP-007',
      name: 'Legacy Regional CRM Zombie',
      tier: 'Tier 3 (Supporting)',
      businessUnit: 'Commercial Operations',
      tco: 425000,
      annualAvoidableCost: 385000,
      activeUsers: 9,
      monthlyEvents: 42,
      dependenciesCount: 1,
      blastRadiusDollars: 45000,
      vendor: 'CloudMatrix Legacy',
      vendorLockInRisk: 'Low',
      timeQuadrant: 'Eliminate',
      capabilities: ['Customer Relationship Management (Superseded)'],
      description: 'Classic enterprise zombie system. High maintenance contracts, negligible user telemetry, zero active downstream dependencies.',
      healthScore: 18,
      sensoryTension: 0.88
    },
    {
      id: 'APP-012',
      name: 'Omnichannel API Mesh Gateway',
      tier: 'Tier 1 (Mission Critical)',
      businessUnit: 'Digital Engineering',
      tco: 910000,
      annualAvoidableCost: 240000,
      activeUsers: 14200,
      monthlyEvents: 98000000,
      dependenciesCount: 24,
      blastRadiusDollars: 3900000,
      vendor: 'OpenMesh Technologies',
      vendorLockInRisk: 'Low',
      timeQuadrant: 'Invest',
      capabilities: ['API Traffic Routing', 'Token Authentication', 'Rate Limiting'],
      description: 'Elastic workload subject to heavy-tailed spikes. Primary candidate for FinOps rightsizing and serverless concurrency tuning.',
      healthScore: 84,
      sensoryTension: 0.42
    },
    {
      id: 'APP-015',
      name: 'Global Instant Payments Engine',
      tier: 'Tier 1 (Mission Critical)',
      businessUnit: 'Global Transaction Services',
      tco: 2150000,
      annualAvoidableCost: 310000,
      activeUsers: 6200,
      monthlyEvents: 64000000,
      dependenciesCount: 15,
      blastRadiusDollars: 5200000,
      vendor: 'SwiftPay Systems',
      vendorLockInRisk: 'High',
      timeQuadrant: 'Invest',
      capabilities: ['ISO 20022 Clearing', 'Real-Time Settlement', 'Sanction Screening'],
      description: 'Major multi-year TVR investment project. Currently at 62% benefit realization target with a $1.33M value realization gap.',
      healthScore: 78,
      sensoryTension: 0.55
    },
    {
      id: 'APP-021',
      name: 'Document Archive Silo Matrix',
      tier: 'Tier 2 (Operational)',
      businessUnit: 'Risk & Legal Compliance',
      tco: 310000,
      annualAvoidableCost: 220000,
      activeUsers: 340,
      monthlyEvents: 12000,
      dependenciesCount: 3,
      blastRadiusDollars: 280000,
      vendor: 'DocStore Enterprise',
      vendorLockInRisk: 'Medium',
      timeQuadrant: 'Migrate',
      capabilities: ['Regulatory Archival', 'Cold Storage Retention'],
      description: 'On-premise silo redundant with the Modern Enterprise Data Lakehouse. Migration roadmap yields high ROI.',
      healthScore: 45,
      sensoryTension: 0.65
    },
    {
      id: 'APP-034',
      name: 'Supply Chain Procurement ERP',
      tier: 'Tier 2 (Operational)',
      businessUnit: 'Corporate Procurement',
      tco: 840000,
      annualAvoidableCost: 110000,
      activeUsers: 1100,
      monthlyEvents: 85000,
      dependenciesCount: 8,
      blastRadiusDollars: 1650000,
      vendor: 'TechNova',
      vendorLockInRisk: 'High',
      timeQuadrant: 'Tolerate',
      capabilities: ['Vendor Management', 'Purchase Order Orchestration'],
      description: 'High contractual exit penalty ($120k penalty + 14-month lock-in). Monitored under Stage-Gate governance.',
      healthScore: 64,
      sensoryTension: 0.48
    }
  ]

  const enterpriseStats = {
    totalSpend: 13248500,
    applicationsCount: 48,
    businessCapabilitiesCount: 12,
    avoidableSpend: 1865000,
    avoidableSpendPercentage: 14.1,
    spofBottlenecks: 3,
    avgBenefitRealization: 68.4,
    reconciliationVariancePercent: 0.00
  }

  // --------------------------------------------------------------------------
  // Reference Applications (Canonical Archetypes for TVI Architecture)
  // --------------------------------------------------------------------------
  const referenceApplications = [
    {
      id: 'REF-001',
      code: 'APP-001',
      name: 'Customer Core Banking Ledger',
      subtitle: 'Mission-Critical Transactional Archetype',
      tier: 'Tier 1 (Mission Critical)',
      archetypeTag: 'Mission Critical',
      timeQuadrant: 'Invest',
      tco: 1480000,
      avoidableCost: 0,
      activeUsers: 8400,
      monthlyEvents: 42000000,
      unitCostPerUser: 176.19,
      unitCostPer1kEvents: 0.0352,
      dependenciesCount: 18,
      blastRadiusDollars: 4850000,
      vendor: 'FinSys Global',
      vendorLockInRisk: 'High',
      healthScore: 94,
      slaTarget: '99.999%',
      carbonKgMo: 1240,
      description: 'The foundational benchmark for enterprise value realization: zero avoidable waste, high transactional volume, and fully burdened cost attribution across core banking capabilities.',
      costBreakdown: {
        infrastructure: 380000,
        software: 480000,
        personnel: 420000,
        overhead: 200000
      },
      infrastructureDetail: 'Multi-AZ AWS EKS Cluster (c6i.4xlarge), Aurora PostgreSQL Multi-Region, S3 Immutable WORM Audit Archive.',
      softwareDetail: 'FinSys Core Transaction Engine Enterprise v9.4 (Per-Core licensing + 24/7 Priority Support).',
      personnelDetail: '3.2 Dedicated FTEs (Platform Engineering, FinOps SRE, Financial Ledger Auditor).',
      overheadDetail: 'Shared IT Management, Enterprise Security Operations Center (SOC), Disaster Recovery Facilities.',
      capabilityAttribution: [
        { name: 'Account Servicing', percentage: 45, burdenedCost: 666000, tag: 'chip-mint' },
        { name: 'Deposit Processing', percentage: 35, burdenedCost: 518000, tag: 'chip-lavender' },
        { name: 'General Ledger Synchronization', percentage: 20, burdenedCost: 296000, tag: 'chip-sky' }
      ],
      topologyNodes: [
        { id: 'cap-1', label: 'Account Servicing', type: 'capability', color: '#a7f3d0' },
        { id: 'cap-2', label: 'Deposit Processing', type: 'capability', color: '#c4b5fd' },
        { id: 'cap-3', label: 'GL Synchronization', type: 'capability', color: '#7dd3fc' },
        { id: 'app-main', label: 'Core Banking Ledger', type: 'core', color: '#121316' },
        { id: 'db-1', label: 'Aurora PostgreSQL', type: 'infra', color: '#fed7aa' },
        { id: 'cache-1', label: 'Redis Mesh Cluster', type: 'infra', color: '#fed7aa' },
        { id: 's3-1', label: 'S3 Immutable Vault', type: 'infra', color: '#fed7aa' },
        { id: 'cons-1', label: 'Mobile Banking API', type: 'consumer', color: '#93c5fd' },
        { id: 'cons-2', label: 'Treasury Portal', type: 'consumer', color: '#93c5fd' },
        { id: 'cons-3', label: 'Fraud Detection Mesh', type: 'consumer', color: '#fca5a5' }
      ],
      whatIfDefaults: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 0,
        licenseEscalation: 0
      },
      governanceAudit: {
        reconciliationStatus: '100% Balanced ($0.00 Variance)',
        soxCompliance: 'Passed (Tier 1 Annual Audit)',
        drRecoveryRpo: '< 1 second (Synchronous Replication)',
        drRecoveryRto: '< 4 minutes (Automated Failover)',
        zeroTrustStatus: 'Mutual TLS 1.3 + OIDC Workload Identity'
      }
    },
    {
      id: 'REF-002',
      code: 'APP-012',
      name: 'Omnichannel API Mesh Gateway',
      subtitle: 'Elastic Cloud-Native FinOps Archetype',
      tier: 'Tier 1 (Mission Critical)',
      archetypeTag: 'Cloud Native',
      timeQuadrant: 'Invest',
      tco: 910000,
      avoidableCost: 240000,
      activeUsers: 14200,
      monthlyEvents: 98000000,
      unitCostPerUser: 64.08,
      unitCostPer1kEvents: 0.0093,
      dependenciesCount: 24,
      blastRadiusDollars: 3900000,
      vendor: 'OpenMesh Technologies',
      vendorLockInRisk: 'Low',
      healthScore: 84,
      slaTarget: '99.99%',
      carbonKgMo: 820,
      description: 'The archetype for cloud-native FinOps optimization: elastic microservices with high event velocity, rightsizing headroom, and dynamic rate-limiting tiers.',
      costBreakdown: {
        infrastructure: 440000,
        software: 160000,
        personnel: 210000,
        overhead: 100000
      },
      infrastructureDetail: 'Distributed Envoy Service Mesh across AWS us-east-1 and eu-west-1 with automated horizontal pod autoscaling.',
      softwareDetail: 'OpenMesh Enterprise Gateway Subscription with automated rate-limiting and zero-trust proxy.',
      personnelDetail: '1.8 Dedicated FTEs (API Gateway Platform Engineers and Cloud FinOps Analysts).',
      overheadDetail: 'Corporate API governance tooling and developer portal infrastructure overhead.',
      capabilityAttribution: [
        { name: 'API Traffic Routing', percentage: 50, burdenedCost: 455000, tag: 'chip-mint' },
        { name: 'Token Authentication', percentage: 30, burdenedCost: 273000, tag: 'chip-lavender' },
        { name: 'Rate Limiting & Telemetry', percentage: 20, burdenedCost: 182000, tag: 'chip-sky' }
      ],
      topologyNodes: [
        { id: 'cap-1', label: 'Traffic Routing', type: 'capability', color: '#a7f3d0' },
        { id: 'cap-2', label: 'Token Auth', type: 'capability', color: '#c4b5fd' },
        { id: 'app-main', label: 'API Mesh Gateway', type: 'core', color: '#121316' },
        { id: 'infra-1', label: 'Envoy K8s Pods', type: 'infra', color: '#fed7aa' },
        { id: 'infra-2', label: 'Route53 Global DNS', type: 'infra', color: '#fed7aa' },
        { id: 'cons-1', label: 'Retail Banking Mobile', type: 'consumer', color: '#93c5fd' },
        { id: 'cons-2', label: 'Partner Open API', type: 'consumer', color: '#93c5fd' }
      ],
      whatIfDefaults: {
        volumeMultiplier: 1.0,
        rightsizingPercent: 25,
        licenseEscalation: 5
      },
      governanceAudit: {
        reconciliationStatus: '100% Balanced ($0.00 Variance)',
        soxCompliance: 'Passed (OAuth2 / MTLS Validated)',
        drRecoveryRpo: '< 5 seconds (Global Traffic Shift)',
        drRecoveryRto: '< 30 seconds (Multi-Region Active-Active)',
        zeroTrustStatus: 'SPIFFE/SPIRE Mutual Authentication'
      }
    },
    {
      id: 'REF-003',
      code: 'APP-007',
      name: 'Legacy Regional CRM Zombie',
      subtitle: 'Application Rationalization Decommission Archetype',
      tier: 'Tier 3 (Supporting)',
      archetypeTag: 'Decommission',
      timeQuadrant: 'Eliminate',
      tco: 425000,
      avoidableCost: 385000,
      activeUsers: 9,
      monthlyEvents: 42,
      unitCostPerUser: 47222.22,
      unitCostPer1kEvents: 10119.04,
      dependenciesCount: 1,
      blastRadiusDollars: 45000,
      vendor: 'CloudMatrix Legacy',
      vendorLockInRisk: 'Low',
      healthScore: 18,
      slaTarget: '95.00%',
      carbonKgMo: 1450,
      description: 'The archetype for enterprise portfolio rationalization: extreme unit economic pathology ($47k/user), 90.6% avoidable cost, and negligible downstream dependencies.',
      costBreakdown: {
        infrastructure: 110000,
        software: 220000,
        personnel: 55000,
        overhead: 40000
      },
      infrastructureDetail: 'Legacy single-tenant VM hosting in legacy datacenter with unpatched operating system.',
      softwareDetail: 'CloudMatrix Legacy Enterprise License (Annual maintenance auto-renewal in Q4).',
      personnelDetail: '0.4 FTE Contractor maintenance for legacy script fixes.',
      overheadDetail: 'Datacenter rack space power and HVAC allocation.',
      capabilityAttribution: [
        { name: 'Customer Relationship Management', percentage: 100, burdenedCost: 425000, tag: 'chip-rose' }
      ],
      topologyNodes: [
        { id: 'cap-1', label: 'Legacy CRM', type: 'capability', color: '#fecdd3' },
        { id: 'app-main', label: 'Legacy Regional CRM', type: 'core', color: '#ef4444' },
        { id: 'infra-1', label: 'Legacy VM Server', type: 'infra', color: '#fed7aa' },
        { id: 'infra-2', label: 'Unmanaged DB', type: 'infra', color: '#fed7aa' }
      ],
      whatIfDefaults: {
        volumeMultiplier: 0.1,
        rightsizingPercent: 90,
        licenseEscalation: -100
      },
      governanceAudit: {
        reconciliationStatus: 'Audited (Flagged for Q3 Sunset)',
        soxCompliance: 'Conditional (Exception Waiver Active)',
        drRecoveryRpo: '24 hours (Cold Tape Backup)',
        drRecoveryRto: '48 hours (Manual Restore)',
        zeroTrustStatus: 'Legacy VPN Only (High Risk)'
      }
    }
  ]

  const activeReferenceAppId = useState<string>('vedanam_ref_app_id', () => 'REF-001')
  const activeReferenceApp = computed(() => {
    return referenceApplications.find(r => r.id === activeReferenceAppId.value) || referenceApplications[0]
  })

  const setReferenceApp = (id: string) => {
    activeReferenceAppId.value = id
  }

  const selectedAppId = useState<string>('vedanam_selected_app', () => 'APP-001')
  const perceptionMode = useState<'sensory' | 'analytical'>('vedanam_mode', () => 'sensory')

  const selectedApp = computed(() => {
    return applications.find(a => a.id === selectedAppId.value) || applications[0]
  })

  const selectApp = (id: string) => {
    selectedAppId.value = id
  }

  return {
    applications,
    enterpriseStats,
    referenceApplications,
    activeReferenceAppId,
    activeReferenceApp,
    setReferenceApp,
    selectedAppId,
    selectedApp,
    selectApp,
    perceptionMode
  }
}
