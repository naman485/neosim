"""
Web Analyzer

Analyzes landing pages, API docs, and MCP tools to assess execution quality.
Conversion depends heavily on execution, not just positioning.
"""

import os
import json
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import httpx


@dataclass
class LandingPageAnalysis:
    """Analysis of a landing page for conversion factors."""
    url: str
    score: float  # 0-10 overall score

    # Component scores (0-10)
    headline_clarity: float = 5.0
    value_prop_strength: float = 5.0
    cta_effectiveness: float = 5.0
    trust_signals: float = 5.0
    pricing_clarity: float = 5.0
    visual_design: float = 5.0
    mobile_ready: float = 5.0
    load_speed: float = 5.0

    # Qualitative findings
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Raw data
    title: str = ""
    meta_description: str = ""
    h1_text: str = ""
    cta_texts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "score": self.score,
            "components": {
                "headline_clarity": self.headline_clarity,
                "value_prop_strength": self.value_prop_strength,
                "cta_effectiveness": self.cta_effectiveness,
                "trust_signals": self.trust_signals,
                "pricing_clarity": self.pricing_clarity,
                "visual_design": self.visual_design,
                "mobile_ready": self.mobile_ready,
                "load_speed": self.load_speed,
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
        }


@dataclass
class APIDocsAnalysis:
    """Analysis of API documentation quality."""
    url: str
    score: float  # 0-10 overall score

    # Component scores
    completeness: float = 5.0
    clarity: float = 5.0
    examples_quality: float = 5.0
    quickstart_exists: float = 5.0
    error_handling_docs: float = 5.0

    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "score": self.score,
            "components": {
                "completeness": self.completeness,
                "clarity": self.clarity,
                "examples_quality": self.examples_quality,
                "quickstart_exists": self.quickstart_exists,
                "error_handling_docs": self.error_handling_docs,
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


@dataclass
class MCPAnalysis:
    """Analysis of MCP tool integration quality."""
    tool_definition_url: str
    score: float  # 0-10 overall score

    # Component scores
    tool_naming: float = 5.0
    input_schema_quality: float = 5.0
    description_clarity: float = 5.0
    error_messages: float = 5.0

    tools_found: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.tool_definition_url,
            "score": self.score,
            "tools_found": self.tools_found,
            "issues": self.issues,
        }


@dataclass
class ExecutionQualityScore:
    """Combined execution quality assessment."""
    landing_page: Optional[LandingPageAnalysis] = None
    api_docs: Optional[APIDocsAnalysis] = None
    mcp: Optional[MCPAnalysis] = None

    @property
    def overall_score(self) -> float:
        """Weighted average of all available scores."""
        scores = []
        weights = []

        if self.landing_page:
            scores.append(self.landing_page.score)
            weights.append(3)  # Landing page is most important for conversion
        if self.api_docs:
            scores.append(self.api_docs.score)
            weights.append(2)
        if self.mcp:
            scores.append(self.mcp.score)
            weights.append(1)

        if not scores:
            return 5.0  # Default middle score

        return sum(s * w for s, w in zip(scores, weights)) / sum(weights)

    @property
    def conversion_multiplier(self) -> float:
        """
        Multiplier to apply to conversion predictions.

        Score 10 = 1.5x (excellent execution boosts conversion)
        Score 5 = 1.0x (average, no adjustment)
        Score 0 = 0.3x (poor execution tanks conversion)
        """
        score = self.overall_score
        if score >= 8:
            return 1.2 + (score - 8) * 0.15  # 1.2 to 1.5
        elif score >= 5:
            return 1.0 + (score - 5) * 0.067  # 1.0 to 1.2
        else:
            return 0.3 + score * 0.14  # 0.3 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "conversion_multiplier": self.conversion_multiplier,
            "landing_page": self.landing_page.to_dict() if self.landing_page else None,
            "api_docs": self.api_docs.to_dict() if self.api_docs else None,
            "mcp": self.mcp.to_dict() if self.mcp else None,
        }


class WebAnalyzer:
    """
    Analyzes web presence for execution quality.

    Uses Claude to evaluate landing pages, docs, and integrations.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = httpx.Client(timeout=30.0)

    def analyze_landing_page(self, url: str) -> LandingPageAnalysis:
        """Fetch and analyze a landing page for conversion factors."""
        # Fetch the page
        try:
            response = self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            html = response.text
            load_time = response.elapsed.total_seconds()
        except Exception as e:
            return LandingPageAnalysis(
                url=url,
                score=0.0,
                weaknesses=[f"Could not fetch page: {str(e)}"],
            )

        # Extract basic elements
        title = self._extract_tag(html, "title")
        meta_desc = self._extract_meta(html, "description")
        h1 = self._extract_tag(html, "h1")
        ctas = self._extract_ctas(html)

        # Analyze with Claude
        analysis = self._analyze_with_llm(url, html, title, meta_desc, h1, ctas, load_time)

        return analysis

    def analyze_api_docs(self, url: str) -> APIDocsAnalysis:
        """Analyze API documentation quality."""
        try:
            response = self.client.get(url, follow_redirects=True)
            response.raise_for_status()
            content = response.text
        except Exception as e:
            return APIDocsAnalysis(
                url=url,
                score=0.0,
                weaknesses=[f"Could not fetch docs: {str(e)}"],
            )

        return self._analyze_docs_with_llm(url, content)

    def analyze_mcp(self, url: str) -> MCPAnalysis:
        """Analyze MCP tool definition quality."""
        try:
            response = self.client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Try to parse as JSON
            try:
                mcp_def = response.json()
            except:
                mcp_def = {"raw": response.text[:2000]}

        except Exception as e:
            return MCPAnalysis(
                tool_definition_url=url,
                score=0.0,
                issues=[f"Could not fetch MCP definition: {str(e)}"],
            )

        return self._analyze_mcp_with_llm(url, mcp_def)

    def _extract_tag(self, html: str, tag: str) -> str:
        """Extract first occurrence of a tag's content."""
        pattern = f"<{tag}[^>]*>([^<]*)</{tag}>"
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_meta(self, html: str, name: str) -> str:
        """Extract meta tag content."""
        pattern = f'<meta[^>]*name=["\']?{name}["\']?[^>]*content=["\']([^"\']*)["\']'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
        # Try alternate format
        pattern = f'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']?{name}["\']?'
        match = re.search(pattern, html, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_ctas(self, html: str) -> List[str]:
        """Extract CTA button texts."""
        ctas = []
        # Find buttons
        button_pattern = r'<button[^>]*>([^<]+)</button>'
        ctas.extend(re.findall(button_pattern, html, re.IGNORECASE))

        # Find links that look like CTAs
        cta_link_pattern = r'<a[^>]*class="[^"]*(?:btn|button|cta)[^"]*"[^>]*>([^<]+)</a>'
        ctas.extend(re.findall(cta_link_pattern, html, re.IGNORECASE))

        return [c.strip() for c in ctas if c.strip()][:10]

    def _analyze_with_llm(
        self,
        url: str,
        html: str,
        title: str,
        meta_desc: str,
        h1: str,
        ctas: List[str],
        load_time: float
    ) -> LandingPageAnalysis:
        """Use Claude to analyze landing page."""
        if not self.api_key:
            # Return basic analysis without LLM
            return self._basic_analysis(url, title, meta_desc, h1, ctas, load_time)

        # Truncate HTML to avoid token limits
        html_excerpt = html[:15000] if len(html) > 15000 else html

        prompt = f"""Analyze this landing page for conversion optimization.

URL: {url}
Title: {title}
Meta Description: {meta_desc}
H1: {h1}
CTA Buttons Found: {', '.join(ctas[:5]) if ctas else 'None found'}
Load Time: {load_time:.2f}s

HTML Excerpt:
{html_excerpt}

Score each factor 0-10 and provide analysis:

Respond with JSON:
```json
{{
    "headline_clarity": <0-10>,
    "value_prop_strength": <0-10>,
    "cta_effectiveness": <0-10>,
    "trust_signals": <0-10>,
    "pricing_clarity": <0-10>,
    "visual_design": <0-10>,
    "mobile_ready": <0-10>,
    "load_speed": <0-10>,
    "overall_score": <0-10>,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["fix 1", "fix 2"]
}}
```"""

        try:
            response = self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "temperature": 0.3,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            result = response.json()["content"][0]["text"]

            # Parse JSON from response
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return LandingPageAnalysis(
                    url=url,
                    score=data.get("overall_score", 5.0),
                    headline_clarity=data.get("headline_clarity", 5.0),
                    value_prop_strength=data.get("value_prop_strength", 5.0),
                    cta_effectiveness=data.get("cta_effectiveness", 5.0),
                    trust_signals=data.get("trust_signals", 5.0),
                    pricing_clarity=data.get("pricing_clarity", 5.0),
                    visual_design=data.get("visual_design", 5.0),
                    mobile_ready=data.get("mobile_ready", 5.0),
                    load_speed=data.get("load_speed", 5.0),
                    strengths=data.get("strengths", []),
                    weaknesses=data.get("weaknesses", []),
                    recommendations=data.get("recommendations", []),
                    title=title,
                    meta_description=meta_desc,
                    h1_text=h1,
                    cta_texts=ctas,
                )
        except Exception as e:
            pass

        return self._basic_analysis(url, title, meta_desc, h1, ctas, load_time)

    def _basic_analysis(
        self,
        url: str,
        title: str,
        meta_desc: str,
        h1: str,
        ctas: List[str],
        load_time: float
    ) -> LandingPageAnalysis:
        """Basic heuristic analysis without LLM."""
        strengths = []
        weaknesses = []
        score = 5.0

        # Check title
        if title and len(title) > 10:
            strengths.append("Has descriptive title")
            score += 0.5
        else:
            weaknesses.append("Missing or weak title")
            score -= 0.5

        # Check meta description
        if meta_desc and len(meta_desc) > 50:
            strengths.append("Has meta description")
            score += 0.5
        else:
            weaknesses.append("Missing meta description")
            score -= 0.5

        # Check H1
        if h1:
            strengths.append("Has H1 headline")
            score += 0.5
        else:
            weaknesses.append("Missing H1 headline")
            score -= 0.5

        # Check CTAs
        if ctas:
            strengths.append(f"Found {len(ctas)} CTAs")
            score += 0.5
        else:
            weaknesses.append("No clear CTAs found")
            score -= 1.0

        # Check load time
        if load_time < 2:
            strengths.append(f"Fast load time ({load_time:.1f}s)")
            score += 0.5
        elif load_time > 5:
            weaknesses.append(f"Slow load time ({load_time:.1f}s)")
            score -= 1.0

        return LandingPageAnalysis(
            url=url,
            score=max(0, min(10, score)),
            title=title,
            meta_description=meta_desc,
            h1_text=h1,
            cta_texts=ctas,
            strengths=strengths,
            weaknesses=weaknesses,
            load_speed=10.0 if load_time < 1 else max(0, 10 - load_time),
        )

    def _analyze_docs_with_llm(self, url: str, content: str) -> APIDocsAnalysis:
        """Analyze API docs with Claude."""
        if not self.api_key:
            return self._basic_docs_analysis(url, content)

        content_excerpt = content[:10000]

        prompt = f"""Analyze this API documentation for developer experience.

URL: {url}

Content:
{content_excerpt}

Score each factor 0-10:

Respond with JSON:
```json
{{
    "completeness": <0-10>,
    "clarity": <0-10>,
    "examples_quality": <0-10>,
    "quickstart_exists": <0-10>,
    "error_handling_docs": <0-10>,
    "overall_score": <0-10>,
    "strengths": [".."],
    "weaknesses": [".."]
}}
```"""

        try:
            response = self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "temperature": 0.3,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            result = response.json()["content"][0]["text"]

            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return APIDocsAnalysis(
                    url=url,
                    score=data.get("overall_score", 5.0),
                    completeness=data.get("completeness", 5.0),
                    clarity=data.get("clarity", 5.0),
                    examples_quality=data.get("examples_quality", 5.0),
                    quickstart_exists=data.get("quickstart_exists", 5.0),
                    error_handling_docs=data.get("error_handling_docs", 5.0),
                    strengths=data.get("strengths", []),
                    weaknesses=data.get("weaknesses", []),
                )
        except:
            pass

        return self._basic_docs_analysis(url, content)

    def _basic_docs_analysis(self, url: str, content: str) -> APIDocsAnalysis:
        """Basic docs analysis without LLM."""
        score = 5.0
        strengths = []
        weaknesses = []

        content_lower = content.lower()

        if "quickstart" in content_lower or "getting started" in content_lower:
            strengths.append("Has quickstart guide")
            score += 1
        else:
            weaknesses.append("No quickstart guide found")
            score -= 0.5

        if "example" in content_lower or "```" in content:
            strengths.append("Has code examples")
            score += 1
        else:
            weaknesses.append("No code examples found")
            score -= 1

        if "error" in content_lower:
            strengths.append("Documents errors")
            score += 0.5

        return APIDocsAnalysis(
            url=url,
            score=max(0, min(10, score)),
            strengths=strengths,
            weaknesses=weaknesses,
        )

    def _analyze_mcp_with_llm(self, url: str, mcp_def: Dict) -> MCPAnalysis:
        """Analyze MCP definition with Claude."""
        tools = []
        issues = []
        score = 5.0

        # Check if it's a valid MCP definition
        if isinstance(mcp_def, dict):
            if "tools" in mcp_def:
                tools = [t.get("name", "unnamed") for t in mcp_def.get("tools", [])]
                score += 2
            elif "name" in mcp_def:
                tools = [mcp_def.get("name")]
                score += 1

            if "inputSchema" in mcp_def or any("inputSchema" in str(t) for t in mcp_def.get("tools", [])):
                score += 1
            else:
                issues.append("Missing input schema")
                score -= 1

            if "description" in mcp_def or any("description" in str(t) for t in mcp_def.get("tools", [])):
                score += 1
            else:
                issues.append("Missing descriptions")
                score -= 1
        else:
            issues.append("Invalid MCP definition format")
            score = 2.0

        return MCPAnalysis(
            tool_definition_url=url,
            score=max(0, min(10, score)),
            tools_found=tools,
            issues=issues,
        )

    def analyze_all(
        self,
        landing_url: str = None,
        docs_url: str = None,
        mcp_url: str = None,
    ) -> ExecutionQualityScore:
        """Analyze all provided URLs and return combined score."""
        result = ExecutionQualityScore()

        if landing_url:
            result.landing_page = self.analyze_landing_page(landing_url)

        if docs_url:
            result.api_docs = self.analyze_api_docs(docs_url)

        if mcp_url:
            result.mcp = self.analyze_mcp(mcp_url)

        return result
