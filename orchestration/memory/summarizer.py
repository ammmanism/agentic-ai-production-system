import asyncio
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["history"],
    template="""You are compressing a long conversation. Write a concise summary that preserves:
- All key decisions, facts, and user preferences
- The main unresolved questions or action items

Original conversation:
{history}

Concise summary:"""
)

# Mock replacement for core.llm get_llm
def get_llm():
    return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

class MemorySummarizer:
    def __init__(self, llm=None, max_tokens_before_summary=3000):
        self.llm = llm or get_llm()
        self.max_tokens_before_summary = max_tokens_before_summary
        self.chain = LLMChain(llm=self.llm, prompt=SUMMARY_PROMPT)

    async def should_summarize(self, messages: List[BaseMessage]) -> bool:
        """Approximate token count – can be replaced with tiktoken."""
        total_chars = sum(len(m.content) for m in messages if hasattr(m, 'content'))
        approx_tokens = total_chars // 4  # rough
        return approx_tokens > self.max_tokens_before_summary

    async def summarize(self, messages: List[BaseMessage]) -> str:
        """Generate a compressed summary of the conversation history."""
        # Format messages into a readable string
        history_str = "\\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in messages
        )
        summary = await self.chain.arun(history=history_str)
        return summary.strip()

    async def compress_if_needed(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Return a compressed version: [System(summary), *last_few_messages]"""
        if not await self.should_summarize(messages):
            return messages

        summary_text = await self.summarize(messages[:-4])  # keep last 4 raw
        compressed_messages = [
            HumanMessage(content=f"[Previous conversation summary]\\n{summary_text}"),
            *messages[-4:]  # keep recent context
        ]
        return compressed_messages
