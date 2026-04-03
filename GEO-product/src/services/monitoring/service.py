"""
GEO 智能优化平台 - AI平台监测服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import httpx
from abc import ABC, abstractmethod
import re

from src.core.config import settings
from src.core.exceptions import MonitoringError, AIPlatformError, ExternalAPIError
from src.models.schemas import (
    PlatformEnum,
    MonitoringTaskCreate,
    CitationRecordCreate,
    MonitoringFrequencyEnum
)


class BaseAIClient(ABC):
    """AI平台客户端基类"""

    def __init__(self, platform: PlatformEnum, api_key: Optional[str] = None):
        self.platform = platform
        self.api_key = api_key or ""
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """执行搜索"""
        pass

    @abstractmethod
    async def extract_citations(self, response: str, brand_keywords: List[str]) -> List[Dict[str, Any]]:
        """提取引用信息"""
        pass

    async def close(self):
        await self.client.aclose()


class DeepSeekClient(BaseAIClient):
    """DeepSeek AI客户端"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(PlatformEnum.DEEPSEEK, api_key)

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行DeepSeek搜索查询"""
        try:
            # 调用DeepSeek API
            response = await self.client.post(
                f"{settings.DEEPSEEK_API_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key or settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": "你是一个有用的AI助手。"},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise AIPlatformError(f"DeepSeek API调用失败: {str(e)}")

    async def extract_citations(self, response: str, brand_keywords: List[str]) -> List[Dict[str, Any]]:
        """从DeepSeek响应中提取品牌引用"""
        citations = []
        for keyword in brand_keywords:
            # 简单的关键词匹配，实际项目中需要更复杂的NLP处理
            pattern = rf".{{0,100}}{re.escape(keyword)}.{{0,100}}"
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                citations.append({
                    "keyword": keyword,
                    "context": match.strip(),
                    "confidence": 0.8 if keyword.lower() in response.lower() else 0.5
                })
        return citations


class KimiClient(BaseAIClient):
    """Kimi AI客户端"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(PlatformEnum.KIMI, api_key)
        # Kimi使用 moonshot API
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行Kimi搜索查询"""
        try:
            response = await self.client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "moonshot-v1-8k",
                    "messages": [
                        {"role": "system", "content": "你是一个有用的AI助手。"},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise AIPlatformError(f"Kimi API调用失败: {str(e)}")

    async def extract_citations(self, response: str, brand_keywords: List[str]) -> List[Dict[str, Any]]:
        """从Kimi响应中提取品牌引用"""
        return await super().extract_citations(response, brand_keywords)


class DoubaoClient(BaseAIClient):
    """豆包 AI客户端"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(PlatformEnum.DOUBAO, api_key)
        self.api_url = f"{settings.VOLCANO_ENDPOINT}/chat/completions"

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行豆包搜索查询"""
        try:
            response = await self.client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key or settings.VOLCANO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "doubao-pro",
                    "messages": [
                        {"role": "system", "content": "你是一个有用的AI助手。"},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise AIPlatformError(f"豆包API调用失败: {str(e)}")

    async def extract_citations(self, response: str, brand_keywords: List[str]) -> List[Dict[str, Any]]:
        """从豆包响应中提取品牌引用"""
        return await super().extract_citations(response, brand_keywords)


class WenxinClient(BaseAIClient):
    """文心一言 AI客户端"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(PlatformEnum.WENXIN, api_key)

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """执行文心一言搜索查询"""
        # 百度文心一言API实现
        raise NotImplementedError("文心一言API接入需要额外的认证流程")

    async def extract_citations(self, response: str, brand_keywords: List[str]) -> List[Dict[str, Any]]:
        """从文心一言响应中提取品牌引用"""
        return await super().extract_citations(response, brand_keywords)


class MonitoringService:
    """监测服务"""

    def __init__(self):
        self.clients: Dict[PlatformEnum, BaseAIClient] = {
            PlatformEnum.DEEPSEEK: DeepSeekClient(),
            PlatformEnum.KIMI: KimiClient(),
            PlatformEnum.DOUBAO: DoubaoClient(),
            PlatformEnum.WENXIN: WenxinClient(),
        }

    async def get_client(self, platform: PlatformEnum) -> BaseAIClient:
        """获取AI平台客户端"""
        if platform not in self.clients:
            raise MonitoringError(f"不支持的平台: {platform}")
        return self.clients[platform]

    async def run_monitoring_task(
        self,
        task: MonitoringTaskCreate,
        tenant_id: str
    ) -> List[CitationRecordCreate]:
        """执行监测任务"""
        results = []

        for platform in task.platforms:
            client = await self.get_client(platform)

            for keyword in task.keywords:
                try:
                    # 构建搜索查询
                    query = f"{keyword}怎么样？"

                    # 调用AI平台
                    response = await client.search(query)

                    # 提取回复内容
                    content = ""
                    if "choices" in response:
                        content = response["choices"][0]["message"]["content"]

                    # 提取引用
                    citations = await client.extract_citations(content, task.keywords)

                    # 创建引用记录
                    for citation in citations:
                        record = CitationRecordCreate(
                            tenant_id=tenant_id,
                            ai_platform=platform,
                            search_query=query,
                            citation_context=citation["context"],
                            brand_keyword=citation["keyword"]
                        )
                        results.append(record)

                except Exception as e:
                    raise MonitoringError(f"监测任务执行失败 [{platform}]: {str(e)}")

        return results

    async def batch_monitor(
        self,
        tenant_id: str,
        keywords: List[str],
        platforms: List[PlatformEnum],
        frequency: MonitoringFrequencyEnum = MonitoringFrequencyEnum.DAILY
    ) -> Dict[str, Any]:
        """批量监测"""
        task = MonitoringTaskCreate(
            name=f"batch_monitor_{datetime.now().isoformat()}",
            keywords=keywords,
            platforms=platforms,
            frequency=frequency,
            tenant_id=tenant_id
        )

        results = await self.run_monitoring_task(task, tenant_id)

        return {
            "total_citations": len(results),
            "citations_by_platform": self._group_by_platform(results),
            "citations_by_keyword": self._group_by_keyword(results),
            "timestamp": datetime.now().isoformat()
        }

    def _group_by_platform(self, citations: List[CitationRecordCreate]) -> Dict[str, int]:
        """按平台分组统计"""
        groups = {}
        for citation in citations:
            platform = citation.ai_platform
            groups[platform] = groups.get(platform, 0) + 1
        return groups

    def _group_by_keyword(self, citations: List[CitationRecordCreate]) -> Dict[str, int]:
        """按关键词分组统计"""
        groups = {}
        for citation in citations:
            keyword = citation.brand_keyword
            groups[keyword] = groups.get(keyword, 0) + 1
        return groups

    def calculate_next_run_time(self, frequency: MonitoringFrequencyEnum) -> datetime:
        """计算下次运行时间"""
        now = datetime.now()
        hours = settings.MONITORING_FREQUENCY.get(frequency.value, 24)
        return now + timedelta(hours=hours)


# 服务单例
monitoring_service = MonitoringService()
