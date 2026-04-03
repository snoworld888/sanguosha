"""
GEO 智能优化平台 - 智能分析服务
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models.schemas import (
    GEMScore,
    DiagnosisReport,
    ContentSource,
    CitationRecord
)


class AnalysisService:
    """分析服务"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)

    def calculate_gem_score(self, content: str, metadata: Dict[str, Any]) -> GEMScore:
        """
        计算GEM评分 (GEO Effectiveness Metric)

        基于SHEEP框架:
        - S: Structure (内容结构)
        - H: Authority (权威性)
        - E: Evidence (论据充分性)
        - E: Expression (表达清晰度)
        - P: Perspective (观点独特性)
        """
        # 内容结构分析
        structure_score = self._analyze_structure(content)

        # 权威性分析
        authority_score = self._analyze_authority(metadata)

        # 论据充分性分析
        evidence_score = self._analyze_evidence(content)

        # 表达清晰度分析
        expression_score = self._analyze_expression(content)

        # 观点独特性分析
        perspective_score = self._analyze_perspective(content, metadata)

        # 计算总分
        total_score = (
            structure_score * 0.20 +
            authority_score * 0.20 +
            evidence_score * 0.20 +
            expression_score * 0.20 +
            perspective_score * 0.20
        )

        return GEMScore(
            total=round(total_score, 2),
            structure=round(structure_score, 2),
            authority=round(authority_score, 2),
            evidence=round(evidence_score, 2),
            expression=round(expression_score, 2),
            perspective=round(perspective_score, 2)
        )

    def _analyze_structure(self, content: str) -> float:
        """分析内容结构"""
        score = 50.0  # 基础分

        # 检查标题
        if content and len(content) > 100:
            score += 10

        # 检查段落数量
        paragraphs = content.split("\n\n")
        if 3 <= len(paragraphs) <= 10:
            score += 15
        elif len(paragraphs) > 10:
            score += 10

        # 检查列表和编号
        if any(marker in content for marker in ["1.", "2.", "•", "-", "第一", "第二"]):
            score += 15

        # 检查关键词密度
        word_count = len(content)
        if 500 <= word_count <= 3000:
            score += 10

        return min(score, 100)

    def _analyze_authority(self, metadata: Dict[str, Any]) -> float:
        """分析权威性"""
        score = 50.0  # 基础分

        # 作者认证
        if metadata.get("is_verified"):
            score += 20

        # 粉丝数量
        followers = metadata.get("followers", 0)
        if followers > 10000:
            score += 15
        elif followers > 1000:
            score += 10

        # 平台类型
        platform = metadata.get("platform", "")
        authoritative_platforms = ["zhihu", "wechat", "bilibili"]
        if platform in authoritative_platforms:
            score += 15

        return min(score, 100)

    def _analyze_evidence(self, content: str) -> float:
        """分析论据充分性"""
        score = 50.0  # 基础分

        # 数据引用
        data_indicators = ["数据显示", "研究表明", "根据", "统计", "%", "数据"]
        data_count = sum(1 for indicator in data_indicators if indicator in content)
        score += min(data_count * 5, 20)

        # 引用标记
        quote_indicators = ['"', '"', '"', '"', "引用", "来源"]
        quote_count = sum(1 for indicator in quote_indicators if indicator in content)
        score += min(quote_count * 3, 15)

        # 外部链接
        if "http" in content:
            score += 10

        return min(score, 100)

    def _analyze_expression(self, content: str) -> float:
        """分析表达清晰度"""
        score = 50.0  # 基础分

        # 句子平均长度
        sentences = content.replace("!", ".").replace("?", ".").split(".")
        avg_sentence_len = sum(len(s.strip()) for s in sentences) / max(len(sentences), 1)

        if 10 <= avg_sentence_len <= 25:
            score += 20
        elif avg_sentence_len < 10:
            score += 10

        # 冗余度
        unique_ratio = len(set(content)) / max(len(content), 1)
        if unique_ratio > 0.6:
            score += 15

        # 可读性
        readable_indicators = ["首先", "其次", "最后", "因此", "然而", "但是", "所以"]
        if any(indicator in content for indicator in readable_indicators):
            score += 15

        return min(score, 100)

    def _analyze_perspective(self, content: str, metadata: Dict[str, Any]) -> float:
        """分析观点独特性"""
        score = 50.0  # 基础分

        # 独特观点标记
        unique_indicators = ["我认为", "我觉得", "个人观点", "独特见解", "创新"]
        if any(indicator in content for indicator in unique_indicators):
            score += 20

        # 原创性（与通用内容的差异度）
        generic_content = "这是一个好的产品，我们推荐使用它"
        try:
            vectors = self.vectorizer.fit_transform([content, generic_content])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            # 相似度越低，独特性越高
            score += (1 - similarity) * 20
        except:
            pass

        return min(score, 100)

    def generate_diagnosis(
        self,
        content: str,
        metadata: Dict[str, Any],
        competitors: List[Dict[str, Any]] = None
    ) -> DiagnosisReport:
        """生成优化诊断报告"""
        gem_score = self.calculate_gem_score(content, metadata)

        # 内容缺口分析
        content_gaps = self._identify_content_gaps(content, metadata)

        # 结构优化建议
        structure_suggestions = self._suggest_structure_improvements(content, metadata)

        # 权威性提升建议
        authority_improvements = self._suggest_authority_improvements(metadata)

        # 竞品差距分析
        competitor_gaps = self._analyze_competitor_gaps(content, competitors or [])

        return DiagnosisReport(
            content_gaps=content_gaps,
            structure_suggestions=structure_suggestions,
            authority_improvements=authority_improvements,
            competitor_gaps=competitor_gaps
        )

    def _identify_content_gaps(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """识别内容缺口"""
        gaps = []

        # 检查核心问题覆盖
        essential_topics = ["价格", "效果", "使用方法", "优缺点", "对比"]
        for topic in essential_topics:
            if topic not in content:
                gaps.append(f"建议添加关于'{topic}'的内容")

        # 检查字数
        if len(content) < 500:
            gaps.append("内容偏短，建议扩充至1000字以上以提高AI引用概率")

        # 检查多媒体
        if metadata.get("has_images") is False:
            gaps.append("建议添加图片/图表以提高内容丰富度")

        return gaps

    def _suggest_structure_improvements(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """建议结构优化"""
        suggestions = []
        platform = metadata.get("platform", "")

        if platform == "wechat":
            suggestions.append("建议使用16:9封面图片")
            suggestions.append("摘要控制在50-100字")
            if not content.startswith("#"):
                suggestions.append("建议在开头添加清晰的标题标签")
        elif platform == "zhihu":
            suggestions.append("建议添加目录结构")
            suggestions.append("开头应包含 TL;DR 要点总结")
        elif platform == "xiaohongshu":
            suggestions.append("建议使用3:4封面比例")
            suggestions.append("添加更多emoji增加视觉吸引力")
            suggestions.append("标签数量建议控制在5-10个")
        elif platform == "douyin":
            suggestions.append("视频前3秒需要有强钩子")
            suggestions.append("建议添加字幕")
            suggestions.append("控制视频长度在30-60秒")

        return suggestions

    def _suggest_authority_improvements(self, metadata: Dict[str, Any]) -> List[str]:
        """建议权威性提升"""
        suggestions = []

        platform = metadata.get("platform", "")

        if platform == "zhihu" and not metadata.get("is_verified"):
            suggestions.append("建议申请知乎专业认证")
        elif platform == "douyin" and not metadata.get("is_blue_v"):
            suggestions.append("建议申请抖音蓝V认证")

        if metadata.get("followers", 0) < 1000:
            suggestions.append("建议积累更多粉丝以提高权威性")

        suggestions.append("建议在内容中添加专家背书或合作信息")

        return suggestions

    def _analyze_competitor_gaps(self, content: str, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析竞品差距"""
        if not competitors:
            return {"has_data": False}

        # 计算与竞品的内容重叠度
        content_words = set(content)

        gap_analysis = {
            "has_data": True,
            "competitor_count": len(competitors),
            "your_advantages": [],
            "competitor_strengths": [],
            "improvement_suggestions": []
        }

        # 简化实现，实际需要更复杂的NLP分析
        for comp in competitors[:3]:
            comp_name = comp.get("name", "未知竞品")
            gap_analysis["competitor_strengths"].append({
                "name": comp_name,
                "cited_topics": comp.get("cited_topics", [])
            })

        return gap_analysis

    def analyze_citation_trends(
        self,
        citations: List[CitationRecord],
        date_range: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """分析引用趋势"""
        if not citations:
            return {"has_data": False, "trend": "no_data"}

        # 按时间统计
        daily_counts = {}
        for citation in citations:
            date = citation.citation_time.strftime("%Y-%m-%d")
            daily_counts[date] = daily_counts.get(date, 0) + 1

        # 计算趋势
        dates = sorted(daily_counts.keys())
        if len(dates) < 2:
            trend = "insufficient_data"

        counts = [daily_counts[d] for d in dates]
        recent_avg = sum(counts[-7:]) / min(len(counts), 7)
        older_avg = sum(counts[:-7]) / max(len(counts) - 7, 1)

        if recent_avg > older_avg * 1.2:
            trend = "increasing"
        elif recent_avg < older_avg * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "has_data": True,
            "trend": trend,
            "total_citations": len(citations),
            "daily_average": round(sum(counts) / len(counts), 2),
            "peak_date": max(daily_counts, key=daily_counts.get),
            "daily_counts": daily_counts,
            "by_platform": self._count_by_platform(citations),
            "by_keyword": self._count_by_keyword(citations)
        }

    def _count_by_platform(self, citations: List[CitationRecord]) -> Dict[str, int]:
        """按平台统计"""
        counts = {}
        for c in citations:
            platform = c.ai_platform
            counts[platform] = counts.get(platform, 0) + 1
        return counts

    def _count_by_keyword(self, citations: List[CitationRecord]) -> Dict[str, int]:
        """按关键词统计"""
        counts = {}
        for c in citations:
            keyword = c.brand_keyword
            counts[keyword] = counts.get(keyword, 0) + 1
        return counts


# 服务单例
analysis_service = AnalysisService()
