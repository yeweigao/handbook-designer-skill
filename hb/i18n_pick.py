"""多语言写法 {zh: …, en: …} 的取值（lint / lock / images / facts 这些检查脚本共用）。"""
LANGS_ALL = {'zh', 'zh-hans', 'zh-hant', 'zh-tw', 'zh-hk', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'it', 'pt', 'ru', 'th', 'vi', 'ms', 'ar'}
def is_multi(o): return isinstance(o, dict) and len(o) > 0 and all(str(k).lower() in LANGS_ALL for k in o)
def pick(o, lang):
    if is_multi(o):
        v = next((v for k, v in o.items() if str(k).lower() == lang.lower()), next(iter(o.values())))
        return pick(v, lang)
    if isinstance(o, dict): return {k: pick(v, lang) for k, v in o.items()}
    if isinstance(o, list): return [pick(v, lang) for v in o]
    return o
def langs(spec):
    b = (spec or {}).get('book') or {}
    return [str(x) for x in (b.get('langs') or [b.get('lang', 'zh')])]
def first_lang(spec, lang=None):
    return pick(spec, lang or langs(spec)[0])
