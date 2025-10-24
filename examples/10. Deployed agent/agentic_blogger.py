"""🎨 Blog Post Generator v2.0 - Your AI Content Creation Studio!

This advanced example demonstrates how to build a sophisticated blog post generator using
the new workflow v2.0 architecture. The workflow combines web research capabilities with
professional writing expertise using a multi-stage approach:

1. Intelligent web research and source gathering
2. Content extraction and processing
3. Professional blog post writing with proper citations

Key capabilities:
- Advanced web research and source evaluation
- Content scraping and processing
- Professional writing with SEO optimization
- Automatic content caching for efficiency
- Source attribution and fact verification
"""

import json
from textwrap import dedent
from typing import Dict, Optional

from agno.team import Team
from agno.agent import Agent
from agno.workflow.workflow import Workflow
from agno.workflow.types import WorkflowExecutionInput

from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini

from agno.tools.tavily import TavilyTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.newspaper4k import Newspaper4kTools

from agno.utils.log import logger
from pydantic import BaseModel, Field

from agno.os import AgentOS

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

# --- Observability ---
import openlit
from langfuse import get_client

# Instrument code
langfuse = get_client()
openlit.init(tracer=langfuse._otel_tracer, disable_batch=True)

# --- Response Models ---
class ResearchTopic(BaseModel):
    """Structured research topic with specific requirements"""
    topic: str = Field(description="Topic to focus on")


class NewsArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(
        ..., description="Summary of the article if available."
    )


class SearchResults(BaseModel):
    articles: list[NewsArticle]


class ScrapedArticle(BaseModel):
    title: str = Field(..., description="Title of the article.")
    url: str = Field(..., description="Link to the article.")
    summary: Optional[str] = Field(
        ..., description="Summary of the article if available."
    )
    content: Optional[str] = Field(
        ...,
        description="Full article content in markdown format. None if content is unavailable.",
    )

# --- Tools ---
search = TavilyTools(
    include_answer=True,
    search_depth='basic',
    format='markdown',
    max_tokens=100
)

# --- Agents ---
research_agent = Agent(
    name="Blog Research Agent",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[search],
    description=dedent("""\
    You are BlogResearch-X, an elite research assistant specializing in discovering
    high-quality sources for compelling blog content. Your expertise includes:

    - Finding authoritative and trending sources
    - Evaluating content credibility and relevance
    - Identifying diverse perspectives and expert opinions
    - Discovering unique angles and insights
    - Ensuring comprehensive topic coverage
    """),
    instructions=dedent("""\
    1. Search Strategy 🔍
       - Find 10-15 relevant sources and select the 5-7 best ones
       - Prioritize recent, authoritative content
       - Look for unique angles and expert insights
    2. Source Evaluation 📊
       - Verify source credibility and expertise
       - Check publication dates for timeliness
       - Assess content depth and uniqueness
    3. Diversity of Perspectives 🌐
       - Include different viewpoints
       - Gather both mainstream and expert opinions
       - Find supporting data and statistics
    """),
    output_schema=SearchResults,
)

content_scraper_agent = Agent(
    name="Content Scraper Agent",
    model=OpenAIChat(id="gpt-5-mini"),
    tools=[Newspaper4kTools()],
    description=dedent("""\
    You are ContentBot-X, a specialist in extracting and processing digital content
    for blog creation. Your expertise includes:

    - Efficient content extraction
    - Smart formatting and structuring
    - Key information identification
    - Quote and statistic preservation
    - Maintaining source attribution
    """),
    instructions=dedent("""\
    1. Content Extraction 📑
       - Extract content from the article
       - Preserve important quotes and statistics
       - Maintain proper attribution
       - Handle paywalls gracefully
    2. Content Processing 🔄
       - Format text in clean markdown
       - Preserve key information
       - Structure content logically
    3. Quality Control ✅
       - Verify content relevance
       - Ensure accurate extraction
       - Maintain readability
    """),
    output_schema=ScrapedArticle,
)

blog_writer_agent = Agent(
    name="Blog Writer Agent",
    model=OpenAIChat(id="gpt-5-mini"),
    description=dedent("""\
    You are BlogMaster-X, an elite content creator combining journalistic excellence
    with digital marketing expertise. Your strengths include:

    - Crafting viral-worthy headlines
    - Writing engaging introductions
    - Structuring content for digital consumption
    - Incorporating research seamlessly
    - Optimizing for SEO while maintaining quality
    - Creating shareable conclusions
    """),
    instructions=dedent("""\
    1. Content Strategy 📝
       - Craft attention-grabbing headlines
       - Write compelling introductions
       - Structure content for engagement
       - Include relevant subheadings
    2. Writing Excellence ✍️
       - Balance expertise with accessibility
       - Use clear, engaging language
       - Include relevant examples
       - Incorporate statistics naturally
    3. Source Integration 🔍
       - Cite sources properly
       - Include expert quotes
       - Maintain factual accuracy
    4. Digital Optimization 💻
       - Structure for scanability
       - Include shareable takeaways
       - Optimize for SEO
       - Add engaging subheadings

    Format your blog post with this structure:
    # {Viral-Worthy Headline}

    ## Introduction
    {Engaging hook and context}

    ## {Compelling Section 1}
    {Key insights and analysis}
    {Expert quotes and statistics}

    ## {Engaging Section 2}
    {Deeper exploration}
    {Real-world examples}

    ## {Practical Section 3}
    {Actionable insights}
    {Expert recommendations}

    ## Key Takeaways
    - {Shareable insight 1}
    - {Practical takeaway 2}
    - {Notable finding 3}

    ## Sources
    {Properly attributed sources with links}
    """),
    markdown=True,
)

# --- Team ---
blog_team = Team(
    name="Blogger team",
    model=Gemini(id="gemini-2.5-flash", temperature=0.3),
    members=[research_agent, content_scraper_agent, blog_writer_agent],
    tools=[ReasoningTools(add_instructions=True)],
    instructions=[
        "Collaborate to provide comprehensive blog entry for the topic provided",
        "Make it engaging but factual, meaning any information has to be linked to its source",
    ],
    markdown=True,
    show_members_responses=True,
    enable_agentic_state=True,
)

# --- Helper Functions ---
async def get_cached_blog_post(session_state, topic: str) -> Optional[str]:
    """Get cached blog post from workflow session state"""
    logger.info("Checking if cached blog post exists")
    return session_state.get("blog_posts", {}).get(topic)


def cache_blog_post(session_state, topic: str, blog_post: str):
    """Cache blog post in workflow session state"""
    logger.info(f"Saving blog post for topic: {topic}")
    if "blog_posts" not in session_state:
        session_state["blog_posts"] = {}
    session_state["blog_posts"][topic] = blog_post


def get_cached_search_results(session_state, topic: str) -> Optional[SearchResults]:
    """Get cached search results from workflow session state"""
    logger.info("Checking if cached search results exist")
    search_results = session_state.get("search_results", {}).get(topic)
    if search_results and isinstance(search_results, dict):
        try:
            return SearchResults.model_validate(search_results)
        except Exception as e:
            logger.warning(f"Could not validate cached search results: {e}")
    return search_results if isinstance(search_results, SearchResults) else None


def cache_search_results(session_state, topic: str, search_results: SearchResults):
    """Cache search results in workflow session state"""
    logger.info(f"Saving search results for topic: {topic}")
    if "search_results" not in session_state:
        session_state["search_results"] = {}
    session_state["search_results"][topic] = search_results.model_dump()


async def get_cached_scraped_articles(
    session_state, topic: str
) -> Optional[Dict[str, ScrapedArticle]]:
    """Get cached scraped articles from workflow session state"""
    logger.info("Checking if cached scraped articles exist")
    scraped_articles = session_state.get("scraped_articles", {}).get(topic)
    if scraped_articles and isinstance(scraped_articles, dict):
        try:
            return {
                url: ScrapedArticle.model_validate(article)
                for url, article in scraped_articles.items()
            }
        except Exception as e:
            logger.warning(f"Could not validate cached scraped articles: {e}")
    return scraped_articles if isinstance(scraped_articles, dict) else None


def cache_scraped_articles(
    session_state, topic: str, scraped_articles: Dict[str, ScrapedArticle]
):
    """Cache scraped articles in workflow session state"""
    logger.info(f"Saving scraped articles for topic: {topic}")
    if "scraped_articles" not in session_state:
        session_state["scraped_articles"] = {}
    session_state["scraped_articles"][topic] = {
        url: article.model_dump() for url, article in scraped_articles.items()
    }


async def get_search_results(
    session_state, topic: str, use_cache: bool = True, num_attempts: int = 3
) -> Optional[SearchResults]:
    """Get search results with caching support"""

    # Check cache first
    if use_cache:
        cached_results = get_cached_search_results(session_state, topic)
        if cached_results:
            logger.info(f"Found {len(cached_results.articles)} articles in cache.")
            return cached_results

    # Search for new results
    for attempt in range(num_attempts):
        try:
            logger.info(
                f"🔍 Searching for articles about: {topic} (attempt {attempt + 1}/{num_attempts})"
            )
            response = await research_agent.arun(topic)

            if (
                response
                and response.content
                and isinstance(response.content, SearchResults)
            ):
                article_count = len(response.content.articles)
                logger.info(f"Found {article_count} articles on attempt {attempt + 1}")

                # Cache the results
                cache_search_results(session_state, topic, response.content)
                return response.content
            else:
                logger.warning(
                    f"Attempt {attempt + 1}/{num_attempts} failed: Invalid response type"
                )

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: {str(e)}")

    logger.error(f"Failed to get search results after {num_attempts} attempts")
    return None

async def scrape_articles(
    session_state,
    topic: str,
    search_results: SearchResults,
) -> Dict[str, ScrapedArticle]:
    """Scrape articles with caching support"""

    # Check cache first
    cached_articles = await get_cached_scraped_articles(session_state, topic)
    if cached_articles:
        logger.info(f"Found {len(cached_articles)} scraped articles in cache.")
        return cached_articles

    scraped_articles: Dict[str, ScrapedArticle] = {}

    logger.info(f"📄 Scraping {len(search_results.articles)} articles...")

    for i, article in enumerate(search_results.articles, 1):
        try:
            logger.info(
                f"📖 Scraping article {i}/{len(search_results.articles)}: {article.title[:50]}..."
            )
            response = await content_scraper_agent.arun(article.url)

            if (
                response
                and response.content
                and isinstance(response.content, ScrapedArticle)
            ):
                scraped_articles[response.content.url] = response.content
                logger.info(f"Scraped article: {response.content.url}")
                logger.info(f"✅ Successfully scraped: {response.content.title[:50]}...")
            else:
                logger.info(f"❌ Failed to scrape: {article.title[:50]}...")

        except Exception as e:
            logger.warning(f"Failed to scrape {article.url}: {str(e)}")
            logger.info(f"❌ Error scraping: {article.title[:50]}...")

    # Cache the scraped articles
    cache_scraped_articles(session_state, topic, scraped_articles)
    return scraped_articles


# --- Main Execution Function ---
async def blog_generation_execution(
    workflow: Workflow, execution_input: WorkflowExecutionInput
):
    """
    Blog post generation workflow execution function.

    Args:
        topic: Blog post topic (if not provided, uses execution_input.input)
    """
    logger.info(f"Selected topic {execution_input.input}")
    blog_topic = execution_input.input.topic
    blog_post = None

    if not blog_topic:
        return "❌ No blog topic provided. Please specify a topic."

    logger.info(f"🎨 Generating blog post about: {blog_topic}")
    logger.info("=" * 60)

    # Check for cached blog post first
    cached_blog = await get_cached_blog_post(workflow.session_state, blog_topic)
    if cached_blog:
        logger.info("📋 Found cached blog post!")
        return cached_blog

    # Phase 1: Research and gather sources
    logger.info("\n🔍 PHASE 1: RESEARCH & SOURCE GATHERING")
    logger.info("=" * 50)

    search_results = await get_search_results(workflow.session_state, blog_topic)

    if not search_results or len(search_results.articles) == 0:
        return f"❌ Sorry, could not find any articles on the topic: {blog_topic}"

    logger.info(f"📊 Found {len(search_results.articles)} relevant sources:")
    for i, article in enumerate(search_results.articles, 1):
        logger.info(f"   {i}. {article.title[:60]}...")

    # Phase 2: Content extraction
    logger.info("\n📄 PHASE 2: CONTENT EXTRACTION")
    logger.info("=" * 50)

    scraped_articles = await scrape_articles(workflow.session_state, blog_topic, search_results)

    if not scraped_articles:
        return f"❌ Could not extract content from any articles for topic: {blog_topic}"

    logger.info(f"📖 Successfully extracted content from {len(scraped_articles)} articles")

    # Phase 3: Blog post writing
    logger.info("\n✍️ PHASE 3: BLOG POST CREATION")
    logger.info("=" * 50)

    # Prepare input for the writer
    writer_input = {
        "topic": blog_topic,
        "articles": [article.model_dump() for article in scraped_articles.values()],
    }

    logger.info("🤖 AI is crafting your blog post...")
    writer_response = blog_writer_agent.run(json.dumps(writer_input, indent=2))

    if not writer_response or not writer_response.content:
        return f"❌ Failed to generate blog post for topic: {blog_topic}"

    blog_post = writer_response.content

    # Cache the blog post
    cache_blog_post(workflow.session_state, blog_topic, blog_post)

    logger.info("✅ Blog post generated successfully!")
    logger.info(f"📝 Length: {len(blog_post)} characters")
    logger.info(f"📚 Sources: {len(scraped_articles)} articles")

    return blog_post


# --- Workflow Definition ---
blog_generator_workflow = Workflow(
    name="Blog Post Generator",
    description="Advanced blog post generator with research and content creation capabilities",
    db=SqliteDb(
        session_table="workflow_session",
        db_file="tmp/blog_generator.db",
    ),
    steps=blog_generation_execution,
    input_schema=ResearchTopic,
    session_state={} # Initialize empty session state for caching
)

# Setup our AgentOS app
agentos = AgentOS(
    description="My custom blogger",
    agents=[research_agent, content_scraper_agent, blog_writer_agent],
    teams=[blog_team],
    workflows=[blog_generator_workflow],
    a2a_interface=True
)
app = agentos.get_app()


if __name__ == "__main__":
    """Run your AgentOS.

    You can see the configuration and available apps at:
    http://localhost:7777/config

    """
    agentos.serve(app="agentic_blogger:app", reload=True)
