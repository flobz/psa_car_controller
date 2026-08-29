import base64
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
try:
    from playwright import sync_api as playwright_sync
    from playwright.sync_api import Page
except ImportError:
    playwright_sync = None
    Page = None

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

    def __init__(self, message, url, html, logs, screenshot=None):  # pylint: disable=R0913,R0917
        super().__init__(message)
        self.url = url
        self.html = html
        self.logs = logs
        self.screenshot = screenshot


class PlaywrightNotInstalled(Exception):
    """Exception raised when Playwright is not installed."""


class FormException(Exception):
    """Exception raised when form submit fails."""


def _fill_credentials(page: Page, email, password):
    """Fill the login form. Assumes the form is already visible."""
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


def check_for_error(page):
    if errors := page.locator('div.gigya-error-msg.gigya-form-error-msg.gigya-error-msg-active').all_inner_texts():
        raise FormException(f"Authentication failed: {errors}")


def get_code(page: Page, scheme: str, email: str, password: str) -> str:
    """Wait for the OAuth code, handling login and consent pages as they appear.

    The Stellantis OAuth flow is driven by the Gigya JS SDK, which initializes
    asynchronously after the page loads. ``wait_until="networkidle"`` is
    unreliable here because the SDK has natural pauses that can be mistaken
    for network idle, causing ``goto`` to return before the login form is
    rendered. Instead, this loop polls for one of three outcomes:
    the login form (fill it and submit), a consent button (click it), or the
    OAuth code in a redirected URL (return it).
    """
    code = [None]

    def find_code_in_url(url):
        if url.startswith(scheme + "://") and (code_found := parse_qs(urlparse(url).query).get("code", [None])[0]):
            code[0] = code_found
    page.on('request', lambda req: find_code_in_url(req.url))

    deadline = time.time() + 90
    credentials_filled = False
    while time.time() < deadline:
        if code[0]:
            return code[0]

        if not credentials_filled and page.is_visible(EMAIL_SELECTOR):
            _fill_credentials(page, email, password)
            credentials_filled = True
            continue

        for selector in AUTHORIZE_SELECTORS:
            if page.is_visible(selector):
                logger.info("Clicking authorization consent: %s", selector)
                page.click(selector)
                break

        time.sleep(1)

    raise RuntimeError("Can't find oauth2 code")


def _launch_browser(p):
    """Launch a Playwright chromium browser."""
    headless = len(os.environ.get("NO_HEADLESS", "")) == 0
    try:
        logger.info("Launching headless chromium")
        return p.chromium.launch(headless=headless), headless
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Failed to launch chromium", exc_info=exc)
    raise PlaywrightNotInstalled("Could not launch chromium. "
                                 "Please run 'playwright install --with-deps chromium'")


def _run_headless_oauth(auth_url: str, email: str, password: str,  # pylint: disable=too-many-locals
                        scheme: str) -> str:
    """Run the Playwright sync flow. Must not be called inside a running event loop."""
    console_logs = []

    def on_console(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")

    def on_response(response):
        logger.debug("Response: %s %s", response.status, response.url)
        console_logs.append(f"[response] {response.status} {response.url}")

    if not playwright_sync:
        raise PlaywrightNotInstalled("Playwright is not installed, run 'pip install playwright'")

    with playwright_sync.sync_playwright() as p:
        browser, headless = _launch_browser(p)
        context = browser.new_context()
        pages = []

        def on_popup(popup):
            pages.append(popup)

        try:
            page = context.new_page()
            page.on("console", on_console)
            page.on("response", on_response)
            page.on("popup", on_popup)
            page.goto(auth_url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            return get_code(page, scheme, email, password)
        except (playwright_sync.TimeoutError, RuntimeError, FormException) as e:
            logger.exception("Headless OAuth failed: %s", e)
            screenshot_b64 = None
            screenshot_page = pages[-1] if pages else page
            try:
                screenshot_bytes = screenshot_page.screenshot(timeout=0, animations="disabled")
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("ascii")
            except Exception as exc:  # pylint: disable=broad-except
                logger.debug("Could not capture screenshot: %s", exc)
            try:
                check_for_error(page)
            except Exception:  # pylint: disable=broad-except
                logger.debug("Could not check for form errors", exc_info=True)
            raise HeadlessOAuthError(
                "Headless OAuth failed: could not capture authorization code.",
                url=page.url, html=page.content(), logs=console_logs,
                screenshot=screenshot_b64
            ) from e
        finally:
            if headless:
                browser.close()


def get_oauth_code_headless(auth_url: str, email: str, password: str,
                            scheme: str) -> str:
    """Automate PSA/Stellantis OAuth login using a headless Playwright chromium browser.

    Playwright's sync API cannot run inside a running asyncio event loop (e.g. a
    Dash callback). When that is the case, dispatch the work to a dedicated thread
    that has no event loop.
    """
    try:
        import asyncio  # pylint: disable=import-outside-toplevel
        asyncio.get_running_loop()
    except (RuntimeError, ImportError):
        # No running loop: safe to call the sync API directly.
        return _run_headless_oauth(auth_url, email, password, scheme)

    # A loop is running (e.g. inside a Dash callback). Run the sync Playwright
    # flow in a separate thread with no event loop to avoid the
    # "Sync API inside the asyncio loop" error.
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_run_headless_oauth, auth_url, email, password, scheme)
        return future.result()
