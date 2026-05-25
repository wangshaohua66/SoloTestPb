"""Citation graph builder and visualizer for CiteMaster."""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

from utils.logger import get_logger
from utils.config import Config
from utils.file_ops import FileManager
from core.models import CitationEntry

logger = get_logger()


@dataclass
class CitationNode:
    """Represents a node in the citation graph."""
    key: str
    title: str
    author: str
    year: Optional[int]
    citations: List[str] = field(default_factory=list)
    cited_by: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    entry_type: str = "misc"

    @property
    def citation_count(self) -> int:
        """Number of papers this paper cites."""
        return len(self.citations)

    @property
    def cited_by_count(self) -> int:
        """Number of papers that cite this paper."""
        return len(self.cited_by)

    @property
    def degree(self) -> int:
        """Total degree (in + out)."""
        return self.citation_count + self.cited_by_count


@dataclass
class CitationEdge:
    """Represents a directed edge in the citation graph."""
    from_key: str
    to_key: str
    weight: int = 1


@dataclass
class CitationGraph:
    """Represents the complete citation graph."""
    nodes: Dict[str, CitationNode] = field(default_factory=dict)
    edges: List[CitationEdge] = field(default_factory=list)
    adjacency_list: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    reverse_adjacency: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    def add_node(self, entry: CitationEntry) -> None:
        """Add a node to the graph from a CitationEntry."""
        node = CitationNode(
            key=entry.citation_key,
            title=entry.title,
            author=entry.author,
            year=entry.year,
            citations=list(entry.citations),
            cited_by=list(entry.cited_by),
            tags=list(entry.tags),
            entry_type=entry.entry_type
        )
        self.nodes[entry.citation_key] = node

    def add_edge(self, from_key: str, to_key: str) -> None:
        """Add a directed edge from from_key to to_key."""
        if from_key in self.nodes and to_key in self.nodes:
            edge = CitationEdge(from_key=from_key, to_key=to_key)
            self.edges.append(edge)
            self.adjacency_list[from_key].append(to_key)
            self.reverse_adjacency[to_key].append(from_key)

    def get_node(self, key: str) -> Optional[CitationNode]:
        """Get a node by key."""
        return self.nodes.get(key)

    def get_neighbors(self, key: str) -> List[str]:
        """Get all neighbors (citations and cited_by)."""
        neighbors = set()
        neighbors.update(self.adjacency_list.get(key, []))
        neighbors.update(self.reverse_adjacency.get(key, []))
        return list(neighbors)

    def get_citations(self, key: str) -> List[str]:
        """Get papers cited by the given paper."""
        return self.adjacency_list.get(key, [])

    def get_cited_by(self, key: str) -> List[str]:
        """Get papers that cite the given paper."""
        return self.reverse_adjacency.get(key, [])

    def find_path(self, start: str, end: str, max_depth: int = 5) -> List[str]:
        """Find a path between two nodes using BFS."""
        if start not in self.nodes or end not in self.nodes:
            return []

        if start == end:
            return [start]

        visited = {start}
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            for neighbor in self.get_neighbors(current):
                if neighbor == end:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []

    def get_connected_components(self) -> List[Set[str]]:
        """Find all connected components in the graph."""
        visited = set()
        components = []

        for key in self.nodes:
            if key not in visited:
                component = set()
                queue = [key]

                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue

                    visited.add(current)
                    component.add(current)

                    for neighbor in self.get_neighbors(current):
                        if neighbor not in visited:
                            queue.append(neighbor)

                components.append(component)

        return sorted(components, key=len, reverse=True)

    def get_top_cited(self, n: int = 10) -> List[CitationNode]:
        """Get the top n most cited papers."""
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda node: node.cited_by_count,
            reverse=True
        )
        return sorted_nodes[:n]

    def get_top_citing(self, n: int = 10) -> List[CitationNode]:
        """Get the top n papers that cite the most others."""
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda node: node.citation_count,
            reverse=True
        )
        return sorted_nodes[:n]

    def get_isolated_nodes(self) -> List[CitationNode]:
        """Get nodes with no citations or cited_by relations."""
        return [
            node for node in self.nodes.values()
            if node.degree == 0
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the graph."""
        if not self.nodes:
            return {
                "total_nodes": 0,
                "total_edges": 0,
                "connected_components": 0,
                "avg_degree": 0,
                "max_degree": 0,
                "isolated_nodes": 0,
                "top_cited": [],
                "top_citing": []
            }

        degrees = [node.degree for node in self.nodes.values()]
        components = self.get_connected_components()

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "connected_components": len(components),
            "avg_degree": sum(degrees) / len(degrees),
            "max_degree": max(degrees) if degrees else 0,
            "isolated_nodes": len(self.get_isolated_nodes()),
            "largest_component_size": len(components[0]) if components else 0,
            "top_cited": [(n.key, n.cited_by_count) for n in self.get_top_cited(5)],
            "top_citing": [(n.key, n.citation_count) for n in self.get_top_citing(5)]
        }


class GraphBuilder:
    """Builds and visualizes citation graphs."""

    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Citation Graph - CiteMaster</title>
    <style>
        .error-banner {
            display: none;
            background: #e74c3c;
            color: white;
            padding: 15px 20px;
            text-align: center;
            border-bottom: 2px solid #c0392b;
        }
        .error-banner.show {
            display: block;
        }
        .fallback-container {
            display: none;
            padding: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .fallback-container.show {
            display: block;
        }
        .fallback-section {
            background: #0f3460;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .fallback-section h3 {
            color: #e94560;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #533483;
        }
        .fallback-paper {
            background: #16213e;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #533483;
        }
        .fallback-paper.high-cited {
            border-left-color: #e94560;
        }
        .fallback-paper.isolated {
            border-left-color: #f39c12;
        }
        .fallback-paper h4 {
            margin: 0 0 8px 0;
            color: #fff;
            font-size: 14px;
        }
        .fallback-paper .meta {
            color: #aaa;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .fallback-paper .relations {
            font-size: 11px;
            color: #888;
        }
        .fallback-paper .relations span {
            display: inline-block;
            background: #533483;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 8px;
            margin-top: 4px;
        }
        .retry-btn {
            background: #e94560;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
            font-size: 12px;
        }
        .retry-btn:hover {
            background: #d63850;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #888;
        }
        .loading.show {
            display: block;
        }
        .offline-notice {
            background: #f39c12;
            color: #1a1a2e;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 13px;
            display: none;
        }
        .offline-notice.show {
            display: block;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        .header {
            padding: 20px;
            background: #16213e;
            border-bottom: 1px solid #0f3460;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .stats {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        .stat-item {
            background: #0f3460;
            padding: 10px 20px;
            border-radius: 8px;
        }
        .stat-label {
            font-size: 12px;
            color: #aaa;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #e94560;
        }
        #graph-container {
            width: 100%;
            height: calc(100vh - 120px);
            position: relative;
        }
        .tooltip {
            position: absolute;
            background: rgba(15, 52, 96, 0.95);
            padding: 15px;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 350px;
            border: 1px solid #e94560;
            z-index: 1000;
        }
        .tooltip h3 {
            font-size: 14px;
            margin-bottom: 8px;
            color: #e94560;
        }
        .tooltip p {
            font-size: 12px;
            margin-bottom: 5px;
            line-height: 1.4;
        }
        .node {
            cursor: pointer;
            transition: stroke-width 0.2s;
        }
        .node:hover {
            stroke-width: 3px;
        }
        .link {
            stroke: #533483;
            stroke-opacity: 0.6;
            transition: stroke-opacity 0.2s;
        }
        .link:hover {
            stroke-opacity: 1;
        }
        .node-label {
            font-size: 9px;
            fill: #fff;
            pointer-events: none;
            text-shadow: 0 0 3px #000;
        }
        .legend {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(15, 52, 96, 0.9);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
        }
        .legend-color {
            width: 15px;
            height: 15px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="error-banner" id="error-banner">
        ⚠️ D3.js library failed to load. Network connection may be unavailable.
        <button class="retry-btn" onclick="location.reload()">Retry</button>
    </div>
    <div class="header">
        <h1>📚 Citation Graph Visualization</h1>
        <div class="offline-notice" id="offline-notice">
            🔌 Offline mode - Showing static view. Connect to internet and refresh for interactive graph.
        </div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Total Papers</div>
                <div class="stat-value" id="total-nodes">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Citations</div>
                <div class="stat-value" id="total-edges">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Avg Connections</div>
                <div class="stat-value" id="avg-degree">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Components</div>
                <div class="stat-value" id="components">0</div>
            </div>
        </div>
    </div>
    <div id="graph-container">
        <div class="tooltip" id="tooltip"></div>
        <div class="loading" id="loading">
            <div style="font-size: 18px; margin-bottom: 10px;">⏳ Loading interactive graph...</div>
            <div style="font-size: 13px; color: #888;">If this takes too long, check your network connection</div>
        </div>
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #e94560;"></div>
                <span>Highly cited (≥5)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #533483;"></div>
                <span>Moderately cited</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #0f3460;"></div>
                <span>Low cited</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f39c12;"></div>
                <span>Isolated</span>
            </div>
        </div>
    </div>
    <div class="fallback-container" id="fallback-container">
        <div class="fallback-section">
            <h3>📄 All Papers ({TOTAL_NODES})</h3>
            {FALLBACK_PAPERS}
        </div>
        <div class="fallback-section">
            <h3>🔗 Citation Relations ({TOTAL_EDGES})</h3>
            {FALLBACK_EDGES}
        </div>
    </div>

    <script>
        const graphData = {GRAPH_DATA};

        document.getElementById('total-nodes').textContent = graphData.summary.total_nodes;
        document.getElementById('total-edges').textContent = graphData.summary.total_edges;
        document.getElementById('avg-degree').textContent = graphData.summary.avg_degree.toFixed(1);
        document.getElementById('components').textContent = graphData.summary.connected_components;

        function showOfflineMode(message) {
            document.getElementById('error-banner').classList.add('show');
            document.getElementById('offline-notice').classList.add('show');
            document.getElementById('graph-container').style.display = 'none';
            document.getElementById('fallback-container').classList.add('show');
            if (message) {
                document.getElementById('error-banner').innerHTML =
                    '⚠️ ' + message + ' <button class="retry-btn" onclick="location.reload()">Retry</button>';
            }
            console.warn('D3.js not available, showing offline fallback view');
        }

        function showInteractiveMode() {
            document.getElementById('loading').classList.remove('show');
            document.getElementById('graph-container').style.display = 'block';
        }

        function loadD3(callback) {
            if (typeof d3 !== 'undefined') {
                callback(null, d3);
                return;
            }

            document.getElementById('loading').classList.add('show');
            const script = document.createElement('script');
            script.src = 'https://d3js.org/d3.v7.min.js';
            script.onload = function() {
                callback(null, d3);
            };
            script.onerror = function() {
                callback(new Error('Failed to load D3.js from CDN'), null);
            };
            document.head.appendChild(script);

            setTimeout(function() {
                if (typeof d3 === 'undefined') {
                    callback(new Error('D3.js loading timed out after 10 seconds'), null);
                }
            }, 10000);
        }

        function initializeGraph(d3) {
            const container = document.getElementById('graph-container');
            const width = container.clientWidth;
            const height = container.clientHeight;

            const svg = d3.select('#graph-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const tooltip = d3.select('#tooltip');

            const defs = svg.append('defs');
            defs.append('marker')
                .attr('id', 'arrowhead')
                .attr('viewBox', '-0 -5 10 10')
                .attr('refX', 25)
                .attr('refY', 0)
                .attr('orient', 'auto')
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .append('path')
                .attr('d', 'M 0,-5 L 10,0 L 0,5')
                .attr('fill', '#533483')
                .attr('fill-opacity', 0.6);

            const getNodeColor = (node) => {
                if (node.cited_by_count === 0 && node.citation_count === 0) return '#f39c12';
                if (node.cited_by_count >= 5) return '#e94560';
                if (node.cited_by_count >= 2) return '#533483';
                return '#0f3460';
            };

            const getNodeRadius = (node) => {
                return Math.max(8, Math.min(30, 8 + node.cited_by_count * 2));
            };

            const simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.edges).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => getNodeRadius(d) + 5));

            const link = svg.append('g')
                .selectAll('line')
                .data(graphData.edges)
                .enter().append('line')
                .attr('class', 'link')
                .attr('marker-end', 'url(#arrowhead)')
                .attr('stroke-width', d => Math.max(1, Math.min(3, d.weight)));

            const node = svg.append('g')
                .selectAll('circle')
                .data(graphData.nodes)
                .enter().append('circle')
                .attr('class', 'node')
                .attr('r', d => getNodeRadius(d))
                .attr('fill', d => getNodeColor(d))
                .attr('stroke', '#fff')
                .attr('stroke-width', 1.5)
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            const label = svg.append('g')
                .selectAll('text')
                .data(graphData.nodes)
                .enter().append('text')
                .attr('class', 'node-label')
                .attr('text-anchor', 'middle')
                .attr('dy', d => -getNodeRadius(d) - 5)
                .text(d => d.label);

            node.on('mouseover', (event, d) => {
                tooltip.style('opacity', 1)
                    .html(`
                        <h3>${d.title}</h3>
                        <p><strong>Author:</strong> ${d.author}</p>
                        <p><strong>Year:</strong> ${d.year || 'N/A'}</p>
                        <p><strong>Type:</strong> ${d.entry_type}</p>
                        <p><strong>Cites:</strong> ${d.citation_count} papers</p>
                        <p><strong>Cited by:</strong> ${d.cited_by_count} papers</p>
                        ${d.tags.length > 0 ? `<p><strong>Tags:</strong> ${d.tags.join(', ')}</p>` : ''}
                    `)
                    .style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', () => {
                tooltip.style('opacity', 0);
            });

            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }

            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });

            window.addEventListener('resize', () => {
                const newWidth = container.clientWidth;
                const newHeight = container.clientHeight;
                svg.attr('width', newWidth).attr('height', newHeight);
                simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
                simulation.alpha(0.3).restart();
            });

            showInteractiveMode();
        }

        loadD3(function(err, d3) {
            if (err) {
                showOfflineMode(err.message);
            } else {
                try {
                    initializeGraph(d3);
                } catch (e) {
                    console.error('Failed to initialize graph:', e);
                    showOfflineMode('Failed to render interactive graph');
                }
            }
        });
    </script>
</body>
</html>
"""

    def __init__(self, config: Config):
        self.config = config
        self.file_manager = FileManager(config)

    def build_graph(self, entries: List[CitationEntry]) -> CitationGraph:
        """Build a citation graph from a list of entries."""
        try:
            graph = CitationGraph()

            valid_keys = {e.citation_key for e in entries}

            for entry in entries:
                graph.add_node(entry)

            for entry in entries:
                for cited_key in entry.citations:
                    if cited_key in valid_keys:
                        graph.add_edge(entry.citation_key, cited_key)
                    else:
                        logger.debug(f"Citation target '{cited_key}' not in library for entry '{entry.citation_key}'")

            logger.info(f"Built citation graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
            return graph

        except Exception as e:
            logger.exception("Failed to build citation graph", e)
            raise Exception(f"Failed to build citation graph: {e}")

    def export_graph_json(self, graph: CitationGraph, output_path: Optional[Path] = None) -> Path:
        """Export graph data to JSON for visualization."""
        try:
            output_path = Path(output_path) if output_path else Path(
                self.config.get("graph_output_path", "data/citation_graph.json")
            )

            nodes_data = []
            for key, node in graph.nodes.items():
                short_label = node.author.split(',')[0] if node.author else "Unknown"
                if node.year:
                    short_label += f" ({node.year})"
                else:
                    short_label += " (n.d.)"

                nodes_data.append({
                    "id": key,
                    "title": node.title,
                    "author": node.author,
                    "year": node.year,
                    "label": short_label,
                    "entry_type": node.entry_type,
                    "citation_count": node.citation_count,
                    "cited_by_count": node.cited_by_count,
                    "tags": node.tags
                })

            edges_data = []
            for edge in graph.edges:
                edges_data.append({
                    "source": edge.from_key,
                    "target": edge.to_key,
                    "weight": edge.weight
                })

            data = {
                "nodes": nodes_data,
                "edges": edges_data,
                "summary": graph.get_summary()
            }

            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_manager.write_json(output_path, data)

            logger.info(f"Exported graph JSON to {output_path}")
            return output_path

        except Exception as e:
            logger.exception("Failed to export graph JSON", e)
            raise Exception(f"Failed to export graph JSON: {e}")

    def visualize(self, graph: CitationGraph, output_path: Optional[Path] = None) -> Path:
        """Generate an interactive HTML visualization of the citation graph."""
        try:
            output_path = Path(output_path) if output_path else Path(
                self.config.get("graph_output_path", "data/citation_graph.html")
            )

            json_path = output_path.with_suffix('.json')
            self.export_graph_json(graph, json_path)

            nodes_data = []
            for key, node in graph.nodes.items():
                short_label = node.author.split(',')[0] if node.author else "Unknown"
                if node.year:
                    short_label += f" ({node.year})"
                else:
                    short_label += " (n.d.)"

                nodes_data.append({
                    "id": key,
                    "title": node.title,
                    "author": node.author,
                    "year": node.year,
                    "label": short_label,
                    "entry_type": node.entry_type,
                    "citation_count": node.citation_count,
                    "cited_by_count": node.cited_by_count,
                    "tags": node.tags
                })

            edges_data = []
            for edge in graph.edges:
                edges_data.append({
                    "source": edge.from_key,
                    "target": edge.to_key,
                    "weight": edge.weight
                })

            graph_data = {
                "nodes": nodes_data,
                "edges": edges_data,
                "summary": graph.get_summary()
            }

            import json
            graph_json = json.dumps(graph_data, indent=2)

            fallback_papers = self._generate_fallback_papers(nodes_data)
            fallback_edges = self._generate_fallback_edges(edges_data, nodes_data)

            html_content = self.HTML_TEMPLATE.replace("{GRAPH_DATA}", graph_json)
            html_content = html_content.replace("{TOTAL_NODES}", str(len(nodes_data)))
            html_content = html_content.replace("{TOTAL_EDGES}", str(len(edges_data)))
            html_content = html_content.replace("{FALLBACK_PAPERS}", fallback_papers)
            html_content = html_content.replace("{FALLBACK_EDGES}", fallback_edges)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_manager.write_text(output_path, html_content)

            logger.info(f"Generated citation graph visualization at {output_path}")
            return output_path

        except Exception as e:
            logger.exception("Failed to generate graph visualization", e)
            raise Exception(f"Failed to generate graph visualization: {e}")

    def _generate_fallback_papers(self, nodes_data: List[Dict]) -> str:
        """Generate HTML for offline fallback paper list."""
        if not nodes_data:
            return '<p style="color: #888;">No papers in library.</p>'

        sorted_nodes = sorted(
            nodes_data,
            key=lambda n: n.get('cited_by_count', 0),
            reverse=True
        )

        papers_html = []
        for node in sorted_nodes:
            cited = node.get('cited_by_count', 0)
            citations = node.get('citation_count', 0)
            is_isolated = cited == 0 and citations == 0
            is_high_cited = cited >= 5

            classes = ['fallback-paper']
            if is_high_cited:
                classes.append('high-cited')
            elif is_isolated:
                classes.append('isolated')

            relations = []
            if cited > 0:
                relations.append(f'<span>📥 Cited by: {cited}</span>')
            if citations > 0:
                relations.append(f'<span>📤 Cites: {citations}</span>')
            if is_isolated:
                relations.append('<span style="background: #f39c12; color: #1a1a2e;">🔒 Isolated</span>')

            year_str = str(node.get('year', 'n.d.'))
            title = node.get('title', 'Untitled')
            author = node.get('author', 'Unknown')

            paper_html = f'''
            <div class="{' '.join(classes)}">
                <h4>{title}</h4>
                <div class="meta">{author} • {year_str} • {node.get('entry_type', 'misc')}</div>
                <div class="relations">{' '.join(relations)}</div>
            </div>
            '''
            papers_html.append(paper_html)

        return '\n'.join(papers_html)

    def _generate_fallback_edges(self, edges_data: List[Dict], nodes_data: List[Dict]) -> str:
        """Generate HTML for offline fallback citation relations."""
        if not edges_data:
            return '<p style="color: #888;">No citation relations defined.</p>'

        node_map = {n['id']: n for n in nodes_data}

        edges_html = []
        for edge in edges_data:
            source = node_map.get(edge['source'], {})
            target = node_map.get(edge['target'], {})

            source_label = source.get('label', edge['source'])
            target_label = target.get('label', edge['target'])

            edge_html = f'''
            <div class="fallback-paper">
                <h4>🔗 {source_label} → {target_label}</h4>
                <div class="meta">{source.get('title', edge['source'])}</div>
                <div class="relations">
                    <span>cites</span>
                    <span>{target.get('title', edge['target'])}</span>
                </div>
            </div>
            '''
            edges_html.append(edge_html)

        return '\n'.join(edges_html)

    def generate_text_graph(self, graph: CitationGraph, max_depth: int = 2) -> str:
        """Generate a text-based representation of the citation graph."""
        lines = []
        lines.append("=" * 60)
        lines.append("Citation Graph Overview")
        lines.append("=" * 60)

        summary = graph.get_summary()
        lines.append(f"Total papers: {summary['total_nodes']}")
        lines.append(f"Total citations: {summary['total_edges']}")
        lines.append(f"Connected components: {summary['connected_components']}")
        lines.append(f"Average connections: {summary['avg_degree']:.2f}")
        lines.append("")

        if summary['top_cited']:
            lines.append("Top Cited Papers:")
            lines.append("-" * 60)
            for key, count in summary['top_cited']:
                node = graph.get_node(key)
                if node:
                    lines.append(f"  [{count} citations] {node.author} ({node.year})")
                    lines.append(f"      {node.title[:60]}...")
            lines.append("")

        components = graph.get_connected_components()
        if len(components) > 1:
            lines.append(f"Connected Components ({len(components)}):")
            lines.append("-" * 60)
            for i, comp in enumerate(components[:5], 1):
                sample = list(comp)[:3]
                lines.append(f"  Component {i}: {len(comp)} papers")
                for key in sample:
                    node = graph.get_node(key)
                    if node:
                        lines.append(f"    - {node.author.split(',')[0]} ({node.year})")
                if len(comp) > 3:
                    lines.append(f"    ... and {len(comp) - 3} more")
            lines.append("")

        isolated = graph.get_isolated_nodes()
        if isolated:
            lines.append(f"Isolated Papers ({len(isolated)}):")
            lines.append("-" * 60)
            for node in isolated[:10]:
                lines.append(f"  - {node.author.split(',')[0]} ({node.year}): {node.title[:50]}...")
            if len(isolated) > 10:
                lines.append(f"  ... and {len(isolated) - 10} more")
            lines.append("")

        lines.append("Citation Network (top 10 most connected):")
        lines.append("-" * 60)
        top_connected = sorted(
            graph.nodes.values(),
            key=lambda n: n.degree,
            reverse=True
        )[:10]

        for node in top_connected:
            if node.degree == 0:
                continue
            lines.append(f"  {node.author.split(',')[0]} ({node.year}) [degree: {node.degree}]")
            if node.citations:
                cited = node.citations[:3]
                lines.append(f"    Cites: {', '.join(cited)}{'...' if len(node.citations) > 3 else ''}")
            if node.cited_by:
                cited_by = node.cited_by[:3]
                lines.append(f"    Cited by: {', '.join(cited_by)}{'...' if len(node.cited_by) > 3 else ''}")

        return "\n".join(lines)
