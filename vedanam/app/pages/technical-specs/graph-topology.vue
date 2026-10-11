<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCursor } from '~/composables/useCursor'
import { useAudioSynth } from '~/composables/useAudioSynth'
import FooterSection from '~/components/FooterSection.vue'
import MathFormula from '~/components/MathFormula.vue'

const { setCursor, resetCursor } = useCursor()
const { playInteractChime } = useAudioSynth()

// Interactive Blast Radius Simulator
interface SimNode {
  id: string
  name: string
  tier: string
  directDownstream: number
  transitiveReach: number
  downstreamTco: number
  betweenness: number
  pagerank: number
  spofStatus: boolean
  criticalityLevel: 'Catastrophic' | 'High' | 'Moderate' | 'Isolated'
}

const sampleNodes: SimNode[] = [
  {
    id: 'APP-010',
    name: 'Global Instant Payments Gateway',
    tier: 'Tier 1 (Mission Critical)',
    directDownstream: 9,
    transitiveReach: 24,
    downstreamTco: 6450000,
    betweenness: 0.184,
    pagerank: 0.042,
    spofStatus: true,
    criticalityLevel: 'Catastrophic'
  },
  {
    id: 'APP-001',
    name: 'Customer Core Banking Ledger',
    tier: 'Tier 1 (Mission Critical)',
    directDownstream: 6,
    transitiveReach: 18,
    downstreamTco: 4850000,
    betweenness: 0.142,
    pagerank: 0.038,
    spofStatus: false,
    criticalityLevel: 'High'
  },
  {
    id: 'APP-012',
    name: 'Omnichannel API Mesh Gateway',
    tier: 'Tier 1 (Mission Critical)',
    directDownstream: 8,
    transitiveReach: 21,
    downstreamTco: 3900000,
    betweenness: 0.165,
    pagerank: 0.035,
    spofStatus: false,
    criticalityLevel: 'High'
  },
  {
    id: 'APP-021',
    name: 'Document Archive Silo Matrix',
    tier: 'Tier 2 (Operational)',
    directDownstream: 1,
    transitiveReach: 3,
    downstreamTco: 280000,
    betweenness: 0.012,
    pagerank: 0.008,
    spofStatus: false,
    criticalityLevel: 'Moderate'
  },
  {
    id: 'APP-007',
    name: 'Legacy Regional CRM Zombie',
    tier: 'Tier 3 (Supporting)',
    directDownstream: 0,
    transitiveReach: 0,
    downstreamTco: 0,
    betweenness: 0.000,
    pagerank: 0.003,
    spofStatus: false,
    criticalityLevel: 'Isolated'
  }
]

const selectedNodeId = ref('APP-010')

const activeSimNode = computed(() => {
  return sampleNodes.find(n => n.id === selectedNodeId.value) || sampleNodes[0]
})

const selectNode = (id: string) => {
  selectedNodeId.value = id
  playInteractChime(1.25)
}
</script>

<template>
  <div class="subpage-wrapper">
    <div class="container subpage-container">
      <!-- Top Navigation -->
      <div class="subpage-nav-header">
        <NuxtLink
          to="/technical-specs"
          class="back-pill-link"
          @mouseenter="setCursor('ALL SPECS', 'default')"
          @mouseleave="resetCursor"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          <span>Back to Technical Specs Hub</span>
        </NuxtLink>
        <div class="step-indexer">
          <span class="pastel-chip chip-lavender">Phase 02</span>
          <span class="indexer-text">Steps 03 & 08 of 12</span>
        </div>
      </div>

      <!-- Hero Header -->
      <header class="subpage-hero">
        <span class="section-tag">Relationship Intelligence & Graph Theory</span>
        <h1 class="subpage-main-title">Graph Topology: Semantic Lineage, Centrality & Blast Radius</h1>
        <p class="subpage-lead">
          Relational SQL databases cannot efficiently navigate deep recursive dependencies without expensive table scans. TVI implements an in-memory typed semantic property graph in NetworkX to compute topological bottlenecks, detect circular dependency traps, and simulate cascading failure blast radii.
        </p>
      </header>

      <!-- Step 03 Section -->
      <section class="spec-detail-block" id="step-03">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 03</span>
          <span class="pastel-chip chip-lavender">Graph Construction</span>
          <span class="module-ref mono">src/tvi/graph.py & graph_queries.py</span>
        </div>
        <h2 class="block-heading">Typed Semantic Property Graph Construction & Lineage Traversal</h2>
        <p class="block-intro">
          The technology portfolio is modeled as a directed MultiDiGraph $G = (V, E)$ consisting of 102 vertices across 7 entity classes and 196 directed typed edges representing physical and contractual dependencies.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">3.1</div>
              <div class="wf-content">
                <h4>Ontology Schema Ingestion & Type Enforcement</h4>
                <p>
                  Loads <code>ontology.yaml</code> into an in-memory validation registry. Defines typed vertex categories: <code>Application</code>, <code>BusinessCapability</code>, <code>ITService</code>, <code>BusinessUnit</code>, <code>Vendor</code>, <code>Project</code>, and <code>KPI</code>.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">3.2</div>
              <div class="wf-content">
                <h4>MultiDiGraph Edge Assembly</h4>
                <p>
                  Populates directed edges: <code>DEPENDS_ON</code> (technical upstream calls), <code>PROVIDES</code> (capability enablement), <code>HOSTED_ON</code> (cloud infrastructure towers), <code>FUNDED_BY</code> (business unit cost centers), <code>DELIVERS</code> (transformation project outputs), and <code>TRACKS</code> (KPI benefit linkage).
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">3.3</div>
              <div class="wf-content">
                <h4>Topological Metric Computation (Brandes Betweenness & PageRank)</h4>
                <p>
                  Executes Brandes' algorithm in <span class="mono">O(|V| &middot; |E|)</span> to calculate shortest-path betweenness centrality for all nodes. Nodes with elevated betweenness represent enterprise architectural nexus points whose interruption causes disproportionate systemic friction.
                </p>
                <MathFormula
                  latex="C_B(v) = \sum_{s \neq v \neq t \in V} \frac{\sigma_{st}(v)}{\sigma_{st}}"
                  formula-html="<i>C</i><sub><i>B</i></sub>(<i>v</i>) = <span class='math-op'>&sum;</span><sub><i>s</i> &ne; <i>v</i> &ne; <i>t</i> &isin; <i>V</i></sub> <span class='math-frac'><span class='math-num'>&sigma;<sub><i>st</i></sub>(<i>v</i>)</span><span class='math-denom'>&sigma;<sub><i>st</i></sub></span></span>"
                  name="Brandes' Betweenness Centrality"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Step 08 Section -->
      <section class="spec-detail-block" id="step-08">
        <div class="block-badge-row">
          <span class="step-num-badge">STEP 08</span>
          <span class="pastel-chip chip-rose">Resilience Engineering</span>
          <span class="module-ref mono">src/tvi/dependency.py</span>
        </div>
        <h2 class="block-heading">Transitive Blast Radius, DAG Cycles & Single Points of Failure</h2>
        <p class="block-intro">
          When an IT team proposes to decommission or patch an enterprise application, they typically check immediate 1-hop dependencies. This "topological blindness" triggers catastrophic outages. Step 08 computes complete transitive reachability sets <i>R</i>(<i>u</i>) across arbitrary traversal depths.
        </p>

        <!-- Execution Sequence -->
        <div class="workflow-steps-box">
          <h3 class="wf-title">Execution Sequence (Step-by-Step Process)</h3>
          <div class="wf-timeline">
            <div class="wf-item">
              <div class="wf-num">8.1</div>
              <div class="wf-content">
                <h4>Acyclicity Validation via Tarjan SCC & Kahn's Sort</h4>
                <p>
                  The graph runs Tarjan's Strongly Connected Components (SCC) algorithm to verify that service invocation topologies contain zero circular dependency loops (<i>A</i> &rarr; <i>B</i> &rarr; <i>C</i> &rarr; <i>A</i>), guaranteeing clean topological sort order.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">8.2</div>
              <div class="wf-content">
                <h4>Transitive Closure Reachability Set Computation</h4>
                <p>
                  For every application <i>u</i> &isin; <i>V</i>, the engine executes a multi-hop Breadth-First Search (BFS) over incoming <code>DEPENDS_ON</code> edges to extract the complete reachability set <i>R</i>(<i>u</i>) = { <i>v</i> &isin; <i>V</i> | <i>u</i> &#8669; <i>v</i> }.
                </p>
              </div>
            </div>

            <div class="wf-item">
              <div class="wf-num">8.3</div>
              <div class="wf-content">
                <h4>Blast Radius Index (BRI) & Downstream Spend Calculation</h4>
                <p>
                  Computes the Blast Radius Index BRI(<i>u</i>) incorporating node count, criticality weights, and total downstream operational spend. Identifies Single Points of Failure (SPOFs) where a non-redundant component anchors critical revenue channels.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Interactive Blast Radius & SPOF Simulator -->
        <div class="interactive-tool-card">
          <div class="tool-header">
            <div class="tool-title-cluster">
              <span class="pastel-chip chip-rose">Interactive Outage Simulator</span>
              <h3>Transitive Blast Radius & Outage Cascade Simulator</h3>
            </div>
            <div class="node-select-pills">
              <button
                v-for="node in sampleNodes"
                :key="node.id"
                type="button"
                class="node-pill"
                :class="{ active: selectedNodeId === node.id }"
                @click="selectNode(node.id)"
              >
                <span>{{ node.id }}</span>
              </button>
            </div>
          </div>

          <div class="tool-body-grid">
            <div class="node-profile-panel">
              <div class="node-headline">
                <span class="node-id-chip">{{ activeSimNode.id }}</span>
                <h4>{{ activeSimNode.name }}</h4>
                <span class="node-tier">{{ activeSimNode.tier }}</span>
              </div>

              <div class="sim-metrics-grid">
                <div class="sim-metric-card">
                  <span class="k">Direct 1-Hop Impact</span>
                  <strong class="v">{{ activeSimNode.directDownstream }} nodes</strong>
                </div>
                <div class="sim-metric-card highlight-rose">
                  <span class="k">Transitive Blast Radius</span>
                  <strong class="v">{{ activeSimNode.transitiveReach }} nodes</strong>
                </div>
                <div class="sim-metric-card">
                  <span class="k">Downstream TCO at Risk</span>
                  <strong class="v">${{ (activeSimNode.downstreamTco / 1000000).toFixed(2) }}M</strong>
                </div>
                <div class="sim-metric-card">
                  <span class="k">Betweenness Centrality</span>
                  <strong class="v">{{ activeSimNode.betweenness.toFixed(3) }}</strong>
                </div>
              </div>

              <div v-if="activeSimNode.spofStatus" class="spof-alert-box">
                <span class="alert-icon">⚠️</span>
                <div>
                  <strong>CRITICAL SINGLE POINT OF FAILURE (SPOF) DETECTED</strong>
                  <p>
                    {{ activeSimNode.name }} anchors 24 dependent microservices across 3 business units with zero automated failover route. Decommissioning or uncoordinated patching will trigger a catastrophic enterprise cascade.
                  </p>
                </div>
              </div>
            </div>

            <div class="cascade-formula-panel">
              <MathFormula
                latex="\text{BRI}(u) = \frac{|R(u)|}{N - 1} \times \sum_{v \in R(u)} w_{\text{crit}}(v) \cdot \text{TCO}(v)"
                formula-html="BRI(<i>u</i>) = <span class='math-frac'><span class='math-num'>|<i>R</i>(<i>u</i>)|</span><span class='math-denom'><i>N</i> &minus; 1</span></span> &times; <span class='math-op'>&sum;</span><sub><i>v</i> &isin; <i>R</i>(<i>u</i>)</sub> <i>w</i><sub>crit</sub>(<i>v</i>) &middot; TCO(<i>v</i>)"
                name="Blast Radius Index (BRI) Formulation"
              />
              <p class="formula-expl">
                Where <i>R</i>(<i>u</i>) is the transitive reachability set, <i>N</i> = 102 is total network nodes, and <i>w</i><sub>crit</sub>(<i>v</i>) &isin; {3.0, 1.5, 1.0} represents mission criticality weighting.
              </p>
              <div class="spof-legend">
                <span class="leg-item"><span class="leg-dot red" /> Catastrophic: > 20 nodes or SPOF</span>
                <span class="leg-item"><span class="leg-dot yellow" /> High: 10 - 20 nodes</span>
                <span class="leg-item"><span class="leg-dot green" /> Isolated: < 2 nodes</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Bottom Navigation Cluster -->
      <div class="subpage-footer-nav">
        <NuxtLink to="/technical-specs/data-pipeline" class="nav-prev-btn">
          ← Previous: Data Pipeline & OLAP (Steps 01 & 02)
        </NuxtLink>
        <NuxtLink to="/technical-specs/cost-attribution" class="nav-next-btn">
          Next: 5-Layer Cost Stack & Capabilities (Steps 04 & 05) →
        </NuxtLink>
      </div>
    </div>

    <FooterSection />
  </div>
</template>

<style scoped>
.subpage-wrapper {
  padding-top: 7.5rem;
  background-color: var(--bg-canvas);
  min-height: 100vh;
}

.subpage-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0 var(--container-padding) 5rem;
}

.subpage-nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.back-pill-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 1.1rem;
  border-radius: var(--radius-pill);
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 0.84rem;
  font-weight: 600;
  color: #33363f;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.back-pill-link:hover {
  background: #ffffff;
  color: #121316;
  transform: translateX(-2px);
}

.step-indexer {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.indexer-text {
  font-size: 0.84rem;
  font-weight: 600;
  color: #6c7180;
}

.subpage-hero {
  max-width: 1050px;
  margin-bottom: 3.5rem;
}

.subpage-main-title {
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 4vw, 3.4rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: #121316;
  margin: 0.6rem 0 1rem;
}

.subpage-lead {
  font-size: 1.15rem;
  line-height: 1.65;
  color: #4b4f5d;
}

.spec-detail-block {
  background: #ffffff;
  border-radius: var(--radius-container);
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 12px 40px -10px rgba(0, 0, 0, 0.05);
  padding: 2.5rem;
  margin-bottom: 3.5rem;
}

.block-badge-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 1.2rem;
}

.step-num-badge {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  font-weight: 800;
  background: #17181d;
  color: #ffffff;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-pill);
}

.module-ref {
  font-size: 0.78rem;
  background: #f1f3f7;
  color: #474b59;
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-pill);
}

.block-heading {
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #121316;
  margin-bottom: 0.8rem;
}

.block-intro {
  font-size: 1.05rem;
  line-height: 1.65;
  color: #4c505f;
  margin-bottom: 2rem;
}

.workflow-steps-box {
  background: #fafafc;
  border: 1px solid #ebedf3;
  border-radius: 20px;
  padding: 1.85rem;
  margin-bottom: 2.25rem;
}

.wf-title {
  font-size: 1rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #121316;
  margin-bottom: 1.25rem;
}

.wf-timeline {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.wf-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.wf-num {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 800;
  background: #17181d;
  color: #ffffff;
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  flex-shrink: 0;
}

.wf-content h4 {
  font-size: 0.98rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.35rem;
}

.wf-content p {
  font-size: 0.92rem;
  line-height: 1.55;
  color: #555968;
}

.interactive-tool-card {
  background: #f7f8fb;
  border: 1px solid #e3e6ee;
  border-radius: 22px;
  padding: 1.85rem;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.tool-title-cluster h3 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #121316;
  margin-top: 0.3rem;
}

.node-select-pills {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.node-pill {
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-pill);
  border: 1px solid #dcdfe6;
  background: #ffffff;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  color: #4b4f5d;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.node-pill.active {
  background: #121316;
  color: #ffffff;
  border-color: #121316;
}

.tool-body-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 2rem;
}

.node-profile-panel {
  display: flex;
  flex-direction: column;
}

.node-headline {
  margin-bottom: 1.25rem;
}

.node-id-chip {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 700;
  background: #17181d;
  color: #ffffff;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-pill);
  display: inline-block;
  margin-bottom: 0.3rem;
}

.node-headline h4 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #121316;
}

.node-tier {
  font-size: 0.82rem;
  color: #7b8090;
}

.sim-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.sim-metric-card {
  background: #ffffff;
  border: 1px solid #e1e4eb;
  border-radius: 12px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
}

.sim-metric-card.highlight-rose {
  border-color: var(--pastel-rose);
  background: #fff5f6;
}

.sim-metric-card .k {
  font-size: 0.72rem;
  color: #787d8d;
}

.sim-metric-card .v {
  font-size: 1.15rem;
  color: #121316;
  margin-top: 0.2rem;
}

.spof-alert-box {
  display: flex;
  gap: 0.8rem;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 12px;
  padding: 1rem;
}

.alert-icon {
  font-size: 1.3rem;
}

.spof-alert-box strong {
  font-size: 0.85rem;
  color: #991b1b;
  display: block;
  margin-bottom: 0.2rem;
}

.spof-alert-box p {
  font-size: 0.8rem;
  line-height: 1.45;
  color: #7f1d1d;
}

.cascade-formula-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.cascade-formula-panel h4 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #121316;
  margin-bottom: 0.5rem;
}

.formula-box {
  background: #17181d;
  color: #c4b5fd;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
  overflow-x: auto;
}

.formula-expl {
  font-size: 0.84rem;
  line-height: 1.55;
  color: #555967;
  margin-bottom: 1.25rem;
}

.spof-legend {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #5a5f6e;
}

.leg-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.leg-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.leg-dot.red { background: #ef4444; }
.leg-dot.yellow { background: #f59e0b; }
.leg-dot.green { background: #10b981; }

.subpage-footer-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid #e4e7ee;
}

.nav-prev-btn, .nav-next-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.65rem 1.4rem;
  border-radius: var(--radius-pill);
  font-size: 0.88rem;
  font-weight: 700;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.nav-prev-btn {
  background: #ffffff;
  color: #3b3f4d;
  border: 1px solid #d8dbe2;
}

.nav-prev-btn:hover {
  background: #f1f3f7;
  color: #121316;
}

.nav-next-btn {
  background: #121316;
  color: #ffffff;
}

.nav-next-btn:hover {
  background: #2b2e38;
  transform: translateX(3px);
}

.mono {
  font-family: var(--font-mono);
}

@media (max-width: 900px) {
  .tool-body-grid {
    grid-template-columns: 1fr;
  }
}
</style>
