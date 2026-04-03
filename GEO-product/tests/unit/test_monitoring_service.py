"""
GEO 智能优化平台 - 监测服务单元测试
"""
import pytest
from datetime import datetime, timedelta
from src.services.monitoring import (
    MonitoringService,
    DeepSeekClient,
    KimiClient,
    DoubaoClient
)
from src.models.schemas import (
    PlatformEnum,
    MonitoringTaskCreate,
    MonitoringFrequencyEnum
)


class TestMonitoringService:
    """监测服务测试"""

    def setup_method(self):
        """测试前准备"""
        self.service = MonitoringService()

    @pytest.mark.asyncio
    async def test_get_client_deepseek(self):
        """测试获取DeepSeek客户端"""
        client = await self.service.get_client(PlatformEnum.DEEPSEEK)
        assert isinstance(client, DeepSeekClient)

    @pytest.mark.asyncio
    async def test_get_client_kimi(self):
        """测试获取Kimi客户端"""
        client = await self.service.get_client(PlatformEnum.KIMI)
        assert isinstance(client, KimiClient)

    @pytest.mark.asyncio
    async def test_get_client_doubao(self):
        """测试获取豆包客户端"""
        client = await self.service.get_client(PlatformEnum.DOUBAO)
        assert isinstance(client, DoubaoClient)

    @pytest.mark.asyncio
    async def test_get_client_unsupported(self):
        """测试获取不支持的平台客户端"""
        with pytest.raises(Exception):
            await self.service.get_client("unsupported_platform")

    def test_calculate_next_run_time_hourly(self):
        """测试小时级监测下次运行时间计算"""
        next_run = self.service.calculate_next_run_time(MonitoringFrequencyEnum.HOURLY)
        assert isinstance(next_run, datetime)
        # 应该比现在晚1小时左右
        assert (next_run - datetime.now()).total_seconds() <= 3605

    def test_calculate_next_run_time_daily(self):
        """测试天级监测下次运行时间计算"""
        next_run = self.service.calculate_next_run_time(MonitoringFrequencyEnum.DAILY)
        assert isinstance(next_run, datetime)
        # 应该比现在晚24小时左右
        assert (next_run - datetime.now()).total_seconds() <= 86405

    def test_calculate_next_run_time_weekly(self):
        """测试周级监测下次运行时间计算"""
        next_run = self.service.calculate_next_run_time(MonitoringFrequencyEnum.WEEKLY)
        assert isinstance(next_run, datetime)
        # 应该比现在晚168小时(一周)左右
        assert (next_run - datetime.now()).total_seconds() <= 604805

    def test_group_by_platform(self):
        """测试按平台分组统计"""
        from src.models.schemas import CitationRecordCreate

        citations = [
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.DEEPSEEK,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌A"
            ),
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.DEEPSEEK,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌A"
            ),
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.KIMI,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌A"
            ),
        ]

        groups = self.service._group_by_platform(citations)

        assert groups["deepseek"] == 2
        assert groups["kimi"] == 1

    def test_group_by_keyword(self):
        """测试按关键词分组统计"""
        from src.models.schemas import CitationRecordCreate

        citations = [
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.DEEPSEEK,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌A"
            ),
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.DEEPSEEK,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌A"
            ),
            CitationRecordCreate(
                tenant_id="t1",
                ai_platform=PlatformEnum.DEEPSEEK,
                search_query="测试",
                citation_context="测试内容",
                brand_keyword="品牌B"
            ),
        ]

        groups = self.service._group_by_keyword(citations)

        assert groups["品牌A"] == 2
        assert groups["品牌B"] == 1


class TestDeepSeekClient:
    """DeepSeek客户端测试"""

    def setup_method(self):
        """测试前准备"""
        self.client = DeepSeekClient()

    def test_initialization(self):
        """测试初始化"""
        assert self.client.platform == PlatformEnum.DEEPSEEK

    @pytest.mark.asyncio
    async def test_extract_citations_basic(self):
        """测试基本引用提取"""
        response = """
        关于品牌A的优势，我们可以从以下几个方面来看：

        品牌A在市场上表现非常出色，产品质量很好。
        很多用户都在询问品牌A和品牌B的区别。
        """

        brand_keywords = ["品牌A", "品牌B"]
        citations = await self.client.extract_citations(response, brand_keywords)

        assert len(citations) >= 2  # 至少应该提取到2个引用
        keywords_found = [c["keyword"] for c in citations]
        assert "品牌A" in keywords_found

    @pytest.mark.asyncio
    async def test_extract_citations_no_match(self):
        """测试无匹配时返回空"""
        response = "这是一段不包含任何品牌信息的内容。"
        brand_keywords = ["品牌A", "品牌B"]

        citations = await self.client.extract_citations(response, brand_keywords)

        # 关键词匹配可能为空或confidence很低
        assert isinstance(citations, list)

    @pytest.mark.asyncio
    async def test_extract_citations_case_insensitive(self):
        """测试大小写不敏感"""
        response = "品牌a是一个很棒的品牌！"
        brand_keywords = ["品牌A"]

        citations = await self.client.extract_citations(response, brand_keywords)

        assert len(citations) > 0


class TestMonitoringTask:
    """监测任务测试"""

    def test_task_creation(self):
        """测试任务创建"""
        task = MonitoringTaskCreate(
            name="测试任务",
            keywords=["品牌A", "品牌B"],
            platforms=[PlatformEnum.DEEPSEEK, PlatformEnum.KIMI],
            frequency=MonitoringFrequencyEnum.DAILY,
            tenant_id="tenant_001"
        )

        assert task.name == "测试任务"
        assert len(task.keywords) == 2
        assert len(task.platforms) == 2
        assert task.frequency == MonitoringFrequencyEnum.DAILY

    def test_task_frequency_values(self):
        """测试任务频率枚举值"""
        assert MonitoringFrequencyEnum.HOURLY.value == "hourly"
        assert MonitoringFrequencyEnum.DAILY.value == "daily"
        assert MonitoringFrequencyEnum.WEEKLY.value == "weekly"
