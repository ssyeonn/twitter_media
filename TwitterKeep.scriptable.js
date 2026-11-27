// Run in Scriptable from an Apple shortcut. The shortcut saves the returned URLs.
const endpoint = "https://api.fxtwitter.com/2/status/";
const postPattern = /https:\/\/(?:(?:www|mobile|m)\.)?(?:x|twitter)\.com\/(?:i\/web|[a-z0-9_]{1,15})\/status\/([0-9]{1,20})(?![a-z0-9_])/i;
const photoPattern = /^https:\/\/pbs\.twimg\.com\/media\/[^\s]+$/i;
const mp4Pattern = /^https:\/\/video\.twimg\.com\/[^?\s#]+\.mp4(?:\?[^\s#]*)?$/i;

const input = Array.isArray(args.shortcutParameter)
  ? args.shortcutParameter.join("\n")
  : String(args.shortcutParameter ?? "");
const post = input.match(postPattern);
if (!post) {
  throw new Error("공개 트위터 게시물 링크를 공유해 주세요.");
}

const request = new Request(endpoint + post[1]);
request.timeoutInterval = 20;
let result;
try {
  result = await request.loadJSON();
} catch {
  throw new Error("다운로드 서버에 연결할 수 없어요. 잠시 후 다시 시도해 주세요.");
}

if (request.response.statusCode !== 200 || result?.code !== 200) {
  throw new Error("게시물을 불러올 수 없어요. 공개 게시물인지 확인해 주세요.");
}

const items = result.status?.media?.all ?? [];
const urls = [];
for (const item of items) {
  if (item.type === "photo") {
    if (photoPattern.test(item.url)) urls.push(item.url);
    continue;
  }

  const url = mp4Pattern.test(item.url)
    ? item.url
    : (item.formats ?? []).find(format => mp4Pattern.test(format.url))?.url;
  if (url) urls.push(url);
}

if (urls.length === 0) {
  throw new Error("저장할 사진이나 MP4 영상을 찾지 못했어요.");
}

Script.setShortcutOutput(urls);
Script.complete();
