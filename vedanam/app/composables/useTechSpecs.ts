/**
 * Technical Specifications Composable for Vedanam / TVI
 * Provides structured data for the 6 phases, 12 steps, mathematical models,
 * hardware benchmarks, and interactive simulation models.
 */

export interface TechSpecStep {
  id: number
  code: string
  phase: string
  phaseNumber: number
  title: string
  shortTitle: string
  notebook: string
  pythonModule: string
  category: 'Data & OLAP' | 'Graph Topology' | 'Cost & Attribution' | 'Rationalization' | 'Value & Variance' | 'AI & Governance'
  badgeColor: 'mint' | 'lavender' | 'sky' | 'peach' | 'rose'
  subpageUrl: string
  summary: string
  executionDetails: string[]
  formulaName: string
  formulaLatex: string
  formulaHtml?: string
  formulaExplanation: string
  inputContract: string
  outputContract: string
  latencySla: string
  memoryBudget: string
  keyParameters: { name: string; value: string; desc: string }[]
  codeSnippet: string
}

export interface SystemArchitectureSpec {
  tier: string
  name: string
  technology: string
  role: string
  memoryLimit: string
  latency: string
  guarantees: string
}

export const useTechSpecs = () => {
  const systemArchitecture: SystemArchitectureSpec[] = [
    {
      tier: 'Analytical Truth',
      name: 'DuckDB Columnar OLAP',
      technology: 'DuckDB v1.1.3 + Snappy Parquet',
      role: 'In-process vectorized relational queries, GL general ledger mass-balance sums, MoM variance joins.',
      memoryLimit: '< 4.0 GB RAM (Zero Spillover)',
      latency: '< 4.2 ms avg query',
      guarantees: 'Zero-Reconciliation Mass Balance (0.00% drift)'
    },
    {
      tier: 'Relationship Intelligence',
      name: 'NetworkX Semantic Graph',
      technology: 'NetworkX v3.4.2 In-Memory MultiDiGraph',
      role: 'Typed enterprise ontology, multi-hop transitive traversals, Betweenness centrality, DAG cycle validation.',
      memoryLimit: '< 250 MB RAM',
      latency: '< 8.5 ms BFS traversal',
      guarantees: 'Strict ontology enforcement, cycle-free DAGs'
    },
    {
      tier: 'Autonomous Decision Layer',
      name: 'Dual-Mode Knowledge Graph Analyst',
      technology: 'Deterministic Regex / AST Parser + Local Ollama (Mistral 7B)',
      role: 'Natural language question translation, parameterized Cypher/SQL, zero-hallucination grounding.',
      memoryLimit: '< 50 MB (Rules) / 5.2 GB (Ollama SLM)',
      latency: '< 1.8 ms (Rules mode)',
      guarantees: '100% Offline, Read-Only sandboxing, Zero prompt injection'
    },
    {
      tier: 'Presentation & Sensory Twin',
      name: 'Vedanam Nuxt 4 Architecture',
      technology: 'Nuxt 4 + Three.js + GSAP ScrollTrigger',
      role: 'Living architectural digital twin, 432Hz harmonic soundscapes, interactive what-if simulation matrices.',
      memoryLimit: '< 120 MB Browser Heap',
      latency: '60 - 120 FPS render loop',
      guarantees: '100% Viewport utilization, zero memory leaks'
    }
  ]

  const hardwareBenchmarks = [
    { label: 'Host Hardware Target', value: '16 GB RAM Laptop (Apple Silicon / x86_64)', status: 'Verified' },
    { label: 'External Cloud Call Budget', value: 'Zero (100% Offline / Local-First)', status: 'Strictly Enforced' },
    { label: 'Random Determinism Seed', value: 'Seed 42 (Reproducible in config.yaml)', status: 'Guaranteed' },
    { label: 'General Ledger Mass-Balance Error', value: '0.00% (Machine epsilon exact)', status: 'Validated' },
    { label: 'Graph Scale in Production', value: '102 Enterprise Nodes, 196 Typed Edges', status: 'Continuous Audit' },
    { label: 'Automated Integrity Test Suite', value: '83/83 Pytest Suites Passing (13.1s)', status: 'Passing' }
  ]

  const steps: TechSpecStep[] = [
    {
      id: 1,
      code: 'STEP-01',
      phase: 'Phase 1: Procedural Data Generation & Synthesis',
      phaseNumber: 1,
      title: 'Procedural Entity Generation & Heavy-Tailed Telemetry',
      shortTitle: 'Data Generation & Copulas',
      notebook: '01_generate_enterprise_data.ipynb',
      pythonModule: 'src/tvi/data_generation.py & copulas.py',
      category: 'Data & OLAP',
      badgeColor: 'mint',
      subpageUrl: '/technical-specs/data-pipeline',
      summary: 'Procedural synthesis of 102 enterprise nodes and multi-tier relationships with multivariate copula correlations and heavy-tailed non-Gaussian distributions.',
      executionDetails: [
        'Seeds pseudo-random number generator with fixed seed = 42 for absolute determinism.',
        'Replaces naive Gaussian assumptions with bounded Beta (proportions), Weibull (MTBF failure curves), and Log-Normal (telemetry spikes).',
        'Applies Gaussian Copula with Cholesky decomposition L*L^T to preserve non-linear rank correlations between active users, cloud vCPUs, and GL spend.',
        'Injects 25 enterprise benchmark scenarios (Scenarios A through Y) including zombie systems, duplicate OMS clusters, and single points of failure.'
      ],
      formulaName: "Sklar's Theorem for Multivariate Copulas",
      formulaLatex: 'F(x_1, \\dots, x_d) = C(F_1(x_1), \\dots, F_d(x_d)) \\quad \\text{with} \\quad C_R(u) = \\Phi_R(\\Phi^{-1}(u_1), \\dots, \\Phi^{-1}(u_d))',
      formulaHtml: '<i>F</i>(<i>x</i><sub>1</sub>, …, <i>x</i><sub><i>d</i></sub>) = <i>C</i>(<i>F</i><sub>1</sub>(<i>x</i><sub>1</sub>), …, <i>F</i><sub><i>d</i></sub>(<i>x</i><sub><i>d</i></sub>)) &emsp;<span class="math-keyword">with</span>&emsp; <i>C</i><sub><i>R</i></sub>(<b>u</b>) = &Phi;<sub><i>R</i></sub>(&Phi;<sup>&minus;1</sup>(<i>u</i><sub>1</sub>), …, &Phi;<sup>&minus;1</sup>(<i>u</i><sub><i>d</i></sub>))',
      formulaExplanation: 'Separates marginal distributions (e.g. log-normal compute consumption) from joint dependency structures, ensuring authentic heavy-tailed telemetry without violating financial boundaries.',
      inputContract: 'config.yaml, ontology.yaml, random_seed = 42',
      outputContract: '11 Raw CSV entities in data/generated/ (applications, vendors, costs, consumption, etc.)',
      latencySla: '< 1.4 seconds total generation',
      memoryBudget: '< 180 MB RAM peak',
      keyParameters: [
        { name: 'random_seed', value: '42', desc: 'Deterministic pseudo-random state' },
        { name: 'app_count', value: '48', desc: 'Enterprise applications generated' },
        { name: 'capability_count', value: '12', desc: 'Business capabilities mapped' },
        { name: 'cost_records_count', value: '3,840', desc: 'GL invoice entries generated' }
      ],
      codeSnippet: `def generate_enterprise_data(config: Config) -> EnterpriseDataset:
    sampler = DistributionSampler(config.distributions, seed=config.random_seed)
    copula = GaussianCopula(correlation_matrix=config.copula_matrix)
    telemetry = copula.sample_multivariate(n_samples=3840, marginals=config.marginals)
    return inject_scenarios(telemetry, scenarios=config.scenarios)`
    },
    {
      id: 2,
      code: 'STEP-02',
      phase: 'Phase 1: Procedural Data Generation & Synthesis',
      phaseNumber: 1,
      title: 'TBM ATUM Taxonomy & Vectorized Columnar OLAP',
      shortTitle: 'DuckDB OLAP & Mass Balance',
      notebook: '02_tbm_itfm_data_model.ipynb',
      pythonModule: 'src/tvi/database.py',
      category: 'Data & OLAP',
      badgeColor: 'sky',
      subpageUrl: '/technical-specs/data-pipeline',
      summary: 'Columnar schema compilation in DuckDB enforcing ATUM 4-tier taxonomy and machine-precision Zero-Reconciliation mass-balance proofs.',
      executionDetails: [
        'Creates in-process DuckDB tables with vectorized execution indices over Parquet with Snappy compression.',
        'Implements the Apptio TBM Unified Model (ATUM) across Cost Pools -> IT Towers -> Applications -> Services.',
        'Validates Zero-Reconciliation Theorem: Machine-exact integer-cents ledger summation confirming zero balance loss.',
        'Materializes analytical SQL views for multi-year cost summaries, monthly active user economics, and vendor spend rollups.'
      ],
      formulaName: 'General Ledger Mass-Balance Conservation',
      formulaLatex: '\\sum_{k \\in \\text{Cost Pools}} C_k \\equiv \\sum_{t \\in \\text{IT Towers}} C_t \\equiv \\sum_{a \\in \\text{Apps}} C_a = C_{\\text{Total}} \\quad (\\text{Variance} = 0.00\\%)',
      formulaHtml: '<span class="math-op">&sum;</span><sub><i>k</i> &isin; Cost Pools</sub> <i>C</i><sub><i>k</i></sub> &equiv; <span class="math-op">&sum;</span><sub><i>t</i> &isin; Towers</sub> <i>C</i><sub><i>t</i></sub> &equiv; <span class="math-op">&sum;</span><sub><i>a</i> &isin; Apps</sub> <i>C</i><sub><i>a</i></sub> = <i>C</i><sub>Total</sub> &emsp;<span class="math-note">Variance = 0.00%</span>',
      formulaExplanation: 'Ensures that every dollar in the general ledger is accounted for through every taxonomic transformation layer, eliminating the 12-18% reconciliation variance typical of spreadsheet models.',
      inputContract: 'data/generated/*.csv',
      outputContract: 'database/tvi.duckdb & data/parquet/*.parquet (11 tables)',
      latencySla: '< 4.2 ms for full enterprise GL aggregation',
      memoryBudget: '< 4.0 GB DuckDB buffer manager limit',
      keyParameters: [
        { name: 'storage_format', value: 'Parquet + Snappy', desc: 'Columnar compression algorithm' },
        { name: 'vector_size', value: '2,048 rows', desc: 'DuckDB SIMD vector execution chunk' },
        { name: 'precision', value: 'DECIMAL(18,2)', desc: 'Exact monetary arithmetic precision' }
      ],
      codeSnippet: `def create_tbm_schema(conn: duckdb.DuckDBPyConnection):
    conn.execute("""
        CREATE VIEW v_fully_burdened_tco AS
        SELECT app_id, SUM(amount) AS tco,
               SUM(CASE WHEN cost_tower = 'Infrastructure' THEN amount ELSE 0 END) AS infra_cost
        FROM cost_records GROUP BY app_id;
    """)`
    },
    {
      id: 3,
      code: 'STEP-03',
      phase: 'Phase 2: Semantic Knowledge Graph & Topology',
      phaseNumber: 2,
      title: 'Typed Semantic Property Graph & Multi-Hop Lineage',
      shortTitle: 'NetworkX Semantic Graph',
      notebook: '03_build_knowledge_graph.ipynb',
      pythonModule: 'src/tvi/graph.py & graph_queries.py',
      category: 'Graph Topology',
      badgeColor: 'lavender',
      subpageUrl: '/technical-specs/graph-topology',
      summary: 'Construction of an in-memory typed semantic property graph in NetworkX with multi-hop traversals and Brandes betweenness centrality.',
      executionDetails: [
        'Translates tabular entities into a directed MultiDiGraph with 102 typed nodes and 196 semantic edges.',
        'Enforces enterprise ontology schema: DEPENDS_ON, PROVIDES, HOSTED_ON, FUNDED_BY, DELIVERS, TRACKS.',
        'Computes graph topological metrics: In-degree, Out-degree, PageRank, and Brandes Betweenness Centrality.',
        'Exports graph topologies to GraphML, Cytoscape JSON, and focused subgraphs for interactive visual exploration.'
      ],
      formulaName: "Brandes' Betweenness Centrality Algorithm",
      formulaLatex: 'C_B(v) = \\sum_{s \\neq v \\neq t \\in V} \\frac{\\sigma_{st}(v)}{\\sigma_{st}} \\quad \\text{in} \\quad \\mathcal{O}(|V| \\cdot |E|)',
      formulaHtml: '<i>C</i><sub><i>B</i></sub>(<i>v</i>) = <span class="math-op">&sum;</span><sub><i>s</i> &ne; <i>v</i> &ne; <i>t</i> &isin; <i>V</i></sub> <span class="math-frac"><span class="math-num">&sigma;<sub><i>st</i></sub>(<i>v</i>)</span><span class="math-denom">&sigma;<sub><i>st</i></sub></span></span> &emsp;<span class="math-keyword">in</span>&emsp; <span class="math-cal">O</span>(|<i>V</i>| &middot; |<i>E</i>|)',
      formulaExplanation: 'Identifies high-traffic topological bottlenecks by quantifying the fraction of shortest dependency paths between all enterprise node pairs that pass through node v.',
      inputContract: 'database/tvi.duckdb & ontology.yaml',
      outputContract: 'In-memory nx.MultiDiGraph & graph_output/enterprise_tvr.graphml',
      latencySla: '< 8.5 ms BFS multi-hop traversal',
      memoryBudget: '< 250 MB RAM',
      keyParameters: [
        { name: 'nodes_count', value: '102', desc: 'Total graph vertices' },
        { name: 'edges_count', value: '196', desc: 'Directed semantic edges' },
        { name: 'damping_factor', value: '0.85', desc: 'PageRank propagation damping' }
      ],
      codeSnippet: `def build_knowledge_graph(db: TVIDatabase, ontology: Ontology) -> nx.MultiDiGraph:
    G = nx.MultiDiGraph()
    for node in db.get_all_entities():
        G.add_node(node.id, **node.properties)
    for edge in db.get_all_relationships():
        G.add_edge(edge.source, edge.target, key=edge.type, **edge.properties)
    return G`
    },
    {
      id: 4,
      code: 'STEP-04',
      phase: 'Phase 3: Cost Intelligence & Capability Attribution',
      phaseNumber: 3,
      title: '5-Layer Activity-Based Cost Stack & Unit Economics',
      shortTitle: '5-Layer TCO & Unit Economics',
      notebook: '04_application_cost_intelligence.ipynb',
      pythonModule: 'src/tvi/cost_analytics.py',
      category: 'Cost & Attribution',
      badgeColor: 'peach',
      subpageUrl: '/technical-specs/cost-attribution',
      summary: 'Deconstruction of fully burdened application TCO across a 5-layer cost stack, unit economics modeling, and Lorenz spend concentration.',
      executionDetails: [
        'Disaggregates application spend into 5 discrete layers: Direct Infrastructure, Software Licenses, Internal Personnel, External Vendors, and Shared Overhead.',
        'Computes FinOps unit economics: Burdened cost per monthly active user and cost per 1,000 transaction events.',
        'Distinguishes high-throughput "Workhorse" platforms from low-telemetry "Zombie" systems.',
        'Calculates Lorenz curve distribution and the enterprise Gini coefficient for technology spend concentration.'
      ],
      formulaName: '5-Layer Burdened Cost & Gini Concentration',
      formulaLatex: '\\text{TCO}_i = C_{\\text{Infra},i} + C_{\\text{Soft},i} + C_{\\text{Pers},i} + C_{\\text{Vend},i} + C_{\\text{Overhead},i}, \\quad G = \\frac{\\sum_{i=1}^n (2i - n - 1) y_i}{n \\sum_{i=1}^n y_i}',
      formulaHtml: 'TCO<sub><i>i</i></sub> = <i>C</i><sub>Infra,<i>i</i></sub> + <i>C</i><sub>Soft,<i>i</i></sub> + <i>C</i><sub>Pers,<i>i</i></sub> + <i>C</i><sub>Vend,<i>i</i></sub> + <i>C</i><sub>Overhead,<i>i</i></sub>, &emsp; <i>G</i> = <span class="math-frac"><span class="math-num"><span class="math-op">&sum;</span> (2<i>i</i> &minus; <i>n</i> &minus; 1) <i>y</i><sub><i>i</i></sub></span><span class="math-denom"><i>n</i> <span class="math-op">&sum;</span> <i>y</i><sub><i>i</i></sub></span></span>',
      formulaExplanation: 'Eliminates partial cost blindspots by fully burdening each service with its fair share of platform operations, database licensing, and security infrastructure.',
      inputContract: 'DuckDB cost_records & consumption_records',
      outputContract: 'DataFrame of fully burdened application profiles with unit economics',
      latencySla: '< 5.8 ms for all 48 applications',
      memoryBudget: '< 80 MB RAM',
      keyParameters: [
        { name: 'cost_stack_layers', value: '5', desc: 'Direct to shared attribution tiers' },
        { name: 'enterprise_gini', value: '0.62', desc: 'Observed spend concentration index' },
        { name: 'overhead_allocation', value: 'Activity-Based', desc: 'Proportional driver assignment' }
      ],
      codeSnippet: `def compute_application_tco_stack(app_id: str, db: TVIDatabase) -> AppCostStack:
    costs = db.query_cost_breakdown(app_id)
    unit_cost_user = costs.total_tco / max(1, costs.active_users)
    unit_cost_event = (costs.total_tco / (costs.monthly_events * 12)) * 1000
    return AppCostStack(tco=costs.total_tco, cost_per_user=unit_cost_user, cost_per_1k=unit_cost_event)`
    },
    {
      id: 5,
      code: 'STEP-05',
      phase: 'Phase 3: Cost Intelligence & Capability Attribution',
      phaseNumber: 3,
      title: 'Proportional Capability Attribution & Redundancy Analysis',
      shortTitle: 'Capability Attribution & Sankey',
      notebook: '05_capability_cost_intelligence.ipynb',
      pythonModule: 'src/tvi/cost_analytics.py',
      category: 'Cost & Attribution',
      badgeColor: 'rose',
      subpageUrl: '/technical-specs/cost-attribution',
      summary: 'Bipartite projection attributing application costs to business capabilities with weight conservation proofs and redundancy quantification.',
      executionDetails: [
        'Maps applications to business capabilities via bipartite relationship edges PROVIDES.',
        'Applies proportional allocation weights: sum of weights for any application equals exactly 1.0 (Double-Counting Prevention Proof).',
        'Detects capability redundancy where multiple legacy applications provide duplicate business functionality (e.g. Scenario C Order-to-Cash duplication).',
        'Generates multi-tier Sankey value flow matrices showing flow from General Ledger -> Cost Pools -> Applications -> Capabilities.'
      ],
      formulaName: 'Double-Counting Prevention Conservation Proof',
      formulaLatex: '\\text{Cost}(C_j) = \\sum_{i=1}^m w_{ij} \\cdot \\text{TCO}(A_i) \\quad \\text{where} \\quad \\forall i, \\sum_{j=1}^k w_{ij} = 1.0',
      formulaHtml: 'Cost(<i>C</i><sub><i>j</i></sub>) = <span class="math-op">&sum;</span><sub><i>i</i>=1</sub><sup><i>m</i></sup> <i>w</i><sub><i>ij</i></sub> &middot; TCO(<i>A</i><sub><i>i</i></sub>) &emsp;<span class="math-keyword">where</span>&emsp; &forall; <i>i</i>, <span class="math-op">&sum;</span><sub><i>j</i>=1</sub><sup><i>k</i></sup> <i>w</i><sub><i>ij</i></sub> &equiv; 1.00',
      formulaExplanation: 'Proves mathematically that enterprise capability rollups match the general ledger sum exactly, preventing simultaneous double-billing of shared platforms across business units.',
      inputContract: 'DuckDB applications, rel_app_capability & NetworkX G',
      outputContract: 'Capability attribution summary & Sankey node-link dataset',
      latencySla: '< 7.1 ms capability matrix projection',
      memoryBudget: '< 95 MB RAM',
      keyParameters: [
        { name: 'total_capabilities', value: '12', desc: 'Level-1 business capabilities' },
        { name: 'max_redundancy_apps', value: '3', desc: 'Maximum duplicate applications per capability' },
        { name: 'mass_conservation', value: '100.00%', desc: 'Allocated sum / total TCO ratio' }
      ],
      codeSnippet: `def attribute_capability_costs(G: nx.MultiDiGraph, app_costs: Dict[str, float]) -> Dict[str, float]:
    cap_costs = defaultdict(float)
    for app, tco in app_costs.items():
        caps = [target for _, target in G.out_edges(app) if G.edges[app, target, 'PROVIDES']]
        weight = 1.0 / len(caps)
        for cap in caps:
            cap_costs[cap] += tco * weight
    return dict(cap_costs)`
    },
    {
      id: 6,
      code: 'STEP-06',
      phase: 'Phase 4: Consumption Profiling & Rationalization',
      phaseNumber: 4,
      title: 'Telemetry Profiling, Quadrant Split & GreenOps Rightsizing',
      shortTitle: 'Telemetry & Zombie Detection',
      notebook: '06_consumption_intelligence.ipynb',
      pythonModule: 'src/tvi/consumption_analytics.py',
      category: 'Rationalization',
      badgeColor: 'mint',
      subpageUrl: '/technical-specs/portfolio-rationalization',
      summary: 'Multivariate telemetry analysis, median-split 2x2 cost vs utilization quadrant profiling, and cloud GreenOps carbon emissions estimation.',
      executionDetails: [
        'Normalizes multi-dimensional telemetry: CPU utilization, Memory pressure, IOPS, API call velocity, and Active user concurrency.',
        'Applies median-split partitioning along Cost vs Utilization axes into 4 quadrants: Workhorses, Over-Provisioned, Under-Utilized, and Zombie Systems.',
        'Calculates Cloud Elasticity Coefficient epsilon measuring how well cloud costs dynamically track demand fluctuations.',
        'Computes GreenOps Scope 2 greenhouse gas emissions: kWh power consumption derived from PUE and regional grid carbon intensity.'
      ],
      formulaName: 'Cloud Elasticity & GreenOps GHG Math',
      formulaLatex: '\\epsilon = \\frac{\\% \\Delta \\text{Cost}}{\\% \\Delta \\text{Workload}}, \\quad \\text{GHG (kg } \\text{CO}_2\\text{e)} = \\sum_{h} (\\text{kWh}_h \\times \\text{PUE} \\times I_{\\text{grid}})',
      formulaHtml: '&epsilon; = <span class="math-frac"><span class="math-num">% &Delta; Cost</span><span class="math-denom">% &Delta; Workload</span></span>, &emsp; GHG = <span class="math-op">&sum;</span><sub><i>h</i></sub> (kWh<sub><i>h</i></sub> &times; PUE &times; <i>I</i><sub>grid</sub>)',
      formulaExplanation: 'Identifies zombie applications that consume power and capital 24/7 with near-zero transactional utility, enabling targeted automated rightsizing.',
      inputContract: 'DuckDB consumption_records (hourly time-series)',
      outputContract: 'Quadrant segmentation classification & GreenOps emission audit',
      latencySla: '< 6.4 ms telemetry profile aggregation',
      memoryBudget: '< 110 MB RAM',
      keyParameters: [
        { name: 'pue_factor', value: '1.20', desc: 'Hyperscale Cloud Power Usage Effectiveness' },
        { name: 'zombie_threshold', value: 'Cost > P50, Util < P20', desc: 'Deterministic Zombie classification rule' },
        { name: 'grid_intensity', value: '0.385 kg/kWh', desc: 'Regional grid carbon emissions factor' }
      ],
      codeSnippet: `def classify_consumption_quadrants(df: pd.DataFrame) -> pd.DataFrame:
    median_cost = df['tco'].median()
    median_util = df['composite_utilization'].median()
    df['quadrant'] = np.select([
        (df['tco'] >= median_cost) & (df['composite_utilization'] >= median_util),
        (df['tco'] >= median_cost) & (df['composite_utilization'] < median_util),
        (df['tco'] < median_cost) & (df['composite_utilization'] >= median_util),
    ], ['Workhorses', 'Over-Provisioned', 'Efficient Supporting'], default='Zombie Systems')
    return df`
    },
    {
      id: 7,
      code: 'STEP-07',
      phase: 'Phase 4: Consumption Profiling & Rationalization',
      phaseNumber: 4,
      title: 'TOPSIS Multi-Criteria Decision Analysis & TIME Matrix',
      shortTitle: 'TOPSIS MCDA & TIME Runbooks',
      notebook: '07_application_rationalization.ipynb',
      pythonModule: 'src/tvi/rationalization.py',
      category: 'Rationalization',
      badgeColor: 'sky',
      subpageUrl: '/technical-specs/portfolio-rationalization',
      summary: 'Objective multi-criteria portfolio ranking using TOPSIS vector normalization, Pareto frontiers, and contractual exit penalty modeling.',
      executionDetails: [
        'Formulates a decision matrix across 5 weighted criteria: Annual TCO, Technical Debt, Blast Radius, Business Capability Fit, and Vendor Lock-in Risk.',
        'Executes TOPSIS vector normalization to compute Euclidean distances to Positive Ideal Solution (PIS) and Negative Ideal Solution (NIS).',
        'Assigns applications into the Gartner TIME framework (Tolerate, Invest, Migrate, Eliminate).',
        'Enforces Analytical Guardrail 1: Models avoidable cost scenarios with contract termination penalty amortization rather than claiming fictional gross savings.'
      ],
      formulaName: 'TOPSIS Relative Closeness Formulation',
      formulaLatex: 'R_i^* = \\frac{S_i^-}{S_i^* + S_i^-} \\quad \\text{where} \\quad S_i^* = \\sqrt{\\sum_{j=1}^m (v_{ij} - v_j^*)^2}, \\; S_i^- = \\sqrt{\\sum_{j=1}^m (v_{ij} - v_j^-)^2}',
      formulaHtml: '<i>R</i><sub><i>i</i></sub><sup>*</sup> = <span class="math-frac"><span class="math-num"><i>S</i><sub><i>i</i></sub><sup>&minus;</sup></span><span class="math-denom"><i>S</i><sub><i>i</i></sub><sup>*</sup> + <i>S</i><sub><i>i</i></sub><sup>&minus;</sup></span></span> &emsp;<span class="math-keyword">where</span>&emsp; <i>S</i><sub><i>i</i></sub><sup>*</sup> = &radic;<span class="math-sqrt-body"><span class="math-op">&sum;</span> (<i>v</i><sub><i>ij</i></sub> &minus; <i>v</i><sub><i>j</i></sub><sup>*</sup>)<sup>2</sup></span>',
      formulaExplanation: 'Ranks rationalization priorities without human subjectivity, placing applications closest to maximum cost avoidance and lowest operational risk at the top of the elimination queue.',
      inputContract: 'DuckDB fully burdened TCO + consumption + dependency metrics',
      outputContract: 'MCDA ranked portfolio & TIME matrix classification dataframe',
      latencySla: '< 11.2 ms TOPSIS matrix calculation',
      memoryBudget: '< 75 MB RAM',
      keyParameters: [
        { name: 'weights_vector', value: '[0.25, 0.20, 0.25, 0.15, 0.15]', desc: 'Criteria importance weights' },
        { name: 'time_quadrants', value: 'Tolerate, Invest, Migrate, Eliminate', desc: 'Standard 4-cell taxonomy' },
        { name: 'guardrail', value: 'Avoidable Cost vs Gross Savings', desc: 'Enforces penalty deductions' }
      ],
      codeSnippet: `def run_topsis_mcda(matrix: np.ndarray, weights: np.ndarray, is_benefit: List[bool]) -> np.ndarray:
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))
    weighted = norm_matrix * weights
    pis = np.where(is_benefit, weighted.max(axis=0), weighted.min(axis=0))
    nis = np.where(is_benefit, weighted.min(axis=0), weighted.max(axis=0))
    d_plus = np.linalg.norm(weighted - pis, axis=1)
    d_minus = np.linalg.norm(weighted - nis, axis=1)
    return d_minus / (d_plus + d_minus)`
    },
    {
      id: 8,
      code: 'STEP-08',
      phase: 'Phase 2: Semantic Knowledge Graph & Topology',
      phaseNumber: 2,
      title: 'Transitive Blast Radius, DAG Cycles & Single Points of Failure',
      shortTitle: 'Blast Radius & SPOF Cascades',
      notebook: '08_dependency_and_impact_analysis.ipynb',
      pythonModule: 'src/tvi/dependency.py',
      category: 'Graph Topology',
      badgeColor: 'lavender',
      subpageUrl: '/technical-specs/graph-topology',
      summary: 'Directed Acyclic Graph cycle detection, transitive closure BFS reachability sets, Blast Radius Index (BRI), and Monte Carlo outage cascade simulation.',
      executionDetails: [
        'Runs Tarjans algorithm for Strongly Connected Components (SCC) and Kahns topological sort to verify DAG acyclicity.',
        'Calculates transitive reachability sets R(u) using multi-hop BFS over DEPENDS_ON edges.',
        'Computes the Blast Radius Index (BRI) weighting downstream application criticality and revenue impact.',
        'Pinpoints Single Points of Failure (SPOFs) such as Scenario D APP010 Payments Gateway and simulates cascade failure impact.'
      ],
      formulaName: 'Transitive Blast Radius Index (BRI)',
      formulaLatex: '\\text{BRI}(u) = \\frac{|R(u)|}{N - 1} \\times \\sum_{v \\in R(u)} w_{\\text{crit}}(v) \\cdot \\text{TCO}(v) \\quad \\text{where} \\; R(u) = \\{ v \\in V \\mid u \\rightsquigarrow v \\}',
      formulaHtml: 'BRI(<i>u</i>) = <span class="math-frac"><span class="math-num">|<i>R</i>(<i>u</i>)|</span><span class="math-denom"><i>N</i> &minus; 1</span></span> &times; <span class="math-op">&sum;</span><sub><i>v</i> &isin; <i>R</i>(<i>u</i>)</sub> <i>w</i><sub>crit</sub>(<i>v</i>) &middot; TCO(<i>v</i>) &emsp;<span class="math-keyword">where</span>&emsp; <i>R</i>(<i>u</i>) = { <i>v</i> &isin; <i>V</i> &mid; <i>u</i> &#8669; <i>v</i> }',
      formulaExplanation: 'Measures total collateral damage if system u fails, combining downstream topology reachability with real financial and commercial criticality.',
      inputContract: 'NetworkX MultiDiGraph G & applications metadata',
      outputContract: 'Reachability graph, Blast Radius Index ratings, and SPOF ranking',
      latencySla: '< 5.4 ms full transitive closure across all nodes',
      memoryBudget: '< 130 MB RAM',
      keyParameters: [
        { name: 'max_depth', value: '10 hops', desc: 'Maximum traversal horizon' },
        { name: 'spof_node_id', value: 'APP-010', desc: 'Scenario D Payment Gateway hub' },
        { name: 'cycle_detection', value: 'Tarjan SCC (Strict Zero Cycles)', desc: 'Topological sort requirement' }
      ],
      codeSnippet: `def compute_blast_radius(G: nx.MultiDiGraph, app_id: str) -> BlastRadiusResult:
    downstream = nx.descendants(G, app_id)
    impacted_tco = sum(G.nodes[node].get('tco', 0) for node in downstream)
    critical_count = sum(1 for node in downstream if G.nodes[node].get('tier') == 'Tier 1')
    return BlastRadiusResult(node_count=len(downstream), impacted_tco=impacted_tco, critical_count=critical_count)`
    },
    {
      id: 9,
      code: 'STEP-09',
      phase: 'Phase 5: Value Realization & Variance Intelligence',
      phaseNumber: 5,
      title: 'TVR Benefit Realization & Difference-in-Differences Econometrics',
      shortTitle: 'TVR Realization & DiD',
      notebook: '09_investment_benefit_realization.ipynb',
      pythonModule: 'src/tvi/value_realization.py',
      category: 'Value & Variance',
      badgeColor: 'peach',
      subpageUrl: '/technical-specs/value-variance',
      summary: 'Technology Value Realization (TVR) framework tracking post-implementation KPI movements, VRR waterfalls, and causal econometric DiD models.',
      executionDetails: [
        'Substitutes static project accounting with post-delivery longitudinal benefit realization auditing.',
        'Calculates Value Realization Ratio (VRR) and Net Value Realization (NVR) across multi-year transformation projects.',
        'Employs Difference-in-Differences (DiD) econometrics with two-way fixed effects to isolate causal technology impact from macro baseline trends.',
        'Enforces Analytical Guardrail 2: Strictly documents benefits as "associated with" KPI shifts to prevent ungrounded single-factor claims.'
      ],
      formulaName: 'Difference-in-Differences Causal Estimator',
      formulaLatex: '\\hat{\\beta}_{\\text{DiD}} = (\\bar{Y}_{\\text{Post}, T} - \\bar{Y}_{\\text{Pre}, T}) - (\\bar{Y}_{\\text{Post}, C} - \\bar{Y}_{\\text{Pre}, C})',
      formulaHtml: '<span class="math-hat">&beta;&#770;</span><sub>DiD</sub> = (<i>Y&#772;</i><sub>Post, <i>T</i></sub> &minus; <i>Y&#772;</i><sub>Pre, <i>T</i></sub>) &minus; (<i>Y&#772;</i><sub>Post, <i>C</i></sub> &minus; <i>Y&#772;</i><sub>Pre, <i>C</i></sub>)',
      formulaExplanation: 'Subtracts natural market drift in an untreated control group from the treated transformation cohort, proving what portion of efficiency gains was genuinely caused by the technology investment.',
      inputContract: 'DuckDB benefits, kpis, rel_benefit_kpi & projects',
      outputContract: 'Benefit waterfall series, VRR scorecard, and DiD regression results',
      latencySla: '< 8.2 ms econometric regression solve',
      memoryBudget: '< 85 MB RAM',
      keyParameters: [
        { name: 'vrr_target', value: '>= 0.85', desc: 'Threshold for investment success' },
        { name: 'scenario_e_vrr', value: '0.94', desc: 'Successful payments modernization' },
        { name: 'scenario_f_vrr', value: '0.38', desc: 'Failed legacy CRM rewrite drift' }
      ],
      codeSnippet: `def compute_did_treatment_effect(treatment_pre, treatment_post, control_pre, control_post) -> float:
    delta_treatment = np.mean(treatment_post) - np.mean(treatment_pre)
    delta_control = np.mean(control_post) - np.mean(control_pre)
    return float(delta_treatment - delta_control)`
    },
    {
      id: 10,
      code: 'STEP-10',
      phase: 'Phase 5: Value Realization & Variance Intelligence',
      phaseNumber: 5,
      title: 'Price-Volume-Mix Variance Decomposition & SLA Credits',
      shortTitle: 'PVM Variance & SLA Credits',
      notebook: '10_cost_driver_and_variance_analysis.ipynb',
      pythonModule: 'src/tvi/variance.py',
      category: 'Value & Variance',
      badgeColor: 'rose',
      subpageUrl: '/technical-specs/value-variance',
      summary: 'Month-over-month algebraic cost variance decomposition into Rate, Volume, and Mix effects, statistical anomaly detection, and automated SLA credits.',
      executionDetails: [
        'Decomposes Month-over-Month cost shifts into three mathematically pure drivers: Price/Rate Effect, Volume Effect, and Mix Effect.',
        'Executes multi-level hierarchical rollups: Enterprise -> Business Unit -> IT Tower -> Application.',
        'Runs non-parametric Modified Z-Score anomaly detection (Median Absolute Deviation) and Isolation Forest classification.',
        'Calculates contractual SLA breach penalties and produces audit-ready FinOps vendor credit claim payloads.'
      ],
      formulaName: 'Algebraic Price-Volume-Mix Decomposition',
      formulaLatex: '\\Delta C = \\underbrace{\\sum (P_1 - P_0) V_0}_{\\text{Price Effect}} + \\underbrace{\\sum P_0 (V_1 - V_0)}_{\\text{Volume Effect}} + \\underbrace{\\sum (P_1 - P_0)(V_1 - V_0)}_{\\text{Mix / Interaction Effect}}',
      formulaHtml: '&Delta;<i>C</i> = <span class="math-term"><span class="math-brace">(<i>P</i><sub>1</sub> &minus; <i>P</i><sub>0</sub>)<i>V</i><sub>0</sub></span><span class="math-label">Price Effect</span></span> + <span class="math-term"><span class="math-brace"><i>P</i><sub>0</sub>(<i>V</i><sub>1</sub> &minus; <i>V</i><sub>0</sub>)</span><span class="math-label">Volume Effect</span></span> + <span class="math-term"><span class="math-brace">(<i>P</i><sub>1</sub> &minus; <i>P</i><sub>0</sub>)(<i>V</i><sub>1</sub> &minus; <i>V</i><sub>0</sub>)</span><span class="math-label">Mix Effect</span></span>',
      formulaExplanation: 'Reveals whether cloud invoice increases were driven by vendor price hikes, authentic business user growth, or inefficient resource configuration shifts.',
      inputContract: 'DuckDB cost_records & cloud_billing_records (multi-month)',
      outputContract: 'PVM variance waterfall breakdown & FinOps anomaly ticket payloads',
      latencySla: '< 7.8 ms variance rollup and anomaly pass',
      memoryBudget: '< 105 MB RAM',
      keyParameters: [
        { name: 'mad_threshold', value: '3.5', desc: 'Modified Z-score anomaly sensitivity' },
        { name: 'sla_penalty_floor', value: '99.9%', desc: 'Contractual uptime threshold' },
        { name: 'reconciliation_proof', value: 'Delta C = P + V + M (Exact)', desc: 'Zero unallocated variance' }
      ],
      codeSnippet: `def decompose_pvm_variance(p0, p1, v0, v1) -> PVMBreakdown:
    price_effect = (p1 - p0) * v0
    volume_effect = p0 * (v1 - v0)
    mix_effect = (p1 - p0) * (v1 - v0)
    total_delta = price_effect + volume_effect + mix_effect
    return PVMBreakdown(price=price_effect, volume=volume_effect, mix=mix_effect, total=total_delta)`
    },
    {
      id: 11,
      code: 'STEP-11',
      phase: 'Phase 6: Dual-Mode AI & Executive Decision Matrix',
      phaseNumber: 6,
      title: 'Dual-Mode AI Analyst & Zero-Hallucination Graph RAG',
      shortTitle: 'Dual-Mode AI Analyst',
      notebook: '11_local_llm_knowledge_graph_analyst.ipynb',
      pythonModule: 'src/tvi/llm.py',
      category: 'AI & Governance',
      badgeColor: 'lavender',
      subpageUrl: '/technical-specs/ai-governance',
      summary: 'Natural language graph analyst operating in dual modes: default zero-hallucination deterministic rules, and optional local Ollama SLM with strict AST grammar verification.',
      executionDetails: [
        'Default Mode: Deterministic intent matching with compiled regex and parameterized Cypher/SQL queries (sub-2ms, zero hallucination).',
        'Optional Mode: Local Ollama Small Language Model (Mistral 7B / Llama 3) running 100% on-device over REST API.',
        'Injects Graph RAG topological subgraphs into prompts, grounding responses in verified analytical truth.',
        'Enforces Analytical Guardrail 3: Strict AST query parsing and read-only database connections preventing prompt injection and SQL injection.'
      ],
      formulaName: 'Deterministic Grounded Intent Mapping',
      formulaLatex: '\\mathcal{Q}(\\text{Prompt}) \\xrightarrow{\\text{Regex / AST}} (\\text{Intent}, \\Theta) \\xrightarrow{\\text{Param Query}} \\text{DuckDB} \\times \\text{NetworkX} \\to \\text{Grounded Answer}',
      formulaHtml: '<span class="math-cal">Q</span>(Prompt) <span class="math-arrow">&xrarr;</span><sup>Regex / AST</sup> (Intent, &Theta;) <span class="math-arrow">&xrarr;</span><sup>Param Query</sup> DuckDB &times; NetworkX <span class="math-arrow">&xrarr;</span> Grounded Answer',
      formulaExplanation: 'Guarantees that no LLM hallucinated figures ever enter financial reports by constraining natural language queries to parameterized, verified analytical templates.',
      inputContract: 'User natural language query & in-memory graph G & DuckDB conn',
      outputContract: 'Validated JSON answer with entity lineage, SQL query string, and graph nodes',
      latencySla: '< 1.8 ms (Deterministic mode) / < 850 ms (Local Ollama mode)',
      memoryBudget: '< 50 MB (Rules) / 5.2 GB (Ollama SLM)',
      keyParameters: [
        { name: 'default_mode', value: 'deterministic', desc: 'Zero hallucination rules engine' },
        { name: 'temperature', value: '0.0', desc: 'Zero temperature for Ollama determinism' },
        { name: 'ast_validator', value: 'Read-Only (SELECT/MATCH only)', desc: 'Query injection firewall' }
      ],
      codeSnippet: `def handle_natural_language_query(query: str, db: TVIDatabase, G: nx.MultiDiGraph, mode='deterministic') -> QueryResult:
    intent, params = match_intent_rules(query)
    if intent == 'BLAST_RADIUS':
        return execute_blast_radius_query(params['app_id'], G)
    elif intent == 'CAPABILITY_TCO':
        return execute_capability_tco_query(params['cap_name'], db, G)
    raise UnrecognizedIntentError("Query routed to grounded parameter catalog.")`
    },
    {
      id: 12,
      code: 'STEP-12',
      phase: 'Phase 6: Dual-Mode AI & Executive Decision Matrix',
      phaseNumber: 6,
      title: 'Unified Technology Value Chain & 4-Tier Automated Validation',
      shortTitle: 'Unified Dossier & Validation',
      notebook: '12_end_to_end_technology_value_intelligence.ipynb',
      pythonModule: 'src/tvi/reporting.py & validation.py',
      category: 'AI & Governance',
      badgeColor: 'mint',
      subpageUrl: '/technical-specs/ai-governance',
      summary: 'End-to-end multi-hop enterprise dossier compilation, automated board-level markdown briefing generator, and 4-tier automated integrity validation.',
      executionDetails: [
        'Compiles the Unified Technology Value Chain dossier: General Ledger -> IT Towers -> Applications -> Capabilities -> Projects -> KPIs.',
        'Generates automated CIO / CFO board briefing reports in clean Markdown with executive decision matrices.',
        'Runs 4-Tier Automated Integrity Validation: Tier 1 Data Quality, Tier 2 Database Mass Balance, Tier 3 Graph Topology, Tier 4 Analytical Guardrails.',
        'Ensures full compliance with the zero-documentation-drift standard across the entire repository.'
      ],
      formulaName: '4-Tier Integrity Validation Function',
      formulaLatex: '\\mathcal{V} = \\mathcal{V}_{\\text{Data}} \\wedge \\mathcal{V}_{\\text{Database}} \\wedge \\mathcal{V}_{\\text{Graph}} \\wedge \\mathcal{V}_{\\text{Analytics}} \\equiv \\text{PASS} \\quad (83/83 \\text{ Tests})',
      formulaHtml: '<span class="math-cal">V</span> = <span class="math-cal">V</span><sub>Data</sub> &and; <span class="math-cal">V</span><sub>Database</sub> &and; <span class="math-cal">V</span><sub>Graph</sub> &and; <span class="math-cal">V</span><sub>Analytics</sub> &equiv; <span class="math-pass">PASS</span> &emsp;<span class="math-note">83/83 Tests Verified</span>',
      formulaExplanation: 'Validates that raw CSVs, DuckDB tables, NetworkX graph edges, and mathematical analytical outputs remain in unbroken referential and financial alignment.',
      inputContract: 'Entire repository state (CSVs, DuckDB, NetworkX, analytical modules)',
      outputContract: 'Executive Briefing Markdown report & 4-Tier Validation Audit Log',
      latencySla: '< 1.8 seconds complete portfolio synthesis',
      memoryBudget: '< 140 MB RAM',
      keyParameters: [
        { name: 'validation_tiers', value: '4 Tiers (Data, DB, Graph, Analytics)', desc: 'Continuous integrity suite' },
        { name: 'report_sections', value: '9 Executive Sections', desc: 'Board briefing template' },
        { name: 'pytest_suite', value: '83 automated tests', desc: '100% passing test coverage' }
      ],
      codeSnippet: `def run_four_tier_validation(db: TVIDatabase, G: nx.MultiDiGraph, config: Config) -> bool:
    v1 = validate_data_quality()
    v2 = validate_database_mass_balance(db)
    v3 = validate_graph_topology(G)
    v4 = validate_analytical_guardrails(db, G)
    return all([v1, v2, v3, v4])`
    }
  ]

  const phases = [
    {
      number: 1,
      name: 'Procedural Data Generation & Columnar OLAP',
      shortName: 'Data & OLAP',
      stepIds: [1, 2],
      badgeColor: 'mint',
      subpageUrl: '/technical-specs/data-pipeline',
      description: 'Procedural generation of 102 enterprise nodes with heavy-tailed distributions and Sklar copulas, ingested into DuckDB for zero-reconciliation OLAP mass-balance arithmetic.'
    },
    {
      number: 2,
      name: 'Semantic Knowledge Graph & Topology Traversal',
      shortName: 'Graph Topology',
      stepIds: [3, 8],
      badgeColor: 'lavender',
      subpageUrl: '/technical-specs/graph-topology',
      description: 'NetworkX typed property graph construction, Brandes betweenness centrality, DAG cycle validation, transitive closure reachability, and SPOF cascade failure simulation.'
    },
    {
      number: 3,
      name: '5-Layer TCO Stack & Proportional Attribution',
      shortName: 'Cost Attribution',
      stepIds: [4, 5],
      badgeColor: 'peach',
      subpageUrl: '/technical-specs/cost-attribution',
      description: '5-layer fully burdened Activity-Based Costing, FinOps unit economics, bipartite capability mapping, and weight conservation proofs eliminating attribution double-counting.'
    },
    {
      number: 4,
      name: 'Telemetry Profiling & TOPSIS MCDA Rationalization',
      shortName: 'Portfolio Rationalization',
      stepIds: [6, 7],
      badgeColor: 'sky',
      subpageUrl: '/technical-specs/portfolio-rationalization',
      description: 'Workload profiling, median-split 2x2 cost vs utilization quadrant segmentation, TOPSIS vector normalization, Gartner TIME placement, and contractual exit penalty models.'
    },
    {
      number: 5,
      name: 'TVR Value Realization & Price-Volume-Mix Variance',
      shortName: 'Value & Variance',
      stepIds: [9, 10],
      badgeColor: 'rose',
      subpageUrl: '/technical-specs/value-variance',
      description: 'Post-delivery benefit realization tracking, Difference-in-Differences causal econometrics, 3-factor PVM algebraic variance decomposition, and automated SLA credit claims.'
    },
    {
      number: 6,
      name: 'Dual-Mode AI Analyst & Executive Synthesis',
      shortName: 'AI & Governance',
      stepIds: [11, 12],
      badgeColor: 'lavender',
      subpageUrl: '/technical-specs/ai-governance',
      description: 'Zero-hallucination deterministic NL analyst with optional local Ollama SLM, Graph RAG grounding, AST query firewall, Unified Value Chain, and 4-tier automated integrity audit.'
    }
  ]

  return {
    steps,
    phases,
    systemArchitecture,
    hardwareBenchmarks
  }
}
