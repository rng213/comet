from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytz
from dotenv import load_dotenv

if TYPE_CHECKING:
    from pytz import _UTCclass
    from pytz.tzinfo import DstTzInfo, StaticTzInfo

# Note: TIMEZONE environment variable is loaded in this dedicated module
# rather than in env.py file because:
#
# 1. It requires a transformation from string to a pytz timezone object
# 2. It needs specific type handling with pytz types that aren't needed elsewhere
# 3. This centralizes all timezone-specific logic in one place
# 4. The returned object is a complex timezone object, not a simple value

load_dotenv()
_tz: str = os.environ["TIMEZONE"]
TIMEZONE: _UTCclass | DstTzInfo | StaticTzInfo = pytz.timezone(_tz)
