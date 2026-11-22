"""支持 ``python -m animalclassification`` 运行方式。"""
from __future__ import annotations

import sys

from animalclassification.cli import main

if __name__ == "__main__":
    sys.exit(main())
