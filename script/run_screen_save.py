from datetime import datetime

import uiautomator2 as u2

from phone_automation.common import package_dir

d = u2.connect()

# 保存到图片文件夹
img_dir = package_dir / "static" / "img" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
d.screenshot(img_dir)
