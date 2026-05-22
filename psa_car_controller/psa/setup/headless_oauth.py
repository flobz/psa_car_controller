import logging
import os
import time
from urllib.parse import urlparse, parse_qs
from playwright import sync_api as playwright_sync
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

# Selectors used by the Gigya login form
EMAIL_SELECTOR = '#gigya-login-form input[name="username"]'
PASSWORD_SELECTOR = '#gigya-login-form input[name="password"]'  # nosec dodgy: password
SUBMIT_SELECTOR = '#gigya-login-form input[type="submit"]'
REMEMBER_ME_SELECTOR = 'label[for="gigya-checkbox-remember"]'

# ForgeRock AM consent page selectors
AUTHORIZE_SELECTORS = [
    'input[name="decision"][value="allow"]',
    'button[name="decision"][value="allow"]',
    '#allow',
    'input[name="allow"]',
    'button[name="allow"]',
    'input[type="submit"][value="Allow"]',
    'input[type="submit"][value="Erlauben"]',
    'input[type="submit"][value="Autoriser"]',
    '#cvs_from input[type="submit"]',
]

TIMEOUT_MS = 60_000


class HeadlessOAuthError(Exception):
    """Exception raised when headless OAuth fails, carrying debug info."""

    def __init__(self, message, url, html, logs):
        super().__init__(message)
        self.url = url
        self.html = html
        self.logs = logs


class PlaywrightNotInstalled(Exception):
    """Exception raised when Playwright is not installed."""


class FormException(Exception):
    """Exception raised when form submit fails."""


def _fill_credentials(page: Page, email, password):
    """Wait for and fill the login form if visible."""
    try:
        page.wait_for_selector(EMAIL_SELECTOR, timeout=30_000)
    except Exception:  # pylint: disable=broad-except
        pass

    if page.is_visible(EMAIL_SELECTOR):
        logger.info("Filling credentials")
        # Use type instead of fill to be more human-like and avoid some bot detection
        page.click(EMAIL_SELECTOR)
        page.type(EMAIL_SELECTOR, email, delay=50)
        page.click(PASSWORD_SELECTOR)
        page.type(PASSWORD_SELECTOR, password, delay=50)

        try:
            page.click(REMEMBER_ME_SELECTOR)
        except playwright_sync.TimeoutError:
            logger.warning("Remember me checkbox not found")
        submit_button = page.locator(SUBMIT_SELECTOR)
        submit_button.click()
        submit_button.wait_for(state="detached", timeout=10_000)
    else:
        logger.info(
            "Login form not visible, checking if already authenticated or on error page")


def check_for_error(page):
    if errors := page.locator('div.gigya-error-msg.gigya-form-error-msg.gigya-error-msg-active').all_inner_texts():
        raise FormException(f"Authentication failed: {errors}")


def get_code(page: Page, scheme: str) -> str:
    """get the OAuth code in the URL or consent page."""
    code = [None]

    def find_code_in_url(url):
        logger.info("Checking for oauth2 code in %s", url)
        if url.startswith(scheme + "://") and (code_found := parse_qs(urlparse(url).query).get("code", [None])[0]):
            code[0] = code_found
    page.on('request', lambda req: find_code_in_url(req.url))
    deadline = time.time() + 30
    while time.time() < deadline:
        for selector in AUTHORIZE_SELECTORS:
            if page.is_visible(selector):
                logger.info("Clicking authorization consent: %s", selector)
                page.click(selector)
                break
            time.sleep(1)
            if code[0]:
                return code[0]

    raise RuntimeError("Can't find oauth2 code")


def get_oauth_code_headless(auth_url: str, email: str, password: str,
                            scheme: str) -> str:
    """Automate PSA/Stellantis OAuth login using a native Playwright WebKit browser."""

    console_logs = []

    def on_console(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")

    if not playwright_sync:
        raise PlaywrightNotInstalled("Playwright is not installed, run 'pip install playwright'")

    with playwright_sync.sync_playwright() as p:
        # Launch native browser (prefer webkit fallback to chromium)
        browser = None
        for browser_type in [p.webkit, p.chromium]:
            try:
                logger.info("Launching headless %s", browser_type.name)
                browser = browser_type.launch(
                    headless=os.environ.get("NO_HEADLESS") is None)
                break
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Failed to launch %s: %s", browser_type.name, exc)

        if not browser:
            raise PlaywrightNotInstalled("Could not launch any Playwright browser. "
                                         "Please run 'playwright install --with-deps webkit'")

        context = browser.new_context()
        try:
            page = context.new_page()
            page.on("console", on_console)
            page.goto(auth_url, wait_until="networkidle", timeout=TIMEOUT_MS)
            _fill_credentials(page, email, password)
            return get_code(page, scheme)
        except (playwright_sync.TimeoutError, RuntimeError) as e:
            logger.exception("Headless OAuth failed: %s", e)
            check_for_error(page)
            raise HeadlessOAuthError(
                "Headless OAuth failed: could not capture authorization code.",
                url=page.url, html=page.content(), logs=console_logs
            ) from e
        finally:
            browser.close()
