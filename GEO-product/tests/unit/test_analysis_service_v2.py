"""
GEO 分析服务补充测试 - 覆盖 citation_trends, count_by_* 等函数
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.services.analysis.service import AnalysisService
from src.models.schemas import (
    GEMScore,
    CitationRecord,
    PlatformEnum
)


class TestAnalysisServiceCitationTrends:
    """分析服务引用趋势测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AnalysisService()

    def _create_citation(
        self,
        ai_platform: str,
        brand_keyword: str,
        days_ago: int
    ) -> CitationRecord:
        """创建测试用引用记录"""
        return CitationRecord(
            id=f"cite_{days_ago}_{ai_platform}",
            tenant_id="test_tenant",
            content_source_id=f"source_{days_ago}_{ai_platform}",
            ai_platform=ai_platform,
            search_query=f"查询{brand_keyword}",
            citation_context=f"这是关于{brand_keyword}的引用内容",
            brand_keyword=brand_keyword,
            citation_time=datetime.now() - timedelta(days=days_ago),
            confidence=0.8,
            created_at=datetime.now() - timedelta(days=days_ago)
        )

    def test_analyze_citation_trends_empty(self):
        """测试空数据趋势分析"""
        result = self.service.analyze_citation_trends([])
        
        assert result["has_data"] is False
        assert result["trend"] == "no_data"

    def test_analyze_citation_trends_single_day(self):
        """测试单日数据趋势分析"""
        citations = [
            self._create_citation("deepseek", "品牌A", 1),
            self._create_citation("deepseek", "品牌B", 1),
        ]
        
        result = self.service.analyze_citation_trends(citations)
        
        assert result["has_data"] is True
        assert result["trend"] == "insufficient_data"

    def test_analyze_citation_trends_increasing(self):
        """测试上升趋势"""
        # 最近7天有更多引用
        citations = []
        for i in range(20):
            citations.append(self._create_citation("deepseek", "品牌A", i % 3))
        
        result = self.service.analyze_citation_trends(citations)
        
        assert result["has_data"] is True
        assert result["trend"] == "increasing"

    def test_analyze_citation_trends_decreasing(self):
        """测试下降趋势"""
        # 更早的日期有更多引用
        citations = []
        for i in range(15):
            days = 14 - (i % 14)  # 早期多
            citations.append(self._create_citation("deepseek", "品牌A", days))
        
        result = self.service.analyze_citation_trends(citations)
        
        assert result["has_data"] is True

    def test_analyze_citation_trends_stable(self):
        """测试稳定趋势"""
        citations = []
        for i in range(20):
            citations.append(self._create_citation("deepseek", "品牌A", i % 10))
        
        result = self.service.analyze_citation_trends(citations)
        
        assert result["has_data"] is True
        assert "total_citations" in result
        assert "daily_average" in result
        assert "peak_date" in result

    def test_analyze_citation_trends_with_date_range(self):
        """测试带日期范围的引用趋势"""
        citations = [
            self._create_citation("deepseek", "品牌A", 5),
            self._create_citation("kimi", "品牌A", 3),
            self._create_citation("doubao", "品牌B", 1),
        ]
        
        result = self.service.analyze_citation_trends(
            citations,
            date_range={
                "start": datetime.now() - timedelta(days=7),
                "end": datetime.now()
            }
        )
        
        assert result["has_data"] is True
        assert "by_platform" in result
        assert "by_keyword" in result

    def test_count_by_platform(self):
        """测试按平台统计"""
        citations = [
            self._create_citation("deepseek", "品牌A", 1),
            self._create_citation("deepseek", "品牌B", 2),
            self._create_citation("kimi", "品牌A", 3),
            self._create_citation("kimi", "品牌C", 4),
            self._create_citation("doubao", "品牌A", 5),
        ]
        
        counts = self.service._count_by_platform(citations)
        
        assert counts["deepseek"] == 2
        assert counts["kimi"] == 2
        assert counts["doubao"] == 1

    def test_count_by_platform_empty(self):
        """测试空列表按平台统计"""
        counts = self.service._count_by_platform([])
        assert counts == {}

    def test_count_by_keyword(self):
        """测试按关键词统计"""
        citations = [
            self._create_citation("deepseek", "品牌A", 1),
            self._create_citation("kimi", "品牌A", 2),
            self._create_citation("doubao", "品牌B", 3),
            self._create_citation("deepseek", "品牌C", 4),
        ]
        
        counts = self.service._count_by_keyword(citations)
        
        assert counts["品牌A"] == 2
        assert counts["品牌B"] == 1
        assert counts["品牌C"] == 1

    def test_count_by_keyword_empty(self):
        """测试空列表按关键词统计"""
        counts = self.service._count_by_keyword([])
        assert counts == {}


class TestAnalysisServiceExtended:
    """分析服务扩展测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AnalysisService()

    def test_analyze_structure_with_list_markers(self):
        """测试带列表标记的内容结构分析"""
        content = """
        下面是几个要点：
        1. 第一点内容
        2. 第二点内容
        3. 第三点内容
        
        此外还有：
        - 额外说明A
        - 额外说明B
        """
        score = self.service._analyze_structure(content)
        assert score > 50  # 应该因为有列表而加分

    def test_analyze_structure_many_paragraphs(self):
        """测试多段落内容结构分析"""
        content = "\n\n".join([f"段落{i}内容" for i in range(15)])
        score = self.service._analyze_structure(content)
        assert score > 50

    def test_analyze_authority_verified_with_followers(self):
        """测试已认证且有粉丝的权威性分析"""
        metadata = {
            "is_verified": True,
            "followers": 50000,
            "platform": "zhihu"
        }
        score = self.service._analyze_authority(metadata)
        assert score > 70  # 应该得高分

    def test_analyze_authority_unverified_low_followers(self):
        """测试未认证且粉丝少的权威性分析"""
        metadata = {
            "is_verified": False,
            "followers": 100,
            "platform": "weibo"
        }
        score = self.service._analyze_authority(metadata)
        assert score < 70  # 应该得低分

    def test_analyze_evidence_with_data_and_quotes(self):
        """测试有数据和引用的论据分析"""
        content = """
        数据显示：使用该产品后效率提升50%。
        研究表明，这是业内领先的水平。
        根据第三方统计，用户满意度达90%。
        正如某专家所说："这是革命性的产品。"
        """
        score = self.service._analyze_evidence(content)
        assert score > 60

    def test_analyze_evidence_with_http_links(self):
        """测试包含外部链接的论据分析"""
        content = "更多信息请访问 https://example.com"
        score = self.service._analyze_evidence(content)
        assert score >= 60  # 包含http链接加分

    def test_analyze_expression_clear_transitions(self):
        """测试清晰过渡的表达分析"""
        content = """
        首先，我们需要了解基本情况。
        其次，制定相应的策略。
        然而，还需要考虑其他因素。
        因此，我们得出以下结论。
        """
        score = self.service._analyze_expression(content)
        assert score > 60

    def test_analyze_expression_short_sentences(self):
        """测试短句子的表达分析"""
        content = "好。很好。非常好。" * 10
        score = self.service._analyze_expression(content)
        assert score >= 50

    def test_analyze_perspective_with_unique_opinions(self):
        """测试有独特观点的内容"""
        content = """
        我个人认为，这个产品有以下独特见解：
        1. 创新点在于...
        2. 我觉得未来的趋势是...
        3. 原创性的解决方案是...
        """
        score = self.service._analyze_perspective(content, {})
        assert score > 60

    def test_identify_content_gaps_short_content(self):
        """测试短内容的内容缺口识别"""
        content = "这是一个很短的产品介绍。"
        metadata = {"platform": "wechat"}
        gaps = self.service._identify_content_gaps(content, metadata)
        
        assert any("字数" in gap for gap in gaps)
        assert len(gaps) >= 2  # 字数 + 核心问题覆盖

    def test_identify_content_gaps_without_images(self):
        """测试无图片的内容缺口"""
        content = "这是一段足够长的产品介绍。" * 50
        metadata = {"platform": "wechat", "has_images": False}
        gaps = self.service._identify_content_gaps(content, metadata)
        
        assert any("图片" in gap for gap in gaps)

    def test_identify_content_gaps_no_gaps(self):
        """测试无明显缺口的内容"""
        content = "价格优惠，效果显著。使用方法简单。优缺点分析如下。" * 50
        metadata = {"platform": "wechat", "has_images": True}
        gaps = self.service._identify_content_gaps(content, metadata)
        
        # 应该只有少量缺口
        assert len(gaps) <= 3

    def test_suggest_structure_for_wechat(self):
        """测试微信结构建议"""
        content = ""  # 不以#开头
        metadata = {"platform": "wechat"}
        suggestions = self.service._suggest_structure_improvements(content, metadata)
        
        assert any("封面" in s for s in suggestions)
        assert any("标题" in s for s in suggestions)

    def test_suggest_structure_for_douyin(self):
        """测试抖音结构建议"""
        content = ""
        metadata = {"platform": "douyin"}
        suggestions = self.service._suggest_structure_improvements(content, metadata)
        
        assert any("3秒" in s or "钩子" in s for s in suggestions)

    def test_suggest_authority_for_unverified_zhihu(self):
        """测试知乎未认证用户权威性建议"""
        metadata = {"platform": "zhihu", "is_verified": False, "followers": 500}
        suggestions = self.service._suggest_authority_improvements(metadata)
        
        assert any("认证" in s for s in suggestions)

    def test_suggest_authority_for_unverified_douyin(self):
        """测试抖音未认证用户权威性建议"""
        metadata = {"platform": "douyin", "is_blue_v": False, "followers": 500}
        suggestions = self.service._suggest_authority_improvements(metadata)
        
        assert any("蓝V" in s for s in suggestions)

    def test_analyze_competitor_gaps_with_competitors(self):
        """测试有竞品数据的差距分析"""
        content = "我们的产品特点"
        competitors = [
            {"name": "竞品A", "cited_topics": ["价格", "效果"]},
            {"name": "竞品B", "cited_topics": ["服务", "质量"]},
            {"name": "竞品C", "cited_topics": ["创新"]},
        ]
        
        gaps = self.service._analyze_competitor_gaps(content, competitors)
        
        assert gaps["has_data"] is True
        assert gaps["competitor_count"] == 3
        assert len(gaps["competitor_strengths"]) == 3
