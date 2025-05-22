import re, string
from wikipedia import WikipediaPage
import wikipedia
from bs4 import BeautifulSoup
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from match import match
from typing import List, Callable, Tuple, Any, Match


def get_page_html(title: str) -> str:
    """Gets html of a wikipedia page

    Args:
        title - title of the page

    Returns:
        html of the page
    """
    results = wikipedia.search(title)
    return WikipediaPage(results[0]).html()


def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)

    Args:
        html - the full html of the page

    Returns:
        html of just the first infobox
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text


def clean_text(text: str) -> str:
    """Cleans given text removing non-ASCII characters and duplicate spaces & newlines

    Args:
        text - text to clean

    Returns:
        cleaned text
    """
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> Match:
    """Finds regex matches for a pattern

    Args:
        text - text to search within
        pattern - pattern to attempt to find within text
        error_text - text to display if pattern fails to match

    Returns:
        text that matches
    """
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)

    if not match:
        raise AttributeError(error_text)
    return match


def get_president_name(country_name: str) -> str:
    """Gets the name of the president of the given country

    Args:
        country_name - name of the country to get president of

    Returns:
        name of the president of the given country
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:President)(?:.*?)(?P<president>[\w\s]+)(?:.*?)"
    error_text = "Page infobox has no president information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("president")


def get_president_term(country_name: str) -> str:
    """Gets the term length of the president of a given country

    Args:
        country_name - name of the country

    Returns:
        term length of the president
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Term\s*of\s*office\s*).*?(\d{4}-\d{4})"
    error_text = "Page infobox has no term information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group(1)


def get_president_party(country_name: str) -> str:
    """Gets the political party of the president of a given country

    Args:
        country_name - name of the country

    Returns:
        political party of the president
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Political\s*party\s*).*?([\w\s]+)"
    error_text = "Page infobox has no political party information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group(1)


def get_president_birth(country_name: str) -> str:
    """Gets the birthdate of the president of the given country

    Args:
        country_name - name of the country

    Returns:
        birthdate of the president
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Born\D*)(?P<birth>\d{4}-\d{2}-\d{2})"
    error_text = "Page infobox has no birth information (at least none in xxxx-xx-xx format)"
    match = get_match(infobox_text, pattern, error_text)

    return match.group("birth")


def get_president_predecessor(country_name: str) -> str:
    """Gets the predecessor of the president of the given country

    Args:
        country_name - name of the country

    Returns:
        predecessor of the president
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Predecessor\s*).*?([\w\s]+)"
    error_text = "Page infobox has no predecessor information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group(1)


def get_president_successor(country_name: str) -> str:
    """Gets the successor of the president of the given country

    Args:
        country_name - name of the country

    Returns:
        successor of the president
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Successor\s*).*?([\w\s]+)"
    error_text = "Page infobox has no successor information"
    match = get_match(infobox_text, pattern, error_text)

    return match.group(1)


# Define the actions based on specific queries
def president_name(matches: List[str]) -> List[str]:
    return [get_president_name(matches[0])]


def president_term(matches: List[str]) -> List[str]:
    return [get_president_term(matches[0])]


def president_party(matches: List[str]) -> List[str]:
    return [get_president_party(matches[0])]


def president_birth(matches: List[str]) -> List[str]:
    return [get_president_birth(matches[0])]


def president_predecessor(matches: List[str]) -> List[str]:
    return [get_president_predecessor(matches[0])]


def president_successor(matches: List[str]) -> List[str]:
    return [get_president_successor(matches[0])]


# Define the pattern-action list for the query system
pa_list: List[Tuple[List[str]]] = [
    ("who is the president of %".split(), president_name),
    ("what is the term of the president of %".split(), president_term),
    ("what is the political party of the president of %".split(), president_party),
    ("when was the president of % born".split(), president_birth),
    ("who was the predecessor of the president of %".split(), president_predecessor),
    ("who is the successor of the president of %".split(), president_successor),
]


def search_pa_list(src: List[str]) -> List[str]:
    """Takes source, finds matching pattern and calls corresponding action."""
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]

    return ["I don't understand"]


def query_loop() -> None:
    """The query loop to interact with the user."""
    print("Welcome to the President Info Bot!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nGoodbye!\n")
query_loop()