import importlib
import logging

import cv2
import numpy as np
import uiautomator2 as u2

logger = logging.getLogger(__name__)

package_dir = importlib.resources.files("phone_automation")


def load_image(img_path):
    img_cv = cv2.imread(img_path)
    if img_cv is None:
        logger.error(f"错误: 无法加载图片: {img_path}")
        raise ValueError(f"无法加载图片: {img_path}")
    return img_cv


def screenshot(d: u2.Device) -> np.ndarray:
    img_screen = d.screenshot()  # 获取 uiautomator2 的 Image 对象
    screen_array = np.array(img_screen)  # 转换为np.array对象
    screen_cv = cv2.cvtColor(screen_array, cv2.COLOR_RGB2BGR)  # 转换为cv2能识别的BGR格式
    return screen_cv


def find_match_image_position(screen_cv: np.ndarray, template_cv: np.ndarray, threshold=0.8, no_find_raise=True):
    """
    在当前屏幕截图上匹配指定图片，如果匹配成功则返回匹配位置的中心坐标。

    Args:
        img_screen: 当前屏幕截图.
        img_cv: 要匹配的图片.
        threshold: 匹配阈值，值越大匹配要求越高.
    """

    # 1. 获取目标图片的宽高
    target_height, target_width, _ = template_cv.shape

    # 2. 使用模板匹配查找目标图片
    result = cv2.matchTemplate(screen_cv, template_cv, cv2.TM_CCOEFF_NORMED)

    # 3. 获取匹配结果中匹配度超过阈值的位置
    locations = np.where(result >= threshold)

    # 4. 如果找到匹配位置
    if locations[0].size > 0:
        # 遍历所有匹配位置，并获取第一个匹配结果的中心点进行点击
        for pt in zip(*locations[::-1]):
            # 计算中心点坐标
            center_x = pt[0] + target_width // 2
            center_y = pt[1] + target_height // 2

            logger.debug(f"找到匹配图片，点击位置: ({center_x}, {center_y})")

            center_x = int(center_x)
            center_y = int(center_y)

            return center_x, center_y  # 只点击第一个匹配的

    if no_find_raise:
        logger.error("未找到匹配图片")
        raise ValueError("未找到匹配图片")
    else:
        logger.warning("未找到匹配图片")
        return None, None
