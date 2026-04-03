"""
GEO 智能优化平台 - 内容生成服务单元测试
"""
import pytest
from src.services.content import (
    ContentGenerationService,
    ContentPolicyChecker,
    WeChatContentGenerator,
    XiaohongshuContentGenerator,
    DouyinContentGenerator
)
from src.models.schemas import (
    PlatformEnum,
    ContentTypeEnum,
    ContentGenerationRequest
)


class TestContentPolicyChecker:
    """内容合规审核测试"""

    def setup_method(self):
        """测试前准备"""
        self.checker = ContentPolicyChecker()

    def test_check_clean_content(self):
        """测试正常内容"""
        content = "这是一篇正常的产品评测文章，介绍了产品的优点和缺点。"
        result = self.checker.check(content)

        assert result["passed"] is True
        assert len(result["errors"]) == 0

    def test_check_content_with_sensitive_words(self):
        """测试包含敏感词的内容"""
        content = "这篇文章包含一些暴力和色情内容。"
        result = self.checker.check(content)

        assert result["passed"] is False
        assert len(result["errors"]) > 0

    def test_check_content_with_extreme_words(self):
        """测试包含极限词的内容"""
        content = "这是最好的产品，第一名，顶级推荐！"
        result = self.checker.check(content)

        assert result["passed"] is True  # 极限词只警告，不报错
        assert len(result["warnings"]) > 0

    def test_check_douyin_banned_content(self):
        """测试抖音禁发内容检测"""
        content = "这里有枪支和管制刀具的信息"
        result = self.checker.check(content, PlatformEnum.DOUYIN)

        assert any("抖音" in w for w in result["warnings"])


class TestWeChatContentGenerator:
    """微信公众号内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = WeChatContentGenerator()

    @pytest.mark.asyncio
    async def test_generate_basic_content(self):
        """测试基本内容生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="人工智能发展趋势",
            keywords=["AI", "机器学习", "深度学习"],
            tone="professional",
            length=1000
        )

        response = await self.generator.generate(request)

        assert response.content.title is not None
        assert len(response.content.body) > 0
        assert "AI" in response.content.title or "人工智能" in response.content.title

    @pytest.mark.asyncio
    async def test_generate_with_topic_in_title(self):
        """测试生成内容标题包含主题"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.WECHAT,
            content_type=ContentTypeEnum.ARTICLE,
            topic="新能源汽车评测",
            keywords=["电动车", "续航"],
            tone="professional",
            length=1000
        )

        response = await self.generator.generate(request)

        assert "新能源" in response.content.title or "电动车" in response.content.title

    def test_generate_tags(self):
        """测试标签生成"""
        keywords = ["AI", "机器学习"]
        tags = self.generator._generate_tags(keywords)

        assert "AI" in tags
        assert "GEO优化" in tags
        assert len(tags) <= 10


class TestXiaohongshuContentGenerator:
    """小红书内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = XiaohongshuContentGenerator()

    @pytest.mark.asyncio
    async def test_generate_xiaohongshu_content(self):
        """测试小红书内容生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.XIAOHONGSHU,
            content_type=ContentTypeEnum.NOTE,
            topic="GEO优化技巧分享",
            keywords=["GEO", "AI搜索", "小红书运营"],
            tone="friendly",
            length=500
        )

        response = await self.generator.generate(request)

        assert response.content.title is not None
        assert "📚" in response.content.title or "#" in response.content.body
        assert len(response.content.tags) > 0

    @pytest.mark.asyncio
    async def test_xiaohongshu_emoji_usage(self):
        """测试小红书emoji使用"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.XIAOHONGSHU,
            content_type=ContentTypeEnum.NOTE,
            topic="测试话题",
            keywords=["测试"],
            tone="friendly",
            length=500
        )

        response = await self.generator.generate(request)

        # 小红书内容应该使用emoji
        assert "👋" in response.content.body or "#" in response.content.body


class TestDouyinContentGenerator:
    """抖音内容生成器测试"""

    def setup_method(self):
        """测试前准备"""
        self.generator = DouyinContentGenerator()

    @pytest.mark.asyncio
    async def test_generate_douyin_script(self):
        """测试抖音脚本生成"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.DOUYIN,
            content_type=ContentTypeEnum.VIDEO,
            topic="产品使用教程",
            keywords=["教程", "使用技巧"],
            tone="energetic",
            length=500
        )

        response = await self.generator.generate(request)

        assert "【开场钩子" in response.content.body
        assert "【结尾引导" in response.content.body
        assert "字幕" in response.content.body

    @pytest.mark.asyncio
    async def test_douyin_golden_3_seconds(self):
        """测试抖音黄金3秒"""
        request = ContentGenerationRequest(
            platform=PlatformEnum.DOUYIN,
            content_type=ContentTypeEnum.VIDEO,
            topic="必看内容",
            keywords=["必看"],
            tone="energetic",
            length=500
        )

        response = await self.generator.generate(request)

        # 应该包含黄金3秒的建议
        assert "0:00-0:03" in response.content.body


class TestContentGenerationService:
    """内容生成服务集成测试"""

    @pytest.mark.asyncio
    async def test_generate_all_platforms(self):
        """测试多平台内容生成"""
        service = ContentGenerationService()

        platforms = [
            (PlatformEnum.WECHAT, WeChatContentGenerator()),
            (PlatformEnum.XIAOHONGSHU, XiaohongshuContentGenerator()),
            (PlatformEnum.DOUYIN, DouyinContentGenerator()),
        ]

        for platform, _ in platforms:
            request = ContentGenerationRequest(
                platform=platform,
                content_type=ContentTypeEnum.ARTICLE,
                topic="测试主题",
                keywords=["测试"],
                tone="professional",
                length=500
            )

            response = await service.generate_content(request)
            assert response.request_id is not None
            assert response.content is not None
            assert response.quality_score > 0

    @pytest.mark.asyncio
    async def test_batch_generate(self):
        """测试批量内容生成"""
        service = ContentGenerationService()

        requests = [
            ContentGenerationRequest(
                platform=PlatformEnum.WECHAT,
                content_type=ContentTypeEnum.ARTICLE,
                topic=f"主题{i}",
                keywords=["测试"],
                tone="professional",
                length=500
            )
            for i in range(3)
        ]

        responses = await service.batch_generate(requests)

        assert len(responses) == 3
        assert all(r.request_id is not None for r in responses)
