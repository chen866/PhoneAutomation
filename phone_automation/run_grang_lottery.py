import logging
import random
import time

import uiautomator2 as u2

from phone_automation.common import find_match_image_position, load_image, package_dir, screenshot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def find_and_click(
    d, image_path, wait=1, retry=3, retry_interval=1, no_find_raise=True, offset: tuple[int, int] = None
):
    if offset is not None:
        offset_x, offset_y = offset
    else:
        offset_x, offset_y = 0, 0

    if wait > 0:
        time.sleep(wait)

    for i in range(retry + 1):
        screen_cv = screenshot(d)
        template_cv = load_image(image_path)
        position = find_match_image_position(screen_cv, template_cv, no_find_raise=False)
        if position[0] is not None:
            logger.debug(f"匹配到的位置: {position}, 图片: {image_path}")
            x, y = position
            if offset_x != 0 or offset_y != 0:
                x += offset_x
                y += offset_y
                logger.debug(f"偏移后的位置: {x}, {y}")
            d.click(x, y)
            return True
        time.sleep(retry_interval)
    else:
        if no_find_raise:
            raise ValueError(f"未找到匹配图片: {image_path}")
        else:
            logger.warning(f"未找到匹配图片: {image_path}")
            return False


class GrangLottery:
    def __init__(self, d):
        self.d = d
        self.imgs = {}

    def update_screen_cv(self):
        self.screen_cv = screenshot(self.d)

    def load_img(self, image_key):
        if image_key not in self.imgs:
            img_path = package_dir / "static" / "img" / f"{image_key}.png"
            self.imgs[image_key] = load_image(img_path)
        return self.imgs[image_key]

    def find_and_click(
        self, image_key, wait=1, retry=3, retry_interval=1, no_find_raise=True, offset: tuple[int, int] = None
    ):
        d = self.d
        template_cv = self.load_img(image_key)

        if offset is not None:
            offset_x, offset_y = offset
        else:
            offset_x, offset_y = 0, 0

        if wait > 0:
            time.sleep(wait)

        for i in range(retry + 1):
            self.update_screen_cv()

            position = find_match_image_position(self.screen_cv, template_cv, no_find_raise=False)
            if position[0] is not None:
                logger.debug(f"匹配到的位置: {position}, 图片: {image_key}")
                x, y = position
                if offset_x != 0 or offset_y != 0:
                    x += offset_x
                    y += offset_y
                    logger.debug(f"偏移后的位置: {x}, {y}")
                d.click(x, y)
                return True
            time.sleep(retry_interval)
        else:
            if no_find_raise:
                raise ValueError(f"未找到匹配图片: {image_key}")
            else:
                logger.warning(f"未找到匹配图片: {image_key}")
                return False

    def swipe(
        self,
        start_position: tuple[int, int],
        relative_distance: tuple[int, int],
        random_range: tuple[int, int] = (0, 0),
        duration: float = 0.1,
    ):
        _start_position = (
            start_position[0] + random.randint(-random_range[0], random_range[0]),
            start_position[1] + random.randint(-random_range[1], random_range[1]),
        )
        end_position = (
            start_position[0] + relative_distance[0] + random.randint(-random_range[0], random_range[0]),
            start_position[1] + relative_distance[1] + random.randint(-random_range[1], random_range[1]),
        )
        self.d.swipe(*_start_position, *end_position, duration=duration)

    def swipe_down(
        self,
        start_position: tuple[int, int],
        distance: int = 500,
        random_range: tuple[int, int] = (0, 0),
        duration: float = 0.1,
    ):
        self.swipe(start_position, (0, -distance), random_range, duration)

    def run_go_to_lottery(self):
        # 首页 -> 庄园
        logger.info("开始 首页 -> 庄园")
        self.find_and_click("grang_text", no_find_raise=False, wait=1, retry=1)
        # 活动消息
        if self.find_and_click("grang_lottery_close", no_find_raise=False, retry=0, wait=3):
            logger.info("关闭 活动消息")
        # 庄园 -> 房间
        logger.info("开始 庄园 -> 房间")
        self.find_and_click("grang_lottery_thumbnail", no_find_raise=False, wait=4, retry=1)
        # 房间 -> 抽奖
        logger.info("开始 房间 -> 抽奖")
        self.find_and_click("grang_lottery_thumbnail_in_room", no_find_raise=False, wait=3, retry=1)

    def run_collect_task1(self):
        # 抽奖 - 任务饲料兑换
        for i in range(2):
            logger.info(f"开始第{i + 1}次 任务 饲料兑换")
            ok = self.find_and_click("grang_lottery_task1", offset=(750, 0), no_find_raise=False, wait=2, retry=0)
            if not ok:
                logger.error("没有找到 任务 饲料兑换")
                break
            ok = self.find_and_click("grang_lottery_task1_btn", no_find_raise=False, wait=1, retry=0)
            if not ok:
                logger.error("没有找到 任务 饲料兑换 - 确认兑换 按钮")
                break

    def run_collect_entries(self, count: int = 3):
        # 抽奖 - 领取次数
        for i in range(count):
            logger.info(f"开始第{i + 1}/{count}次 领取次数")
            ok = self.find_and_click("grang_lottery_entries_collect", retry=0, no_find_raise=False)
            if ok:
                logger.info("领取次数成功")
            else:
                logger.error("没有领奖次数")
                break

    def run_collect_task2(self):
        # 抽奖 - 任务杂货铺
        for i in range(3):
            logger.info(f"开始第{i + 1}次 任务 杂货铺")
            ok = self.find_and_click("grang_lottery_task2", offset=(750, 0), no_find_raise=False, wait=3, retry=2)
            if not ok:
                logger.error("没有找到 任务 杂货铺")
                break
            job_ok = True
            for j in range(6):
                time.sleep(2)
                # 向下滑动
                self.swipe_down((700, 1200), 100, (40, 40), 0.1)
                time.sleep(1)
                # 检查
                if j == 1:
                    ok = self.find_and_click("grang_lottery_task2_flag1", no_find_raise=False, wait=0, retry=0)
                    if not ok:
                        logger.info("任务 杂货铺 不在任务中, 直接停止本次任务")
                        job_ok = False
                        break
            # 未检查到任务, 直接停止本次任务
            if not job_ok:
                continue
            # 返回
            if ok := self.find_and_click("grang_lottery_task2_flag2", no_find_raise=False, wait=2, retry=1):
                logger.info("任务 杂货铺 结束, 返回")
                self.d.press("BACK")
            else:
                logger.warning("没有找到 任务 杂货铺 结束标志 grang_lottery_task2_flag2, 不执行【返回】")
            # 领取奖励
            ok = self.find_and_click("grang_lottery_entries_collect", wait=2, retry=1, no_find_raise=False)
            if ok:
                logger.info("领取次数成功")
            else:
                logger.error("没有领奖次数")
                break

    def run_lottery(self):
        # 抽奖 - 抽奖
        while True:
            ok = self.find_and_click("grang_lottery_collect", no_find_raise=False, offset=(-100, 30), retry=0, wait=0.5)
            if not ok:
                logger.error("没有找到 抽奖 次数")
                break
            # 抽奖 - 关闭结果
            ok = self.find_and_click("grang_lottery_close", no_find_raise=False, retry=0, wait=2)
            if not ok:
                logger.error("没有找到 抽奖 关闭结果")
                break

    def run(self):
        self.run_go_to_lottery()
        # task 2
        self.swipe_down((700, 1200), 500, (40, 40), 0.1)
        self.run_collect_entries()
        self.run_collect_task2()
        # task 1
        self.swipe_down((700, 1200), 500, (40, 40), 0.1)
        self.run_collect_entries()
        self.run_collect_task1()
        self.run_collect_entries()
        self.run_lottery()


if __name__ == "__main__":
    d = u2.connect()
    grang_lottery = GrangLottery(d)
    grang_lottery.run()
