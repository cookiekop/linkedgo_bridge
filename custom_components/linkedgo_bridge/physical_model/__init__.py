"""Physical mode for transfer xlink data points to homeassistant fields."""

from .ST2000 import ST2000
from .ST830 import ST830
from .ST1800_HN import ST1800_HN


XLINK_PHYSICAL_MODEL = {
    "160898c835f003e9160898c835f0d601": ST2000,
    "160042bed58403e9160042bed5842801": ST830,
    "1603bec1cd5903e91603bec1cd599801": ST1800_HN,
}
