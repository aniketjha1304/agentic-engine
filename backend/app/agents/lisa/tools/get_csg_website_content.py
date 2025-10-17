import aiohttp
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel, Field

from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.logger import get_logger
from app.config.default import CSG_GUESTS_WEBSITE_ADDRESS

# Get a logger for this module
logger = get_logger(name=__name__)


class GetCSGWebsiteContent(BaseModel):
    """
    Tool to fetch and get the content of a given website URL.
    """


async def explore_website_content() -> str:
    """
    Fetch and explore the content of a given website URL asynchronously using aiohttp.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CSG_GUESTS_WEBSITE_ADDRESS) as response:
                response.raise_for_status()
                html = await response.text()
    except aiohttp.ClientError as e:
        return f"Error: Unable to fetch the website content ({str(e)})"

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    headings = [h.get_text() for h in soup.find_all(["h1", "h2", "h3"])]
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    links = [a["href"] for a in soup.find_all("a", href=True)]

    result = f"Website Title: {title}\n\n"
    if headings:
        result += "Headings:\n" + "\n".join(headings[:5]) + "\n\n"
    if paragraphs:
        result += "Paragraphs:\n" + "\n".join(paragraphs[:5]) + "\n\n"
    if links:
        result += "Links:\n" + "\n".join(links[:5]) + "\n"
    if not headings and not paragraphs and not links:
        result += "No significant content found on the webpage."

    return result


def create_get_csg_website_content_tool():
    """
    Build and return the tool for searching content on a website.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="get-csg-website-content")
    tool_builder.set_function(explore_website_content)
    tool_builder.set_coroutine(explore_website_content)
    tool_builder.set_description(
        description=(
            """Use this tool to fetch available information about guest apartments 
        from the website. If certain details are missing, they might be available here.  
        This is the final source of information you can access—if the required 
        details are not retrieved, the user should visit the website directly.  

        Website: https://www.siedlungsgemeinschaft.de/mieterservice/gaestewohnungen.html  
        """
        )
    )
    tool_builder.set_schema(schema=GetCSGWebsiteContent)
    return tool_builder.build()
