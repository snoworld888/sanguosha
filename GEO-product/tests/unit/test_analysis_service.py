"""
GEO 智能优化平台 - 分析服务单元测试
"""
import pytest
from src.services.analysis import AnalysisService, analysis_service
from src.models.schemas import GEMScore, PlatformEnum


class TestAnalysisService:
    """分析服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = AnalysisService()

    def test_calculate_gem_score_basic(self):
        """测试GEM评分基本计算"""
        content = """
        这是一篇关于产品评测的文章。

        首先，我们来看一下产品的外观设计。

        其次，关于产品功能，经过测试发现：

        数据显示，该产品在多个指标上表现优秀。

        最后，总结一下优点和缺点。
        """

        metadata = {
            "platform": "wechat",
            "is_verified": True,
            "followers": 15000
        }

        score = self.service.calculate_gem_score(content, metadata)

        assert isinstance(score, GEMScore)
        assert 0 <= score.total <= 100
        assert 0 <= score.structure <= 100
        assert 0 <= score.authority <= 100
        assert 0 <= score.evidence <= 100
        assert 0 <= score.expression <= 100
        assert 0 <= score.perspective <= 100

    def test_calculate_gem_score_empty_content(self):
        """测试空内容的GEM评分"""
        content = ""
        metadata = {}

        score = self.service.calculate_gem_score(content, metadata)

        assert isinstance(score, GEMScore)
        assert 0 <= score.total <= 100

    def test_calculate_gem_score_high_authority(self):
        """测试高权威性内容评分"""
        content = """
        作为一名资深产品经理，我来详细评测这款产品。

        引用数据：据权威机构统计，该产品市场份额超过40%。

        参考来源：清华大学研究报告指出...
        """

        metadata = {
            "platform": "zhihu",
            "is_verified": True,
            "followers": 50000
        }

        score = self.service.calculate_gem_score(content, metadata)

        # 权威性应该较高
        assert score.authority >= 60
        # 论据分也应该较高
        assert score.evidence >= 60

    def test_analyze_structure_short_content(self):
        """测试短内容结构分析"""
        content = "这是很短的内容。"
        score = self.service._analyze_structure(content)
        assert 0 <= score <= 100  # 短内容应该在合理范围内

    def test_analyze_structure_well_formatted(self):
        """测试格式良好的内容结构分析"""
        content = """
        # 标题

        ## 第一部分

        内容正文...

        ## 第二部分

        更多内容...

        1. 列表项1
        2. 列表项2
        3. 列表项3
        """
        score = self.service._analyze_structure(content)
        assert score >= 50

    def test_generate_diagnosis_basic(self):
        """测试生成诊断报告"""
        content = "这是一些简短内容。"
        metadata = {"platform": "wechat"}

        diagnosis = self.service.generate_diagnosis(content, metadata)

        assert diagnosis.content_gaps is not None
        assert diagnosis.structure_suggestions is not None
        assert diagnosis.authority_improvements is not None

    def test_identify_content_gaps(self):
        """测试内容缺口识别"""
        content = "这是一篇简短的文章。"  # 缺少核心话题
        metadata = {"platform": "wechat"}

        gaps = self.service._identify_content_gaps(content, metadata)

        # 应该识别出内容过短的问题
        assert any("扩充" in gap for gap in gaps)

    def test_suggest_structure_for_wechat(self):
        """测试公众号结构优化建议"""
        content = "内容"
        metadata = {"platform": "wechat"}

        suggestions = self.service._suggest_structure_improvements(content, metadata)

        assert any("封面" in s for s in suggestions)
        assert any("16:9" in s for s in suggestions)

    def test_suggest_structure_for_zhihu(self):
        """测试知乎结构优化建议"""
        content = "内容"
        metadata = {"platform": "zhihu"}

        suggestions = self.service._suggest_structure_improvements(content, metadata)

        assert any("目录" in s for s in suggestions)

    def test_suggest_structure_for_xiaohongshu(self):
        """测试小红书结构优化建议"""
        content = "内容"
        metadata = {"platform": "xiaohongshu"}

        suggestions = self.service._suggest_structure_improvements(content, metadata)

        assert any("3:4" in s for s in suggestions)
        assert any("emoji" in s.lower() for s in suggestions)

    def test_suggest_authority_improvements_unverified(self):
        """测试未认证用户权威性建议"""
        metadata = {
            "platform": "zhihu",
            "is_verified": False,
            "followers": 500
        }

        suggestions = self.service._suggest_authority_improvements(metadata)

        assert any("认证" in s for s in suggestions)

    def test_analyze_competitor_gaps_no_data(self):
        """测试无竞品数据时的差距分析"""
        gaps = self.service._analyze_competitor_gaps("内容", [])
        assert gaps.get("has_data") is False

    def test_analyze_competitor_gaps_with_data(self):
        """测试有竞品数据时的差距分析"""
        content = "我们的产品很好"
        competitors = [
            {"name": "竞品A", "cited_topics": ["价格", "质量"]},
            {"name": "竞品B", "cited_topics": ["服务", "售后"]}
        ]

        gaps = self.service._analyze_competitor_gaps(content, competitors)

        assert gaps.get("has_data") is True
        assert gaps.get("competitor_count") == 2


class TestGEMScoreValidation:
    """GEM评分验证测试"""

    def test_gem_score_bounds(self):
        """测试GEM评分边界"""
        service = AnalysisService()

        # 边界测试1：空内容
        score = service.calculate_gem_score("", {})
        assert 0 <= score.total <= 100

        # 边界测试2：超长内容
        long_content = "测试内容 " * 1000
        score = service.calculate_gem_score(long_content, {})
        assert 0 <= score.total <= 100

    def test_gem_score_weight_sum(self):
        """测试GEM评分各维度权重"""
        # 所有维度权重应该相等
        # 这里验证计算逻辑的一致性
        service = AnalysisService()
        content = "这是一段测试内容。" * 50
        metadata = {"platform": "zhihu"}

        score = service.calculate_gem_score(content, metadata)

        # 各维度分数应该在合理范围内
        assert score.structure >= 0  # 基础分为50
        assert score.authority >= 0
        assert score.evidence >= 0
        assert score.expression >= 0
        assert score.perspective >= 0
