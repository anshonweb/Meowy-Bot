from saucenao_api import SauceNao
results = SauceNao('5fae52160f484ac5727ad10410490282c0c4338d').from_url('https://i.imgur.com/oZjCxGo.jpg')

len(results)   # 6
bool(results)  # True

# Request limits
results.short_remaining  # 4  (per 30 seconds limit)
results.long_remaining   # 99 (per day limit)

print(results[0].thumbnail)     # temporary URL for picture preview
print(results[0].similarity)    # 93.3
print(results[0].title )        # めぐみん
print(results[0].urls) # ['https://www.pixiv.net/member_illust.php?mode=medium&illust_id=77630170']
print(results[0].author)        # frgs
print(results[0].raw)           # raw result


