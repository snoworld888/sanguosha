"""
GEO 智能优化平台 - 内容生成服务
"""
from typing import List, Dict, Any, Optional
import asyncio
import re
import uuid
from datetime import datetime

from src.core.config import settings
from src.core.exceptions import ContentPolicyError
from src.models.schemas import (
    PlatformEnum,
    ContentTypeEnum,
    ContentGenerationRequest,
    GeneratedContent,
    ContentGenerationResponse
)


class ContentPolicyChecker:
    """内容合规审核"""

    # 敏感词列表（实际项目中从数据库或文件加载）
    SENSITIVE_WORDS = [
        "暴力", "色情", "毒品", "赌博", "诈骗",
        "分裂", "恐怖", "谣言"
    ]

    # 广告法极限词
    EXTREME_WORDS = [
        "最好", "最佳", "第一", "顶级", "极品",
        "国家级", "世界级", "全网最低", "独一无二"
    ]

    # 抖音禁发内容
    DOUYIN_BANNED = [
        "枪支", "管制刀具", "毒品", "赌博",
        "色情内容", "虚假信息", "封建迷信"
    ]

    def __init__(self):
        self.sensitive_pattern = re.compile(
            "|".join(self.SENSITIVE_WORDS),
            re.IGNORECASE
        )
        self.extreme_pattern = re.compile(
            "|".join(self.EXTREME_WORDS),
            re.IGNORECASE
        )

    def check(self, content: str, platform: PlatformEnum = None) -> Dict[str, Any]:
        """检查内容合规性"""
        warnings = []
        errors = []

        # 敏感词检查
        sensitive_matches = self.sensitive_pattern.findall(content)
        if sensitive_matches:
            errors.append(f"包含敏感词: {', '.join(set(sensitive_matches))}")

        # 广告法合规检查
        extreme_matches = self.extreme_pattern.findall(content)
        if extreme_matches:
            warnings.append(f"可能违反广告法极限词规定: {', '.join(set(extreme_matches))}")

        # 平台特定检查
        if platform == PlatformEnum.DOUYIN:
            for banned in self.DOUYIN_BANNED:
                if banned in content:
                    warnings.append(f"抖音平台可能禁发内容: {banned}")

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class ContentGenerator:
    """内容生成器基类"""

    def __init__(self):
        self.policy_checker = ContentPolicyChecker()

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成内容"""
        raise NotImplementedError

    def _apply_geo_optimization(
        self,
        content: GeneratedContent,
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """应用GEO优化"""
        # 添加SEO友好的标题
        if request.keywords:
            main_keyword = request.keywords[0]
            if main_keyword not in content.title:
                content.title = f"{content.title} - {main_keyword}"

            # 添加关键词到标签
            for keyword in request.keywords[:5]:
                if keyword not in content.tags:
                    content.tags.append(keyword)

        return content


class WeChatContentGenerator(ContentGenerator):
    """微信公众号内容生成器"""

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成公众号内容"""
        request_id = str(uuid.uuid4())

        # 模拟内容生成（实际项目中调用AI API）
        title = self._generate_title(request.topic, request.tone)
        body = await self._generate_body(request)

        content = GeneratedContent(
            title=title,
            body=body,
            cover_url=None,  # 需要调用图像生成服务
            tags=self._generate_tags(request.keywords),
            estimated_read_time=len(body) // 500,
            seo_suggestions=[
                "标题建议包含关键词",
                "首段应包含核心信息",
                "建议添加相关阅读链接"
            ]
        )

        # 应用GEO优化
        content = self._apply_geo_optimization(content, request)

        # 合规检查
        policy_result = self.policy_checker.check(
            content.body,
            PlatformEnum.WECHAT
        )

        return ContentGenerationResponse(
            request_id=request_id,
            content=content,
            quality_score=85.0,
            warnings=policy_result["warnings"] + policy_result["errors"]
        )

    def _generate_title(self, topic: str, tone: str) -> str:
        """生成标题"""
        templates = [
            f"深入解析：{topic}",
            f"关于{topic}，你需要知道的一切",
            f"{topic}完全指南",
            f"一文读懂{topic}"
        ]
        return templates[0]

    async def _generate_body(self, request: ContentGenerationRequest) -> str:
        """生成正文"""
        sections = []

        # 引言
        sections.append(f"# {request.topic}\n\n")
        sections.append(f"在本文中，我们将全面探讨{request.topic}，帮助您深入理解这一主题。\n\n")

        # 关键词覆盖
        if request.keywords:
            sections.append("## 核心要点\n\n")
            for i, keyword in enumerate(request.keywords[:3], 1):
                sections.append(f"{i}. **{keyword}**：这是关于{keyword}的重要内容。\n")
            sections.append("\n")

        # 正文内容
        sections.append("## 详细内容\n\n")
        sections.append(f"关于{request.topic}的深入分析表明，这一领域正在快速发展。")
        sections.append("企业在进行GEO优化时，需要注意以下几点：\n\n")
        sections.append("1. 内容结构要清晰，便于AI理解和引用\n")
        sections.append("2. 要提供充分的证据和数据支撑\n")
        sections.append("3. 保持内容的权威性和专业性\n\n")

        # 总结
        sections.append("## 总结\n\n")
        sections.append(f"通过对{request.topic}的全面分析，我们可以看到...")
        sections.append("希望本文能为您提供有价值的参考。\n")

        return "".join(sections)

    def _generate_tags(self, keywords: List[str]) -> List[str]:
        """生成标签"""
        tags = keywords.copy() if keywords else []
        tags.extend(["GEO优化", "AI搜索", "内容营销"])
        return list(set(tags))[:10]


class ZhihuContentGenerator(ContentGenerator):
    """知乎内容生成器"""

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成知乎回答"""
        request_id = str(uuid.uuid4())

        title = self._generate_title(request.topic)
        body = await self._generate_body(request)

        content = GeneratedContent(
            title=title,
            body=body,
            cover_url=None,
            tags=self._generate_tags(request.keywords),
            estimated_read_time=len(body) // 500,
            seo_suggestions=[
                "建议添加 TL;DR 要点总结",
                "使用目录结构提高可读性",
                "引用权威来源增加可信度"
            ]
        )

        content = self._apply_geo_optimization(content, request)

        policy_result = self.policy_checker.check(content.body, PlatformEnum.ZHUHU)

        return ContentGenerationResponse(
            request_id=request_id,
            content=content,
            quality_score=88.0,
            warnings=policy_result["warnings"] + policy_result["errors"]
        )

    def _generate_title(self, topic: str) -> str:
        return f"\"{topic}\" 深度解析：从入门到精通"

    async def _generate_body(self, request: ContentGenerationRequest) -> str:
        sections = []

        # TL;DR
        sections.append("> **TL;DR**\n")
        sections.append(f"> 本文将为您全面解析{request.topic}的核心要点。\n\n")

        # 目录
        sections.append("## 目录\n")
        sections.append("- 一、背景介绍\n")
        sections.append("- 二、核心概念\n")
        sections.append("- 三、实践方法\n")
        sections.append("- 四、总结与建议\n\n")

        # 正文
        sections.append("## 一、背景介绍\n\n")
        sections.append(f"关于{request.topic}，我们需要先了解其产生的背景...\n\n")

        sections.append("## 二、核心概念\n\n")
        if request.keywords:
            for keyword in request.keywords:
                sections.append(f"**{keyword}**：这是理解{request.topic}的关键概念。\n")
        sections.append("\n")

        sections.append("## 三、实践方法\n\n")
        sections.append("在实际应用中，我们可以采取以下方法：\n\n")
        sections.append("1. 充分调研，了解现状\n")
        sections.append("2. 制定合理策略\n")
        sections.append("3. 持续优化迭代\n\n")

        sections.append("## 四、总结与建议\n\n")
        sections.append("综上所述，...")

        return "".join(sections)

    def _generate_tags(self, keywords: List[str]) -> List[str]:
        tags = keywords.copy() if keywords else []
        tags.extend(["知乎专栏", "深度好文", "收藏夹"])
        return list(set(tags))[:10]


class XiaohongshuContentGenerator(ContentGenerator):
    """小红书内容生成器"""

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成小红书笔记"""
        request_id = str(uuid.uuid4())

        title = self._generate_title(request.topic)
        body = await self._generate_body(request)

        content = GeneratedContent(
            title=title,
            body=body,
            cover_url=None,
            tags=self._generate_tags(request.keywords),
            estimated_read_time=len(body) // 300,
            seo_suggestions=[
                "封面建议使用3:4比例",
                "前3行要吸引眼球",
                "添加热门标签增加曝光"
            ]
        )

        content = self._apply_geo_optimization(content, request)

        policy_result = self.policy_checker.check(content.body, PlatformEnum.XIAOHONGSHU)

        return ContentGenerationResponse(
            request_id=request_id,
            content=content,
            quality_score=82.0,
            warnings=policy_result["warnings"] + policy_result["errors"]
        )

    def _generate_title(self, topic: str) -> str:
        return f"📚 {topic} | 保姆级教程，建议收藏！"

    async def _generate_body(self, request: ContentGenerationRequest) -> str:
        sections = []

        # 开场钩子
        sections.append("姐妹们！👋 今天来聊聊这个话题～\n\n")
        sections.append(f"关于{request.topic}，你是不是也有这些困惑？🤔\n\n")

        # 核心内容
        sections.append("---\n\n")
        sections.append("### 📌 什么是GEO？\n\n")
        sections.append("GEO（Generative Engine Optimization）...")
        sections.append("简单来说，就是让你的内容更容易被AI引用！✨\n\n")

        if request.keywords:
            sections.append("### 🔑 关键词\n")
            for keyword in request.keywords:
                sections.append(f"- #{keyword} ")
            sections.append("\n\n")

        # 结尾引导
        sections.append("---\n\n")
        sections.append("觉得有用的话记得点个赞 👍 和收藏 📌\n")
        sections.append("有问题评论区见～ 💬\n")

        return "".join(sections)

    def _generate_tags(self, keywords: List[str]) -> List[str]:
        tags = keywords.copy() if keywords else []
        tags.extend(["GEO优化", "AI", "干货分享", "小红书运营"])
        return list(set(tags))[:10]


class DouyinContentGenerator(ContentGenerator):
    """抖音内容生成器"""

    async def generate(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成抖音视频脚本"""
        request_id = str(uuid.uuid4())

        title = self._generate_title(request.topic)
        body = await self._generate_body(request)

        content = GeneratedContent(
            title=title,
            body=body,
            cover_url=None,
            tags=self._generate_tags(request.keywords),
            estimated_read_time=60,
            seo_suggestions=[
                "视频前3秒需要有强钩子",
                "添加字幕提高完播率",
                "结尾要有互动引导"
            ]
        )

        content = self._apply_geo_optimization(content, request)

        policy_result = self.policy_checker.check(content.body, PlatformEnum.DOUYIN)

        return ContentGenerationResponse(
            request_id=request_id,
            content=content,
            quality_score=80.0,
            warnings=policy_result["warnings"] + policy_result["errors"]
        )

    def _generate_title(self, topic: str) -> str:
        return f"必看！{topic}这些坑千万不要踩！👀"

    async def _generate_body(self, request: ContentGenerationRequest) -> str:
        sections = []

        # 黄金3秒钩子
        sections.append("【开场钩子 - 0:00-0:03】\n")
        sections.append("❌ 99%的人都在犯这个错误...\n\n")

        # 痛点陈述
        sections.append("【痛点 - 0:03-0:10】\n")
        sections.append(f"关于{request.topic}，你是不是也遇到过...\n\n")

        # 核心内容
        sections.append("【核心内容 - 0:10-0:45】\n")
        sections.append("✅ 正确的方法是：\n")
        sections.append("1. 第一步...\n")
        sections.append("2. 第二步...\n")
        sections.append("3. 第三步...\n\n")

        if request.keywords:
            sections.append("【关键词】\n")
            sections.append(" ".join([f"#{k}" for k in request.keywords[:5]]))
            sections.append("\n\n")

        # 结尾引导
        sections.append("【结尾引导 - 0:45-0:55】\n")
        sections.append("觉得有用的话，点个赞 👍\n")
        sections.append("关注我，每天分享实用干货！\n\n")

        # 字幕建议
        sections.append("【字幕建议】\n")
        sections.append("全程添加字幕，提高完播率\n")

        return "".join(sections)

    def _generate_tags(self, keywords: List[str]) -> List[str]:
        tags = keywords.copy() if keywords else []
        tags.extend(["抖音", "干货", "教程", "必看"])
        return list(set(tags))[:10]


class ContentGenerationService:
    """内容生成服务"""

    def __init__(self):
        self.generators = {
            PlatformEnum.WECHAT: WeChatContentGenerator(),
            PlatformEnum.ZHUHU: ZhihuContentGenerator(),
            PlatformEnum.XIAOHONGSHU: XiaohongshuContentGenerator(),
            PlatformEnum.DOUYIN: DouyinContentGenerator(),
        }

    async def generate_content(
        self,
        request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """生成内容"""
        generator = self.generators.get(request.platform)
        if not generator:
            raise ValueError(f"不支持的平台: {request.platform}")

        return await generator.generate(request)

    async def batch_generate(
        self,
        requests: List[ContentGenerationRequest]
    ) -> List[ContentGenerationResponse]:
        """批量生成内容"""
        tasks = [self.generate_content(req) for req in requests]
        return await asyncio.gather(*tasks)


# 服务单例
content_generation_service = ContentGenerationService()
