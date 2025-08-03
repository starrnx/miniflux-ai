import fnmatch
import re
from markdownify import markdownify as md
from common.logger import logger

def filter_entry(config, agent, entry):
    start_with_list = [name[1]['title'] for name in config.agents.items()]
    style_block = [name[1]['style_block'] for name in config.agents.items()]
    [start_with_list.append('<pre') for i in style_block if i]

    # Todo Compatible with whitelist/blacklist parameter, to be removed
    allow_list = agent[1].get('allow_list') if agent[1].get('allow_list') is not None else agent[1].get('whitelist')
    deny_list = agent[1]['deny_list'] if agent[1].get('deny_list') is not None else agent[1].get('blacklist')
    min_content_length = agent[1].get('min_content_length', 0)  # Default value is 0, means no filtering

    # filter, if not content starts with start flag
    if not entry['content'].startswith(tuple(start_with_list)):
        
        # Check content length filtering
        if min_content_length > 0:
            # Convert HTML to plain text and remove extra whitespace
            content_text = md(entry['content']).strip()
            # Remove extra newlines and whitespace characters
            content_text = re.sub(r'\s+', ' ', content_text)
            if len(content_text) < min_content_length:
                logger.info(f"Filtered entry due to insufficient content length: '{entry['title']}' "
                           f"(length: {len(content_text)}, required: {min_content_length}) "
                           f"from {entry['feed']['title']}")
                return False

        # filter, if in allow_list
        if allow_list is not None:
            if any(fnmatch.fnmatch(entry['feed']['site_url'], pattern) for pattern in allow_list):
                return True

        # filter, if not in deny_list
        elif deny_list is not None:
            if any(fnmatch.fnmatch(entry['feed']['site_url'], pattern) for pattern in deny_list):
                return False
            else:
                return True

        # filter, if allow_list and deny_list are both None
        elif allow_list is None and deny_list is None:
            return True

    return False
