import requests
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Image

def synthesize_emojis(emoji_one: str, emoji_two: str):
    """
    调用 OIAPI 的 Emoji 合成接口（EmojiMix）。
    文档参见：https://oiapi.net/22.html
    """
    url = "https://oiapi.net/API/EmojiMix"
    params = {
        "emoji1": emoji_one,
        "emoji2": emoji_two,
        "0": emoji_one,
        "1": emoji_two
    }
    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[synthesize_emojis] 请求或解析出错：{e}")
        return None

@register("emoji_merge", "monbed", "Emoji 合成插件", "1.1.0")
class EmojiPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("合成")
    async def merge(self, event: AstrMessageEvent, emoji1: str, emoji2: str):
        result = synthesize_emojis(emoji1, emoji2)
        if not result:
            yield event.chain_result([Plain("服务不可用，请稍后再试😢")])
            return

        # OIAPI 返回 code==1 表示成功
        if result.get("code") == 1:
            # 优先从 data.url，其次从 message 中取 URL
            image_url = result.get("data", {}).get("url") or result.get("message")
            if image_url:
                try:
                    yield event.chain_result([Image(file=image_url)])
                except Exception as e:
                    print(f"[merge] 发送图片时出错：{e}")
                    yield event.chain_result([Plain(f"发送合成图片失败😢：{e}")])
                return

        # 失败则返回 message 内容
        err = result.get("message", "合成失败")
        yield event.chain_result([Plain(f"合成失败😢：{err}")])

    async def terminate(self):
        pass
