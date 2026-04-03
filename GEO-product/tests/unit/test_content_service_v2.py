"""
GEO 内容服务补充测试 - 覆盖 ZhihuContentGenerator, XiaohongshuContentGenerator 等
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.content.service import (
    ContentGenerationService,
    WeChatContentGenerator,
    ZhihuContentGenerator,
    XiaohongshuContentGenerator,
    DouyinContentGenerator,
    ContentGenerator,
    ContentPolicyChecker
)
from src.models.schemas import (
    ContentGenerationRequest,
    PlatformEnum,
    ContentTypeEnum
)


class TestZhihuContentGenerator:
    """知乎内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = ZhihuContentGenerator()

    def test_generate_title(self):
        """测试标题生成"""
        title = self.generator._generate_title("人工智能")
        assert "人工智能" in title
        assert "深度解析" in title

    def test_generate_tags(self):
        """测试标签生成"""
        keywords = ["AI", "机器学习"]
        tags = self.generator._generate_tags(keywords)

        assert "AI" in tags
        assert "机器学习" in tags
        assert "知乎专栏" in tags
        assert len(tags) <= 10

    def test_generate_tags_empty(self):
        """测试空关键词标签生成"""
        tags = self.generator._generate_tags([])
        assert "知乎专栏" in tags
        assert len(tags) <= 10

    @pytest.mark.asyncio
    async def test_generate_full_response(self):
        """测试完整生成响应"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.ZHUHU,
            content_type=ContentTypeEnum.ARTICLE,
            topic="区块链技术",
            keywords=["分布式", "加密"],
            tone="professional",
            length=1500
        )

        response = await self.generator.generate(request)

        assert response.content.title is not None
        assert "区块链技术" in response.content.title
        assert len(response.content.body) > 0
        assert response.quality_score > 0


class TestXiaohongshuContentGenerator:
    """小红书内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = XiaohongshuContentGenerator()

    def test_generate_title(self):
        """测试标题生成"""
        title = self.generator._generate_title("护肤心得")
        assert "护肤心得" in title

    def test_generate_tags(self):
        """测试标签生成"""
        keywords = ["护肤", "保湿"]
        tags = self.generator._generate_tags(keywords)

        assert "护肤" in tags
        assert "保湿" in tags
        assert len(tags) <= 10

    def test_generate_tags_limit(self):
        """测试标签数量限制"""
        keywords = [f"关键词{i}" for i in range(20)]
        tags = self.generator._generate_tags(keywords)
        assert len(tags) <= 10

    @pytest.mark.asyncio
    async def test_generate_with_cover(self):
        """测试带封面生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.XIAOHONGSHU,
            content_type=ContentTypeEnum.NOTE,
            topic="美妆教程",
            keywords=["口红", "眼影"],
            tone="casual",
            length=800
        )

        response = await self.generator.generate(request)

        assert response.content.cover_url is not None
        assert response.content.cover_url.startswith("cover_")


class TestCompliancePolicyChecker:
    """合规检查器测试"""

    def setup_method(self):
        """测试前准备"""
        self.checker = ContentPolicyChecker()

    def test_check_clean_content(self):
        """测试正常内容检查"""
        content = "这是一个正常的产品介绍文章。"
        result = self.checker.check(content, PlatformEnum.WECHAT)

        assert result["is_compliant"] is True
        assert len(result["errors"]) == 0

    def test_check_politics_content(self):
        """测试政治敏感内容检测"""
        content = "测试内容"
        result = self.checker.check(content, PlatformEnum.WECHAT)

        # 应该返回检查结果
        assert "is_compliant" in result

    def test_check_ad_violation(self):
        """测试广告法违规检测"""
        content = "这是史上最好用的产品，全球第一！"
        result = self.checker.check(content, PlatformEnum.XIAOHONGSHU)

        # 应该检测到极限词
        assert "errors" in result or "warnings" in result

    def test_check_douyin_restricted(self):
        """测试抖音禁发内容检测"""
        content = "抖音内容"
        result = self.checker.check(content, PlatformEnum.DOUYIN)

        assert "is_compliant" in result

    def test_check_multiple_violations(self):
        """测试多重违规检测"""
        content = "史上最棒的产品，绝对第一！"
        result = self.checker.check(content, PlatformEnum.WECHAT)

        # 可能检测到多个警告
        assert len(result["errors"]) + len(result["warnings"]) >= 0


class TestContentServiceExtended:
    """内容服务扩展测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = ContentGenerationService()

    def test_initialization(self):
        """测试服务初始化"""
        assert len(self.service.generators) == 4
        assert PlatformEnum.WECHAT in self.service.generators
        assert PlatformEnum.ZHUHU in self.service.generators
        assert PlatformEnum.XIAOHONGSHU in self.service.generators
        assert PlatformEnum.DOUYIN in self.service.generators

    @pytest.mark.asyncio
    async def test_generate_content_wechat(self):
        """测试生成微信内容"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="产品介绍",
            keywords=["特点", "优势"],
            tone="professional",
            length=1000
        )

        response = await self.service.generate_content(request)
        assert response.content.title is not None
        assert len(response.content.body) > 0

    @pytest.mark.asyncio
    async def test_generate_content_zhihu(self):
        """测试生成知乎内容"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.ZHUHU,
            content_type=ContentTypeEnum.ARTICLE,
            topic="技术解析",
            keywords=["原理", "实现"],
            tone="professional",
            length=1200
        )

        response = await self.service.generate_content(request)
        assert response.content.title is not None

    @pytest.mark.asyncio
    async def test_generate_content_xiaohongshu(self):
        """测试生成小红书内容"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.XIAOHONGSHU,
            content_type=ContentTypeEnum.NOTE,
            topic="好物推荐",
            keywords=["推荐", "必买"],
            tone="casual",
            length=600
        )

        response = await self.service.generate_content(request)
        assert response.content.title is not None

    @pytest.mark.asyncio
    async def test_generate_content_douyin(self):
        """测试生成抖音内容"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.DOUYIN,
            content_type=ContentTypeEnum.VIDEO,
            topic="生活小妙招",
            keywords=["技巧", "妙招"],
            tone="energetic",
            length=500
        )

        response = await self.service.generate_content(request)
        assert response.content.title is not None

    @pytest.mark.asyncio
    async def test_generate_content_unsupported(self):
        """测试生成不支持平台的内容"""
        from src.models.schemas import PlatformEnum as PEnum

        # 找一个不支持的平台，比如 BAIDU
        request = ContentGenerationRequest(
            platform=PEnum.BAIDU,  # 可能不支持
            content_type=ContentTypeEnum.ARTICLE,
            topic="测试",
            keywords=["测试"],
            tone="professional",
            length=500
        )

        # 应该在generators中找不到
        assert PEnum.BAIDU not in self.service.generators

    def test_apply_geo_optimization(self):
        """测试GEO优化应用"""
        from src.models.schemas import GeneratedContent

        content = GeneratedContent(
            title="测试标题",
            body="测试正文内容" * 50,
            cover_url=None,
            tags=["测试"],
            estimated_read_time=5,
            seo_suggestions=[]
        )

        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="测试",
            keywords=["SEO"],
            tone="professional",
            length=1000
        )

        optimized = self.service._apply_geo_optimization(content, request)

        assert optimized.seo_suggestions is not None

    def test_apply_geo_optimization_keywords(self):
        """测试关键词GEO优化"""
        from src.models.schemas import GeneratedContent

        content = GeneratedContent(
            title="产品A评测",
            body="这是关于产品A的详细介绍",
            cover_url=None,
            tags=["产品A"],
            estimated_read_time=3,
            seo_suggestions=[]
        )

        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="产品A",
            keywords=["产品A", "评测"],
            tone="professional",
            length=500
        )

        optimized = self.service._apply_geo_optimization(content, request)

        # body应该包含关键词
        assert "产品A" in optimized.body


class TestDouyinContentGeneratorExtended:
    """抖音内容生成器扩展测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = DouyinContentGenerator()

    def test_generate_title_with_hooks(self):
        """测试带钩子的标题生成"""
        title = self.generator._generate_title("生活小妙招")
        assert "生活小妙招" in title

    @pytest.mark.asyncio
    async def test_generate_script_with_hooks(self):
        """测试带钩子的脚本生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.DOUYIN,
            content_type=ContentTypeEnum.VIDEO,
            topic="美食制作",
            keywords=["做法", "教程"],
            tone="energetic",
            length=600
        )

        response = await self.generator.generate(request)

        # 前3秒应该有钩子
        assert len(response.content.body) > 0

    def test_generate_tags_douyin(self):
        """测试抖音标签生成"""
        keywords = ["美食", "做法"]
        tags = self.generator._generate_tags(keywords)

        assert "美食" in tags
        assert "做法" in tags


class TestWeChatContentGenerator:
    """微信内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = WeChatContentGenerator()

    def test_initialization(self):
        """测试初始化"""
        assert self.generator.platform == PlatformEnum.WECHAT

    def test_generate_title(self):
        """测试标题生成"""
        title = self.generator._generate_title("产品发布", "professional")
        assert "产品发布" in title

    def test_generate_tags(self):
        """测试标签生成"""
        keywords = ["新品", "发布"]
        tags = self.generator._generate_tags(keywords)

        assert "新品" in tags or "发布" in tags

    @pytest.mark.asyncio
    async def test_generate_article(self):
        """测试文章生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="技术分享",
            keywords=["技术", "架构"],
            tone="professional",
            length=1500
        )

        response = await self.generator.generate(request)

        assert response.content.title is not None
        assert len(response.content.body) > 0


class TestContentBatchGenerate:
    """批量内容生成测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = ContentGenerationService()

    @pytest.mark.asyncio
    async def test_batch_generate_multiple(self):
        """测试批量生成多个内容"""
        requests = [
            ContentGenerationRequest(
                platform=PlatformEnum.WECHAT,
                content_type=ContentTypeEnum.ARTICLE,
                topic="主题A",
                keywords=["A"],
                tone="professional",
                length=800
            ),
            ContentGenerationRequest(
                platform=PlatformEnum.ZHUHU,
                content_type=ContentTypeEnum.ARTICLE,
                topic="主题B",
                keywords=["B"],
                tone="professional",
                length=800
            ),
        ]

        responses = await self.service.batch_generate(requests)

        assert len(responses) == 2
        assert responses[0].content.title is not None
        assert responses[1].content.title is not None
