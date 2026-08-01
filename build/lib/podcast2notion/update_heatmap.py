import os

from podcast2notion.utils import get_embed
from podcast2notion.notion_helper import NotionHelper


HEATMAP_GUIDE = (
    "https://mp.weixin.qq.com/s?__biz=MzI1OTcxOTI4NA==&mid=2247484145&idx=1"
    "&sn=81752852420b9153fc292b7873217651"
    "&chksm=ea75ebeadd0262fc65df100370d3f983ba2e52e2fcde2deb1ed49343fbb10645a77570656728"
)


def get_file():
    """获取 OUT_FOLDER 中最新生成的 svg 文件（按修改时间倒序）"""
    folder_path = "./OUT_FOLDER"
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        entries = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(".svg")
        ]
        if not entries:
            return None
        # 取最新修改的 svg（workflow 会把 notion.svg 改名成 uuid.svg，旧的会留下）
        entries.sort(
            key=lambda f: os.path.getmtime(os.path.join(folder_path, f)),
            reverse=True,
        )
        return entries[0]
    else:
        print("OUT_FOLDER does not exist.")
        return None


notion_helper = NotionHelper()


def main():
    image_file = get_file()
    repo = os.getenv("REPOSITORY")
    ref = os.getenv("REF", "").split("/")[-1] if os.getenv("REF") else ""
    if image_file and repo and ref:
        # 直接用 GitHub raw URL，不再走 heatmap.malinkang.com 第三方代理
        image_url = f"https://raw.githubusercontent.com/{repo}/{ref}/OUT_FOLDER/{image_file}"
        if notion_helper.heatmap_block_id:
            notion_helper.update_heatmap(
                block_id=notion_helper.heatmap_block_id, url=image_url
            )
            print(f"热力图已更新: {notion_helper.heatmap_block_id}")
        else:
            print(
                f"未找到现有热力图 block（type=embed 且 URL 以 https://heatmap.malinkang.com/ 开头）。\n"
                f"请在你的 Notion 主页（NOTION_PAGE）手动添加一个 image 或 embed block，"
                f"下次 workflow 跑就能找到并更新。\n参考教程: {HEATMAP_GUIDE}"
            )
    else:
        print(
            f"更新热力图失败：缺少 image 文件、REPOSITORY 或 REF 环境变量。\n"
            f"参考教程: {HEATMAP_GUIDE}"
        )


if __name__ == "__main__":
    main()
